from typing import Any, Callable, Dict, List, Tuple, Union

import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator
from sklearn.metrics import mean_squared_error
import xgboost as xgb
from hierarchicalforecast.core import HierarchicalReconciliation
from hierarchicalforecast.methods import BottomUp, MinTrace, TopDown
from prophet import Prophet
from typing_extensions import Self

from ..datapreparation.model_preproc import PreprocessBoosting
from ..analytics.evaluationMetrics import EvaluateModel
from ..utility.check_utils import check_not_in_iterable, check_not_isinstance
from ..utility.resources import (
    get_configuration,
    get_module_and_function,
    logger
)
from .utils import create_zero_dataframe, grid_values_hyperparameters, model_tuning, to_category



class ProphetModel():
    def __init__(self, params: Dict[str, Union[Dict[str, Union[int, float, str]], List[str]]], config_path: str, max_na_ratio: float = 0.5):
        """
        Initlization parameters for ProphetModel.

        Parameters
        ----------
        params : Dict[str, Union[Dict[str, Union[int, float, str]], List[str]]]
            The dictionary of hyperparameters from the config file
        config_path : str
            The path to the check configuration files (e.g. config/config_check)
        max_na_ratio : float, optional
            Maximum ratio of NaNs and not null permitted in order to fit the model, by default 0.5
        """
        self.config_path = config_path
        self.max_na_ratio = max_na_ratio
        params.update({'interval_width':['0.95']}) # Update params with the 95% CI since default is 80%

        self.make_grid_params(params)


    def fit(self, X_train: pd.DataFrame, X_val: pd.DataFrame) -> Self:
        """
        Fits the models using a Train and Validations Set. 
        The function sets the Dictionary of Best Parameters and Dictionary of Fitted models which use the respective Best Params.

        Parameters
        ----------
        X_train : pd.DataFrame
            Dataframe for training
        X_val : pd.DataFrame
            Dataframe for validation

        Returns
        -------
        Self

        Raises
        ------
        Exception
            If No models have been trained (Dict of fitted models with all Nones)
        """

        logger.info(message=f"START Fitting Model.")

        count = 0
        total_runs = X_train.index.nunique()

        self.models_dict = {}
        self.models_best_params = {}

        for id_pred, df_train in X_train.groupby('unique_id'):
            self.models_dict[id_pred] = None
            self.models_best_params[id_pred] = {}

            logger.info(message=f"Training {id_pred}")

            if (df_train['y'] > 0).sum() / len(df_train) < self.max_na_ratio:
                logger.info(message=f"The train set for time series {id_pred} has more than {self.max_na_ratio*100}% null values, skipping it.")
                count += 1
                logger.info(message=f"Remaining number of iteration - {total_runs-count}")
                continue
            try:
                evaluator = EvaluateModel(date_true='ds', date_pred='ds', y_true='y', y_pred='yhat', upper_95='yhat_upper', lower_95='yhat_lower')
                # Tune if we have a non-empty validation set
                df_val = X_val[X_val.index==id_pred]
                
                # Find best params
                logger.info(message="Grid Searching Best Parameters.")
                best_params = model_tuning(model=Prophet, evaluator=evaluator, unique_id=id_pred, grid_params=self.grid_params, 
                                           train_df=df_train, validation_df=df_val,
                                           decision_function = 'rmse*0.5 + mae*0.5')

                logger.info(message=f"Best Parameters found: {best_params}")

                model = Prophet(**best_params)
                
                # Retrain on train and val data with best parameters
                logger.info(message=f"Fitting Prophet model using the Best Parameters")
                model.fit(pd.concat([df_train, df_val]))

                self.models_best_params[id_pred] = best_params
                self.models_dict[id_pred] = model
                
            except ValueError as e:
                logger.info(message=f"Skipping training {id_pred}, due to: {e}")
                count += 1
                logger.info(message=f"Remaining number of iteration - {total_runs-count}")
                continue

            count += 1
            logger.info(message=f"Remaining number of iteration - {total_runs-count}")
        
        logger.info(message=f"DONE Fitting Model.")

        # Check consinstency of models_dict
        count = 0
        breaker = len(self.models_dict.keys())
        for m in self.models_dict.values():
            if m != None:
                break
            else:
                count+=1

        if count == breaker:
            raise Exception('No models have been trained, check logs for insights on the reasoning.')

        return self


    def refit(self, X: pd.DataFrame) -> Self:
        """
        Refit the models with the best parameters on new data

        Parameters
        ----------
        X : pd.DataFrame
            Dataframe to fit the data

        Returns
        -------
        Self
        """

        logger.info(message=f"START Re-Fitting Model.")
        total_runs = X.index.nunique()

        count = 0
        for id_pred, df in X.groupby('unique_id'):
            logger.info(message=f"Training {id_pred}")

            # If the models exists and have been trained, execute the retrain on the whole dataset
            if isinstance(self.models_dict[id_pred], ProphetModel):
                model = Prophet(**self.models_best_params[id_pred])
                # Retrain on train and val data with best parameters
                model.fit(df)

                self.models_dict[id_pred] = model

            count += 1
            logger.info(message=f"Remaining number of iteration - {total_runs-count}")

        logger.info(message=f"DONE Re-Fitting Model.")
   

    def predict(self, X: pd.DataFrame) -> pd.DataFrame:
        """
        Makes predictions over an input Dataframe using the fitted Models

        Parameters
        ----------
        X : pd.DataFrame
            Dataframe to use for predictions

        Returns
        -------
        pd.DataFrame
            Pandas Dataframe with the predictions for every hierarchy
        """
        logger.info(message=f"START Predicting Model.")

        predictions = []
        pred_cols_template = ["timestamp","id_pred","pred_mean","sigma","pi_lower_95","pi_upper_95"]

        for id_pred, df in X.groupby('unique_id'):

            model = self.models_dict[id_pred]
            if model is None:
                logger.info(message=f"Skipping prediction for {id_pred}, as the model has not been trained")
                df_output = create_zero_dataframe(pred_cols_template, len(df))
                df_output['id_pred'] = id_pred
                df_output['timestamp'] = list(df['ds'])

            else:
                try:
                    df_test_pred = model.predict(df)
                    df_output = self.prepare_output(predictions=df_test_pred, id_pred=id_pred)

                except ValueError as e:
                    logger.info(message=f"Skipping prediction for {id_pred}, due to: {e}")
                    df_output = create_zero_dataframe(pred_cols_template, len(df))
                    df_output['id_pred'] = id_pred
                    df_output['timestamp'] = list(df['ds'])
                    
            # Appending predictions in the predictions list
            predictions.append(df_output)

        output = pd.concat(predictions).reset_index(drop=True)
        
        logger.info(message=f"DONE Predicting Model.")

        return output


    def score(self, X_true: pd.DataFrame, X_pred: pd.DataFrame) -> pd.DataFrame:
        """
        Creates the scores given two input dataframes (predictions and real values)
        using the EvaluateModel class
        Parameters
        ----------
        X_true : pd.DataFrame
            Dataframe containing the real values
        X_pred : pd.DataFrame
            Dataframe containing the predictions

        Returns
        -------
        pd.DataFrame
            Dataframe of scores generated from the EvaluateModel class
            It contains the scores only if the model for the given hierarchy has been trained
        """

        evaluator = EvaluateModel(date_true='ds', date_pred='timestamp', y_true='y', y_pred='pred_mean', upper_95='pi_upper_95', lower_95='pi_lower_95')
        evaluations = []
        
        for unique_id in X_pred['id_pred'].unique():
            df_real = X_true[X_true.index == unique_id]
            df_pred = X_pred[X_pred['id_pred'] == unique_id]

            if df_pred.pred_mean.sum() > 0:
                evaluations.append(evaluator.make_evaluation(df_real=df_real, df_pred=df_pred, id_pred=unique_id))
        
        return pd.concat(evaluations)
        

    def prepare_output(self, predictions: pd.DataFrame, id_pred: str) -> pd.DataFrame:
        """
        Prepares the output Dataframe with the requested format of:
        -'timestamp' as timestamp
        - 'id_pred' as Hierarchy
        - 'pred_mean' as Predicted Value
        - 'sigma' as Standard Deviation of the Predicted Value
        - 'pi_lower_95' as 0.95 Percentile of the Predicted Value
        - 'pi_upper_95' as 0.5 Percentile of the Predicted Value

        Parameters
        ----------
        predictions : pd.DataFrame
            Dataframe containing the predictions
        id_pred : str
            String corresponding to the Hierarchy

        Returns
        -------
        pd.DataFrame
            Pandas DataFrame with the requested format
        """

        preproc_df = predictions[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].copy()
        preproc_df.columns = ['timestamp', 'pred_mean', 'pi_lower_95', 'pi_upper_95']

        preproc_df['id_pred'] = id_pred

        # Evaluate Standard Deviation from .95 Percentiles using normality rule
        preproc_df['sigma'] = (preproc_df['pi_upper_95'] - preproc_df['pi_lower_95']) / (2 * 1.96) 
        # Round the float values and set tham as integers
        preproc_df[['pred_mean', 'sigma', 'pi_lower_95', 'pi_upper_95']] = preproc_df[['pred_mean', 'sigma', 'pi_lower_95', 'pi_upper_95']].clip(lower=0).round().astype(int)
        
        return preproc_df[['timestamp', 'id_pred', 'pred_mean', 'sigma', 'pi_lower_95', 'pi_upper_95']]
    

    def make_grid_params(self, params: Dict[str, Union[Dict[str, Union[int, float, str]], List[str]]]):
        """
        The function takes as input the dictionary of the config file 
        and executes the grid_values_hyperparameters which generates the 
        combination of grid search parameters.

        Parameters
        ----------
        params : Dict[str, Union[Dict[str, Union[int, float, str]], List[str]]]
            The dictionary of hyperparameters from the config file
        """

        # LOAD DEFAULT STEPS  
        ############################################
        config_path = self.config_path
        default_steps_config = "default_steps.toml"
        default_steps = get_configuration('prophet', config_path, default_steps_config)
        ############################################

        self.grid_params = grid_values_hyperparameters(params, default_steps)


