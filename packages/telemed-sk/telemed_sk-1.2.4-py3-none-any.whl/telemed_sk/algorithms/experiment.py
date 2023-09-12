from typing import Any, Callable, Dict, Type, Union, List, Tuple
from typing_extensions import Self
import pandas as pd
import logging

from .models import ProphetModel
from ..utility.check_utils import check_not_isinstance, check_not_in_iterable
from ..utility.resources import get_module_and_function, log_exception, logger

@log_exception(logger)
class ExperimentClass():
    def __init__(self,  model: str, params : Dict[str, Union[Dict[str, Union[int, float, str]], List[str]]] , config_path : str):
        """ 
        Init of the ExperimentClass
        The class instantiates the wanted model based on the <model> parameter

        Parameters
        ----------
        model : str
            Parameter identifying model to use
        params : Dict[str, Union[Dict[str, Union[int, float, str]], List[str]]]         
            Dictionary representing the model parameters
        config_path : str
            Path in which resides the configuration files 
            
        """
        self.model_name = model.lower()
        self.config_path = config_path

        if self.model_name == 'prophet':
            log_del = logging.getLogger('cmdstanpy')
            log_del.addHandler(logging.NullHandler())
            log_del.propagate = False
            log_del.setLevel(logging.CRITICAL)

            self.Model = ProphetModel(params=params, config_path=self.config_path)
        else:
            raise Exception()


    def check_consistency(self, X: pd.DataFrame):
        """
        Check if the dataframe is consistent for the next operations

        Parameters
        ----------
        X : pd.DataFrame
            Dataframe to check
        """

        check_not_isinstance(obj=X, data_type=pd.DataFrame, func=get_module_and_function())
        check_not_in_iterable(obj='unique_id', iterable=X.reset_index().columns, func=get_module_and_function())
        check_not_in_iterable(obj='ds', iterable=X.columns, func=get_module_and_function())
        check_not_in_iterable(obj='y', iterable=X.columns, func=get_module_and_function())


    def fit(self, X_train: pd.DataFrame, X_val: pd.DataFrame, y=None) -> Self:
        """
        Fit method of ExperimentClass

        Parameters
        ----------
        X_train : pd.DataFrame
            Dataframe with the train observations
        X_val : pd.DataFrame
            Dataframe with the validation observations
        y : _type_, optional
            Target_value, by default None
            This parameter is not used
        Returns
        -------
        Self
        """

        for x in [X_train,X_val]:
            self.check_consistency(X=x)
        
        self.Model.fit(X_train=X_train, X_val=X_val)

    
    def refit(self, X: pd.DataFrame):
        """
        Refit method of ExperimentClass

        Parameters
        ----------
        X : pd.DataFrame
            Dataframe on which the function refit the data
        """
        
        self.check_consistency(X=X)

        self.Model.refit(X=X)
       

    def predict(self, X: pd.DataFrame, y=None) -> pd.DataFrame:
        """
        Predict method which generates predictions given an input dataframe

        Parameters
        ----------
        X : pd.DataFrame
            Dataframe from which generate the predictions
        y : _type_, optional
            Target_value, by default None
            This parameter is not used
        Returns
        -------
        pd.DataFrame
            Output dataframe
        """

        self.check_consistency(X=X)

        output = self.Model.predict(X=X)

        return output


    def fit_predict(self, X_train: pd.DataFrame, X_val: pd.DataFrame, X_test: pd.DataFrame) -> pd.DataFrame:
        """
        fit_predict method of ExperimentClass

        Parameters
        ----------
        X_train : pd.DataFrame
            Dataframe with the train observations
        X_val : pd.DataFrame
            Dataframe with the validation observations
        X_test : pd.DataFrame
            Dataframe with the test observations

        Returns
        -------
        pd.DataFrame
            _description_
        """

        for x in [X_train, X_val, X_test]:
            self.check_consistency(X=x)
        
        output = self.Model.fit(X_train=X_train, X_val=X_val).predict(X=X_test)

        return output
    

    def create_hyperparameters_table(self, hyperparameters: dict[str, Any]) -> dict[str, Any]:
        """
        The function creates the hyperparameters table ready to be logged on mlflow

        Parameters
        ----------
        hyperparameters : dict[str, Any]
            Hyperparameters from the configuration file

        Returns
        -------
        dict[str, Any]
            Dictionary of hyperparameters to log
        """
        def get_params_to_log(model: Type[Callable], hyperparameters: list[str]) -> dict[str, Any]:
            """
            The function takes the parameters to log from the hyperparameters of the configuration file

            Parameters
            ----------
            model : Type[Callable]
                Model from which the parameters are obtained
            hyperparameters : list[str]
                Hyperparameters needed to obtain their value from the model

            Returns
            -------
            dict[str, Any]
                Dictionary of hyperparameters to log
            """
            return {hyper: getattr(model, hyper) for hyper in hyperparameters}

        return {id_pred.replace('/', '_') : get_params_to_log(model=model, hyperparameters=list(hyperparameters.keys())) if model else None 
                for id_pred, model in self.Model.models_dict.items()}


    def score(self, X_true: pd.DataFrame, X_pred: pd.DataFrame, y=None, full_scoring=True) -> Tuple[pd.Series, Union[pd.DataFrame, None]]:
        """
        Creates the scores given two input dataframes (predictions and real values)
        using the EvaluateModel class

        Parameters
        ----------
        X_true : pd.DataFrame
            Dataframe containing the real values
        X_pred : pd.DataFrame
            Dataframe containing the predictions
        y : _type_, optional
            Target_value, by default None
            This parameter is not used
        full_scoring : bool, optional
            Boolean value to switch to True when we need also the full scores for all the models, by default True

        Returns
        -------
        pd.DataFrame
            Tuple[pd.Series, Union[pd.DataFrame, None]]
            Tuple representing the scores and eventually the full scoring
        """
        self.check_consistency(X=X_true)
        check_not_in_iterable(obj='id_pred', iterable=X_pred.columns, func=get_module_and_function())
        check_not_in_iterable(obj='pred_mean', iterable=X_pred.columns, func=get_module_and_function())
        check_not_in_iterable(obj='pi_upper_95', iterable=X_pred.columns, func=get_module_and_function())
        check_not_in_iterable(obj='pi_lower_95', iterable=X_pred.columns, func=get_module_and_function())

        logger.info(message = f"START Evaluating Model.")
        scores = self.Model.score(X_true=X_true, X_pred=X_pred)

        scores_aggr = scores.drop(columns='id_pred')
        scores_aggr = scores_aggr.mean()
        scores_aggr.name = 'Metrics'

        logger.info(message = f"DONE Evaluating Model.")

        if full_scoring:
            return scores_aggr, scores
        else:
            return scores_aggr, None