class HierarchicalReconcileModel():
    def __init__(self, model_name: str, S: pd.DataFrame, tags: Dict[str, List[str]], 
                 reconciler: Union[List,str] = None, max_na_ratio: float = 0.5):
        """
        Init of HierarchicalReconcileModel for reconciliation of hierarchical time series

        Parameters
        ----------
        model_name : str
            Represents the name of the model which predictions must be reconciled
        S : pd.DataFrame
            Dataframe of binary values resulting from the aggregation (incidence matrix of undirected graph)
        tags : Dict[str, List[str]]
            Dictionary containing the information about the hierarchies
        reconciler : [List,str], optional
            Reconcilers, by default None
        max_na_ratio : float, optional
            Maximum ratio of NaNs and not null permitted in order to fit the model, by default 0.5
        """

        self.model_name = model_name
        self.S          = S
        self.tags       = tags

        self.max_na_ratio = max_na_ratio

        if reconciler == None:
            self.reconciler = [TopDown(method= 'proportion_averages')]
        else:
            if isinstance(reconciler, str):
                self.reconciler = [eval(reconciler)]
            elif isinstance(reconciler, list):
                self.reconciler = reconciler
            else:
                self.reconciler = [reconciler]
          

    def fit(self, X_true: pd.DataFrame, X_pred: pd.DataFrame, X_future_pred: pd.DataFrame) -> Self:
        """
        Fit method of HierarchicalReconcileModel
        It prepares the input dataframes for the reconciliation

        Parameters
        ----------
        X_true : pd.DataFrame
            Dataframe containing the true observations
        X_pred : pd.DataFrame
            Dataframe containing the predictions
        X_future_pred : pd.DataFrame
            Dataframe containing the predictions for future values

        Returns
        -------
        Self
        """
        logger.info(message='Fitting Reconciliation Model.')
        self.hrec = HierarchicalReconciliation(reconcilers=self.reconciler)

        self.X     = self.prepare_dataframe_to_hf(X_pred=X_pred, model_name=self.model_name, X_true=X_true).fillna(0)
        self.X_hat = self.prepare_dataframe_to_hf(X_pred=X_future_pred, model_name=self.model_name).fillna(0)

        return self


    def predict(self, level: List = [95], as_output: bool =True) -> pd.DataFrame:
        """
        Predict method which applies the reconciliation to the data

        Parameters
        ----------
        level : List, optional
            Confidence level for the reconcile method, by default [95]
        as_output : bool, optional
            Boolean value to switch to True when we need the output format, by default True
            Output format:  timestamp | id_pred | pred_mean | sigma | pi_lower_95 | pi_upper_95

        Returns
        -------
        pd.DataFrame
            Output dataframe
        """
        logger.info(message='Predicting Reconciliation Model.')
        Y_rec = self.hrec.reconcile(Y_hat_df=self.X_hat, Y_df=self.X, S=self.S, tags=self.tags, 
                        level=level, intervals_method='bootstrap')
        
        if as_output:
            output = self.prepare_output(Y_rec=Y_rec)

            cols = output.select_dtypes(include=np.number).columns
            output[cols] = output[cols].clip(0)
            return output

        return Y_rec


    def fit_predict(self, X_true: pd.DataFrame, X_pred: pd.DataFrame, X_future_pred: pd.DataFrame, level: List =[95], as_output: bool =True) -> pd.DataFrame:
        """
        fit_predict method of HierarchicalReconcileModel

        Parameters
        ----------
        X_true : pd.DataFrame
             Dataframe containing the true observations
        X_pred : pd.DataFrame
            Dataframe containing the predictions
        X_future_pred : pd.DataFrame
            Dataframe containing the predictions for future values
        level : List, optional
            Confidence level for the reconcile method, by default [95]
        as_output : bool, optional
            Boolean value to switch to True when we need the output format, by default True
            Output format:  timestamp | id_pred | pred_mean | sigma | pi_lower_95 | pi_upper_95

        Returns
        -------
        pd.DataFrame
            Output dataframe
        """

        Y_rec = self.fit(X_true=X_true, X_pred=X_pred, X_future_pred=X_future_pred).predict(level=level, as_output=as_output)
        
        return Y_rec
    

    def score(self, X_true: pd.DataFrame, X_pred: pd.DataFrame, check_model_pred: pd.DataFrame,
               hierarchical_output: bool = False, full_scoring: bool = True) -> Tuple[pd.Series, Union[pd.DataFrame, None]]:
        """
        Creates the scores given two input dataframes (predictions and real values)
        using the EvaluateModel class

        Parameters
        ----------
        X_true : pd.DataFrame
            Dataframe containing the real values
        X_pred : pd.DataFrame
            Dataframe containing the predictions
        check_model_pred : pd.DataFrame
            Dataframe to check before selecting the models to include in the score evaluations
        hierarchical_output : bool, optional
            Boolean value to switch to True when we need the hierarchical format, by default False
        full_scoring : bool, optional
            Boolean value to switch to True when we need also the full scores for all the models, by default True

        Returns
        -------
        Tuple[pd.Series, Union[pd.DataFrame, None]]
            Tuple representing the scores and eventually the full scoring
        """

        logger.info(message='Evaluating Reconciliation Model.')

        # Set the columns
        if hierarchical_output:
            date_pred = 'ds'
            col   = [c for c in X_pred.columns if c != 'ds' and '-hi-' not in c[-7:] and 'lo-' not in c[-7:] and '/' in c][0]
            upper = [c for c in X_pred.columns if c != 'ds' and '-hi-' in c[-7:]][0]
            lower = [c for c in X_pred.columns if c != 'ds' and '-lo-' in c[-7:]][0]
        else:
            date_pred = 'timestamp'
            col   = 'pred_mean'
            upper = 'pi_upper_95'
            lower = 'pi_lower_95'
            X_pred = X_pred.set_index('id_pred')
        
        # Instantiate the correct EvaluateModel
        evaluator = EvaluateModel(date_true='ds', date_pred=date_pred, y_true='y', y_pred=col, upper_95=upper, lower_95=lower)

        evals = []
        for unique_id in X_pred.index.unique(): # Iterate over id_preds
            df_real  = X_true[X_true.index == unique_id]
            df_pred  = X_pred[X_pred.index == unique_id]
            df_check = check_model_pred[check_model_pred.index == unique_id]

            # Evaluate if every prediction is 0 or hierarchies with more than 50% nulls, that would only insert bias in the evaluation
            if df_check['pred_mean'].sum() > 0:
                evals.append(evaluator.make_evaluation(df_real=df_real, df_pred=df_pred, id_pred=unique_id, verbose=False))
        
        scores = pd.concat(evals)

        scores_aggr = scores.drop(columns='id_pred')
        scores_aggr = scores_aggr.mean()
        scores_aggr.name = 'Metrics Reconciled'

        if full_scoring:
            return scores_aggr, scores
        else:
            return scores_aggr, None


    def best_reconciler(self, X_true: pd.DataFrame, X_pred: pd.DataFrame, X_future_true: pd.DataFrame, X_future_pred: pd.DataFrame,
                        level: List =[95], decision_function: str = 'rmse*0.5 + mae*0.5') -> Callable:
        """
        Evaluates and returns the best reconciler among the set of reconcilers provided

        Parameters
        ----------
        X_true : pd.DataFrame
            Dataframe containing the true observations
        X_pred : pd.DataFrame
            Dataframe containing the predictions
        X_future_true : pd.DataFrame
            Dataframe containing the predictions for future values
        X_future_pred : pd.DataFrame
            Dataframe containing the real values for future data
        level : List, optional
            Confidence level for the reconcile method, by default [95]
        decision_function : str, optional
            Represents the metric function which the best reconciler optimize, by default 'rmse*0.5 + mae*0.5'

        Returns
        -------
        Callable
            Best reconciler
        """
        
        logger.info(message='START Finding Best Reconciliation Method.')

        Y_rec = self.fit_predict(X_true=X_true, X_pred=X_pred, X_future_pred=X_future_pred, level=level, as_output = False)
        
        # Get reconcilers columns
        reconciler_cols = {}
        for rec in self.reconciler:
            try:
                reconciler_cols.update({rec: [c for c in Y_rec.columns if rec.__class__.__name__ in c and rec.method in c]+['ds']})
            except AttributeError:
                reconciler_cols.update({rec: [c for c in Y_rec.columns if rec.__class__.__name__ in c]+['ds']})
                continue

        get_minimum = {}
        for rec in reconciler_cols: # Iterate over the reconciler methods
            # Select only the corresponding reconciling columns
            preds = Y_rec[reconciler_cols[rec]] 

            # Concatenate the evaluations, drop the id_pred columns and evaluate the mean
            metrics, _ = self.score(X_true=X_future_true, X_pred=preds,
                                    check_model_pred=X_future_pred.set_index('id_pred'), hierarchical_output=True, full_scoring = False)

            # Set every metric as a variable
            for k in metrics.to_dict().keys():
                exec(f"{k.lower().replace(' ', '_')} = {metrics[k]}")
            
            # Update the dictionary with {score: reconciliation_method}
            get_minimum[eval(decision_function.lower())] = rec
        
        # Last run for the Original Predicted model
        metrics, _ = self.score(X_true=X_true, X_pred=X_pred,
                                check_model_pred=X_pred.set_index('id_pred'), hierarchical_output=False, full_scoring = False)
        # Set every metric as a variable
        for k in metrics.to_dict().keys():
            exec(f"{k.lower().replace(' ', '_')} = {metrics[k]}")
        # Update the dictionary with {score: reconciliation_method}
        get_minimum[eval(decision_function.lower())] = self.model_name.lower()

        # Check if the best reconciler is the base one
        # If that's the case, log a warning and calculate the second best reconciler
        minimum_error = np.min(list(get_minimum.keys()))
        if get_minimum[minimum_error] == self.model_name.lower():
            logger.warning(message='None of the reconcilers is better than the base model. Returns the second best reconciler')
            del get_minimum[minimum_error]

            minimum_error = np.min(list(get_minimum.keys()))
            best_reconciler = get_minimum[minimum_error]
        # If that's not the case, return the proper index of the reconciler by removing the model_name
        else:
            best_reconciler = get_minimum[minimum_error]
        
        logger.info(message='DONE Finding Best Reconciliation Method.')
        
        self.reconciler =  best_reconciler
    

    def prepare_output(self, Y_rec: pd.DataFrame) -> pd.DataFrame:
        """
        Prepares the output Dataframe with the requested format of:
        -'timestamp' as timestamp
        - 'id_pred' as Hierarchy
        - 'pred_mean' as Predicted Value
        - 'sigma' as Standard Deviation of the Predicted Value
        - 'pi_lower_95' as 0.95 Percentile of the Predicted Value
        - 'pi_upper_95' as 0.5 Percentile of the Predicted Value

        Parameters
        ----------
        Y_rec : pd.DataFrame
            Dataframe containing the predictions

        Returns
        -------
        pd.DataFrame
            Pandas DataFrame with the requested format
        """
        Y_rec = Y_rec.drop(columns=self.model_name.title())

        col   = [c for c in Y_rec.columns if c != 'ds' and '-hi-' not in c[-7:] and 'lo-' not in c[-7:]][0]
        upper = [c for c in Y_rec.columns if c != 'ds' and '-hi-' in c[-7:]][0]
        lower = [c for c in Y_rec.columns if c != 'ds' and '-lo-' in c[-7:]][0]

        preproc_df = Y_rec.reset_index()[['ds', 'unique_id', col, lower, upper]].copy()
        preproc_df.columns = ['timestamp', 'id_pred', 'pred_mean', 'pi_lower_95', 'pi_upper_95']

        # Evaluate Standard Deviation from .95 Percentiles using normality rule
        preproc_df['sigma'] = (preproc_df['pi_upper_95'] - preproc_df['pi_lower_95']) / (2 * 1.96) 
        # Round the float values and set tham as integers
        preproc_df[['pred_mean', 'sigma', 'pi_lower_95', 'pi_upper_95']] = preproc_df[['pred_mean', 'sigma', 'pi_lower_95', 'pi_upper_95']].clip(lower=0).round().astype(int)
        
        return preproc_df[['timestamp', 'id_pred', 'pred_mean', 'sigma', 'pi_lower_95', 'pi_upper_95']]
    

    def prepare_dataframe_to_hf(self, X_pred: pd.DataFrame, model_name: str, X_true: pd.DataFrame =None) -> pd.DataFrame:
        """
        Prepare the predicted Dataframe from a model from algorithms.models to be reconciled by one
        of HierarchicalForecast reconcilers.

        Parameters
        ----------
        X_pred : pd.DataFrame
            Pandas Dataframe containing the predictions of a model from algorithms.models
        model_name : str
            Name of the model applied to the X_pred
        X_true : pd.DataFrame, optional
            Pandas Dataframe containing the true data, by default None

        Returns
        -------
        pd.DataFrame
            Pandas Dataframe ready to be give to a HierarchicalForecast reconciler
        """
        
        check_not_isinstance(obj=X_pred, data_type=pd.DataFrame, func=get_module_and_function())
        check_not_in_iterable(obj='timestamp', iterable=X_pred.columns, func=get_module_and_function())
        check_not_in_iterable(obj='pred_mean', iterable=X_pred.columns, func=get_module_and_function())
        check_not_in_iterable(obj='id_pred', iterable=X_pred.columns, func=get_module_and_function())

        hier_pred = X_pred.rename(columns = {
            'timestamp' : 'ds', 'pred_mean' : model_name.title(), 'id_pred': 'unique_id'
        })

        hier_pred = hier_pred.set_index('unique_id')
        for col in hier_pred.columns:
            if col not in ['ds', model_name.title()]:
                hier_pred = hier_pred.drop(col, axis = 1)
        
        if type(X_true) != type(None):
            check_not_isinstance(obj=X_true, data_type=pd.DataFrame, func=get_module_and_function())
            hier_pred['y'] = list(X_true['y'])
            
        return hier_pred


class XGBoost(BaseEstimator):
    """Implements a Boosting model to perform both regression and classification"""

    def __init__(
        self,
        params: dict[str, Any] = None,
        regression: bool = False,
        cat_features: list[str] = None,
    ):
        """
        Initializes an instance of the XGBModel class with the specified parameters.

        Parameters
        ----------
        params : dict[str, Any], optional
            A dictionary of XGBoost model parameters to use. If not specified, default values will be used.
        regression : bool, optional
            A boolean indicating whether the model is for regression (True) or classification (False). Default is False.
        cat_features : list[str], optional
            A list of the names of categorical features in the input data. Default is an empty list.

        Examples
        --------
        >>> model = XGBModel(regression=True, cat_features=['A', 'B'])
        """
        self.params = {
            "objective": "reg:logistic",
            "eval_metric": "logloss",
            "verbosity": 0,
            "verbose_eval": False,
            "n_estimators": 5000,
            "early_stopping_rounds": 100,
            "tree_method": "hist",
            "n_jobs": -1,
            "enable_categorical": True,
            "booster": "gbtree",
            "max_depth": 3,
            "learning_rate": 0.01,
            "subsample": 0.8,
            "colsample_bytree": 0.8,
        }
        if regression:
            self.params["objective"] = "reg:squarederror"
            self.params["eval_metric"] = "rmse"
        if params is not None:
            self.params.update(params)

        self.regression = regression
        if cat_features is None:
            cat_features = []
        self.cat_features = cat_features

    def fit(
        self,
        X_train: pd.DataFrame,
        y_train: pd.DataFrame,
        X_val: pd.DataFrame,
        y_val: pd.DataFrame,
    ) -> Self:
        """
        Trains the XGBoost model using the provided training and validation data.
        The validation data is utilized for early stopping to determinethe optimalnumber of estimators.
        Once the best number of estimators is determined,
        the model is refitted using both the training and validation data.

        Parameters
        ----------
        X_train : pd.DataFrame
            A pandas DataFrame of training input data.
        y_train : pd.DataFrame
            A pandas DataFrame of training target data.
        X_val : pd.DataFrame
            A pandas DataFrame of validation input data,
            used to perform early stopping on the best number of estimators.
        y_val : pd.DataFrame
            A pandas DataFrame of validation target data,
            used to perform early stopping on the best number of estimators.

        Returns
        -------
        XGBModel
            The trained XGBModel object.

        Examples
        --------
        >>> model = XGBModel()
        >>> model.fit(X_train, y_train, X_val, y_val)
        """
        self.clf = xgb.XGBModel(**self.params)
        X_train = to_category(X_train, self.cat_features)
        X_val = to_category(X_val, self.cat_features)
        self.clf.fit(X_train, y_train, eval_set=[(X_val, y_val)], verbose=False)

        self.refit(pd.concat([X_train, X_val]), pd.concat([y_train, y_val]))
        return self

    def refit(self, X_train: pd.DataFrame, y_train: pd.DataFrame) -> Self:
        """
        Refits the XGBoost model with the specified training data.

        Parameters
        ----------
        X_train : pd.DataFrame
            A pandas DataFrame of training input data.
        y_train : pd.DataFrame
            A pandas DataFrame of training target data.

        Returns
        -------
        XGBModel
            The refitted XGBModel object.

        Examples
        --------
        >>> model = XGBModel().fit(X_train, y_train, X_val, y_val)
        >>> model.refit(X, y)
        """
        params = self.params.copy()
        params["n_estimators"] = self.clf.best_iteration
        params["early_stopping_rounds"] = None

        X_train = to_category(X_train, self.cat_features)
        self.clf = xgb.XGBModel(**params).fit(X_train, y_train)

        return self

    def predict(self, X: pd.DataFrame) -> np.ndarray:
        """
        Predicts the target values for the given input data.

        Parameters
        ----------
        X : pd.DataFrame
            A pandas DataFrame of input data to make predictions on.

        Returns
        -------
        np.ndarray
            An array of predicted target values.

        Examples
        --------
        >>> model = XGBModel().fit(X_train, y_train, X_val, y_val)
        >>> predictions = model.predict(X_test)
        """
        X = to_category(X, self.cat_features)
        preds = self.clf.predict(X)
        if not self.regression:
            if len(preds.shape) == 1:
                preds = preds.reshape(-1, 1)
            preds = preds / np.sum(preds, axis=1, keepdims=True)

        return preds

    def score(self, X: pd.DataFrame, y: pd.DataFrame) -> float:
        """
        Computes the model's score on the given input data and target values.

        Parameters
        ----------
        X : pd.DataFrame
            A pandas DataFrame of input data.
        y : pd.DataFrame
            A pandas DataFrame of target values.

        Returns
        -------
        float
            The model's score.

        Examples
        --------
        >>> model = XGBModel().fit(X_train, y_train, X_val, y_val)
        >>> score = model.score(X_test, y_test)
        """
        X = to_category(X, self.cat_features)
        if self.regression:
            return mean_squared_error(y, self.predict(X))
        eps = 1e-8
        y_pred = np.clip(self.predict(X), eps, 1 - eps)
        return -(y.values * np.log(y_pred)).sum(axis=1).mean()


class BoostingReconcileModel:
    def __init__(
        self,
        log_transform: bool = True,
        params_xgb: dict[str, Any] = None,
        params_preprocess: dict[str, Any] = None,
        cat_features: list[str] = None 
    ):
        """
        Initializes a BoostingReconcileModel object.

        Parameters
        ----------
        log_transform : bool, optional
            Specifies whether to apply a logarithmic transformation to the target variable,
            by default True.
        params_xgb : dict[str, Any], optional
            Additional parameters to be passed to the XGBoost model, by default None.
        params_preprocess : dict[str, Any], optional
            Additional parameters for the preprocessing step, by default None.
        cat_features : list[str], optional
            A list of categorical features to be used when training the model, by default None.

        Examples
        --------
        >>> model = BoostingReconcileModel(log_transform=True)
        """
        self.log_transform = log_transform
        if self.log_transform:
            self.target_transform = lambda x: np.log(x + 1)
            self.inverse_transform = lambda x: np.exp(x) - 1
        else:
            self.target_transform = lambda x: x
            self.inverse_transform = lambda x: x

        self.xgb_params = params_xgb if params_xgb is not None else {}

        if params_preprocess is None:
            params_preprocess = {
                                "datepart": True,
                                "preds": True,
                                "target": True,
                                "conf_inter": True,
                                "lags": [1, 2],
                            }
        self.preprocess_params = params_preprocess

        if cat_features is None:
            cat_features = ["dayofweek", "month", "quarter"]
        self.cat_features = cat_features


    @staticmethod
    def _get_id_pred(df: pd.DataFrame, n_hier: int):
        """Given a dataframe, finds all the columns at the given hierarchy"""
        id_preds = [
            c
            for c in df.columns
            if c.count("/") == max(0, n_hier - 2) and "Target" in c
        ]
        return id_preds[0].replace("Target_", "")

    @staticmethod
    def _get_hier_params(df: pd.DataFrame) -> dict[str, Any]:
        """Returns a list of preprocessing parameters for each hierarchy"""
        n_levels = df.index.str.count("/").max() + 1
        hier_params = [
            {
                "n_hier": 1,
                "sons_preds": True,
                "father_target": False,
                "divide_target": False,
            }
        ]
        hier_params += [
            {
                "n_hier": i,
                "sons_preds": False,
                "father_target": True,
                "divide_target": True,
            }
            for i in range(2, n_levels + 1)
        ]

        return hier_params

    def fit(
        self,
        X_train_true: pd.DataFrame,
        X_val_true: pd.DataFrame,
        X_train_pred: pd.DataFrame,
        X_val_pred: pd.DataFrame,
    ) -> Self:
        """
        Fits the models using the training and validation sets to find the best parameters
        After fitting is done, the model is refitted on both the training and val set

        Parameters
        ----------
        X_train_true : pd.DataFrame
            DataFrame for the true training data.
        X_val_true : pd.DataFrame
            DataFrame for the true validation data.
        X_train_pred : pd.DataFrame
            DataFrame for the predicted training data.
        X_val_pred : pd.DataFrame
            DataFrame for the predicted validation data.

        Returns
        -------
        Self
            The fitted BoostingReconcileModel object.

        Examples
        --------
        >>> model = BoostingReconcileModel()
        >>> model.fit(X_train_true, X_val_true, X_train_pred, X_val_pred)
        """
        train_real, val_real = X_train_true, X_val_true
        train_preds, val_preds = X_train_pred, X_val_pred

        self.hier_params = self._get_hier_params(train_real)
        self.lista_id_pred = []

        logger.info(message=f"START Fitting XGB Model.")
        self._models: dict[str, XGBoost] = {}
        total_runs = train_real.index.map(lambda x: x.rsplit("/", 1)[0]).nunique() + 1
        count = 0
        for params in self.hier_params:
            train_data = PreprocessBoosting(**(self.preprocess_params | params)).transform(train_real, train_preds)
            val_data = PreprocessBoosting(**(self.preprocess_params | params)).transform(val_real, val_preds)

            for train, val in zip(train_data, val_data):
                X_train, y_train = PreprocessBoosting.get_X_y(train, params["n_hier"])
                X_val, y_val = PreprocessBoosting.get_X_y(val, params["n_hier"])

                id_pred = self._get_id_pred(train, params["n_hier"])
                self.lista_id_pred += [id_pred]
                logger.info(message=f"Training {id_pred}")
                if params["n_hier"] == 1:
                    y_train.loc[:, f"Target_{id_pred}"] = self.target_transform(
                        y_train[f"Target_{id_pred}"].fillna(0).values
                    )
                    y_val.loc[:, f"Target_{id_pred}"] = self.target_transform(
                        y_val[f"Target_{id_pred}"].fillna(0).values
                    )
                    id_pred = f"reg_{id_pred}"
                    model = XGBoost(regression=True, cat_features=self.cat_features)
                else:
                    id_pred = f"class_{id_pred}"
                    model = XGBoost(regression=False, cat_features=self.cat_features)
                
                model.fit(X_train, y_train, X_val, y_val)

                count += 1
                logger.info(message=f"Remaining number of iterations - {total_runs-count}")
                self._models[id_pred] = model

        logger.info(message=f"DONE Fitting Model.")

        return self

    def refit(self, X_true: pd.DataFrame, X_pred: pd.DataFrame) -> Self:
        """
        Refits the models with the best parameters on new data.

        Parameters
        ----------
        X_true : pd.DataFrame
            DataFrame for the true data.
        X_pred : pd.DataFrame
            DataFrame for the predicted data.

        Returns
        -------
        Self
            The refitted BoostingReconcileModel object.

        Examples
        --------
        >>> model = BoostingReconcileModel()
        >>> model.fit(X_train_true, X_val_true, X_train_pred, X_val_pred)
        >>> model.refit(X_true, X_pred)
        """
        train_real, train_preds = X_true, X_pred

        logger.info(message=f"START Refitting XGB Model.")
        total_runs, count = (
            train_real.index.map(lambda x: x.rsplit("/", 1)[0]).nunique() + 1,
            0,
        )
        for params in self.hier_params:
            train_data = PreprocessBoosting(**(self.preprocess_params | params)).transform(train_real, train_preds)
            for train in train_data:
                X_train, y_train = PreprocessBoosting.get_X_y(train, params["n_hier"])

                id_pred = self._get_id_pred(train, params["n_hier"])
                logger.info(message=f"Re-Training {id_pred}")
                if params["n_hier"] == 1:
                    y_train.loc[:, f"Target_{id_pred}"] = self.target_transform(
                        y_train[f"Target_{id_pred}"].fillna(0).values
                    )
                    id_pred = f"reg_{id_pred}"
                else:
                    id_pred = f"class_{id_pred}"

                self._models[id_pred] = self._models[id_pred].refit(X_train, y_train)

                count += 1
                print(f"Remaining number of iterations - {total_runs-count}")
                logger.info(message=f"Remaining number of iterations - {total_runs-count}")

        logger.info(message=f"DONE Refitting XGB Model.")

        return self

    def predict(self, X_pred: pd.DataFrame) -> pd.DataFrame:
        """
        Makes predictions over an input DataFrame using the fitted models.

        Parameters
        ----------
        X_pred : pd.DataFrame
            DataFrame containing the predicted data.

        Returns
        -------
        pd.DataFrame
            Pandas DataFrame with the predictions for every hierarchy.

        Examples
        --------
        >>> model = BoostingReconcileModel()
        >>> model = model.fit(X_train_true, X_val_true, X_train_pred, X_val_pred)
        >>> predictions = model.predict(X_test_pred)
        """
        df_preds = X_pred

        logger.info(message=f"START Predicting XGB Model.")
        pred_mean: dict[str, np.ndarray] = dict()
        pi_lower: dict[str, np.ndarray] = dict()
        pi_upper: dict[str, np.ndarray] = dict()

        n = 0
        for params in self.hier_params:
            PP = PreprocessBoosting(
                **(
                    self.preprocess_params
                    | params
                    | {"conf_inter": True, "target": True}
                )
            )
            predict_data = PP.transform(
                df_preds,
                df_preds,
                "timestamp",
                "timestamp",
                "pred_mean",
                "pred_mean",
                "id_pred",
                "id_pred",
            )

            for data in predict_data:
                X, y = PreprocessBoosting.get_X_y(data, params["n_hier"])

                id_pred = self.lista_id_pred[n]
                if params["n_hier"] == 1:
                    y_pred = self._models[f"reg_{id_pred}"].predict(X)
                    pred_mean[id_pred] = pd.Series(y_pred, X.index)
                    pred_mean[id_pred] = self.inverse_transform(pred_mean[id_pred])
                    std = (data[f"pi_upper_{id_pred}"] - data[f"pi_lower_{id_pred}"]) / 2
                    pi_lower[id_pred] = pred_mean[id_pred] - std
                    pi_upper[id_pred] = pred_mean[id_pred] + std
                else:
                    props = self._models[f"class_{id_pred}"].predict(X)
                    for i, col in enumerate(y.columns):
                        child_mean = pred_mean[id_pred] * props[:, i]
                        pred_mean[col.replace("Target_", "")] = child_mean
                        parent_std = (pi_upper[id_pred] - pi_lower[id_pred]) / 2
                        child_std = parent_std * np.sqrt(props[:, i])
                        pi_lower[col.replace("Target_", "")] = child_mean - child_std
                        pi_upper[col.replace("Target_", "")] = child_mean + child_std
                n += 1

        logger.info(message=f"DONE Predicting XGB Model.")

        return self._prepare_output(pred_mean, pi_upper, pi_lower)
    
    def fit_predict(self,
        X_train_true: pd.DataFrame,
        X_val_true: pd.DataFrame,
        X_train_pred: pd.DataFrame,
        X_val_pred: pd.DataFrame,
        X_future_pred: pd.DataFrame) -> pd.DataFrame:
        """
        Fits the model then predicts future data (X_future_pred)

        Parameters
        ----------
        X_train_true : pd.DataFrame
            DataFrame for the true training data.
        X_val_true : pd.DataFrame
            DataFrame for the true validation data.
        X_train_pred : pd.DataFrame
            DataFrame for the predicted training data.
        X_val_pred : pd.DataFrame
            DataFrame for the predicted validation data.
        X_future_pred : pd.DataFrame
            Dataframe containing the predictions for future values

        Returns
        -------
        pd.DataFrame
            Predictions on future data
        """

        return self.fit(X_train_true, X_val_true, X_train_pred, X_val_pred).predict(X_future_pred)

    @staticmethod
    def _prepare_output(
        pred_mean: dict[str, np.ndarray],
        pi_upper: dict[str, np.ndarray],
        pi_lower: dict[str, np.ndarray],
    ) -> pd.DataFrame:
        """Converts the dictionaries given by the predict method in
        the output dataframe with the specified format"""
        pi_upper = pd.DataFrame(pi_upper)
        pi_upper = pi_upper.reset_index(names="timestamp").melt(id_vars=["timestamp"],value_vars=pi_upper.columns,
                                                                var_name="id_pred",value_name="pi_upper_95")
        pi_lower = pd.DataFrame(pi_lower)
        pi_lower = pi_lower.reset_index(names="timestamp").melt(id_vars=["timestamp"],value_vars=pi_lower.columns,
                                                                var_name="id_pred",value_name="pi_lower_95")
        pred_mean = pd.DataFrame(pred_mean)
        pred_mean = pred_mean.reset_index(names="timestamp").melt(id_vars=["timestamp"],value_vars=pred_mean.columns,
                                                                  var_name="id_pred",value_name="pred_mean")

        res = pd.concat([pred_mean, pi_lower, pi_upper], axis=1)
        res = res.loc[:, ~res.columns.duplicated()]  # Remove duplicate columns
        res["sigma"] = (res["pi_upper_95"] - res["pi_lower_95"]) / (2 * 1.96)

        res[['pred_mean', 'sigma', 'pi_lower_95', 'pi_upper_95']] = res[['pred_mean', 'sigma', 'pi_lower_95', 'pi_upper_95']].clip(lower=0).round().astype(int)
        res = res[['timestamp', 'id_pred', 'pred_mean', 'sigma', 'pi_lower_95', 'pi_upper_95']]

        return res

    def score(self, X_true: pd.DataFrame, X_pred: pd.DataFrame, 
              check_model_pred: pd.DataFrame, full_scoring: bool = True):
        """
        Creates the scores given two input dataframes (predictions and real values)
        using the EvaluateModel class.

        Parameters
        ----------
        X_true : pd.DataFrame
            DataFrame containing the real values.
        X_pred : pd.DataFrame
            DataFrame containing the predictions.
        check_model_pred : pd.DataFrame
            DataFrame to check before selecting the models to include in the score evaluations.
        full_scoring : bool, optional
            Boolean value to switch to True when we need the full scores for all the models. (default is True)

        Returns
        -------
        Tuple[pd.Series, Union[pd.DataFrame, None]]
            Tuple representing the scores and eventually the full scoring.

        Examples
        --------
        >>> model = BoostingReconcileModel()
        >>> model.fit(X_train_true, X_val_true, X_train_pred, X_val_pred)
        >>> scores, full_scores = model.score(X_true, X_pred, check_model_pred)
        """
        # Set the columns
        date_pred = 'timestamp'
        col = 'pred_mean'
        upper = 'pi_upper_95'
        lower = 'pi_lower_95'
        
        # Instantiate the correct EvaluateModel
        evaluator = EvaluateModel(date_true='ds', date_pred=date_pred, y_true='y', y_pred=col, upper_95=upper, lower_95=lower)
        
        evals = []
        for unique_id in X_true.index.unique(): # Iterate over id_preds
            df_real  = X_true[X_true.index == unique_id]
            df_pred  = X_pred[X_pred["id_pred"] == unique_id]
            df_check = check_model_pred[check_model_pred.index == unique_id]

            # Evaluate if every prediction is 0 or hierarchies with more than 50% nulls
            # that would only insert bias in the evaluation
            if df_check['pred_mean'].sum() > 1e-6:
                evals.append(evaluator.make_evaluation(df_real=df_real, df_pred=df_pred, id_pred=unique_id, verbose=False))
        
        scores = pd.concat(evals)

        scores_aggr = scores.drop(columns='id_pred')
        scores_aggr = scores_aggr.mean()
        scores_aggr.name = 'Metrics Reconciled'

        if full_scoring:
            return scores_aggr, scores
        else:
            return scores_aggr, None
