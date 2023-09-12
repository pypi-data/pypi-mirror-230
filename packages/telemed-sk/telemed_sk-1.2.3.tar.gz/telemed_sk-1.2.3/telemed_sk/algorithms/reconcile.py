from typing import Any, Dict, Tuple, Type, Union
import pandas as pd
import datetime

from .models import BoostingReconcileModel, HierarchicalReconcileModel
from ..utility.resources import log_exception,logger

@log_exception(logger)
class ReconcileClass():
    def __init__(self, apply_reconciler: str, mode: str, params: Dict[str, Dict[str, Any]]):
        """Initialize the parameters required to the ReconcileClass methods.

        Parameters
        ----------
        apply_reconciler : str
            Reconciliation method to apply.
        mode : str
            Launch mode of the Reconciliation Pipeline, can have "experiment" or "job" values.
        params : Dict[str, Dict[str, Any]]
            Dictionary of parameters required by the pipeline:
            - If mode is on "experiment" the required param keys are:
                - model_specific_params: For all those parameters required for model initializations and other steps
                                         taken before models fit and predict for "experiment" mode
                - fit_params: For all those parameters required by the models fit function
                - pred_params: For all those parameters required by the models predict function
                - score_params: For all those parameters required by the models score function
                - refit_params: For all those parameters required by the models refitting steps

            - If mode is on "job" the required param keys are:
                - model_specific_params: For all those parameters required for model initializations and other steps
                                                taken before the predictions for "job" mode
                - pred_params: For all those parameters required by the models predict function

        Raises
        ------
        Exception
            Return Exception if a wong mode is given, available modes are either "experiment" or "job".
        """
        
        self.apply_reconciler = apply_reconciler
        self.params = params
        if mode == 'experiment':
            self.model_specific_params = self.params['model_specific_params']
            self.fit_params = self.params['fit_params']
            self.pred_params = params['pred_params']
            self.score_params = self.params['score_params']
            self.refit_params = self.params['refit_params']
            self.init_reconcile_experiment()

        elif mode == 'job':
            self.model_specific_params = self.params['model_specific_params']
            self.pred_params = self.params['pred_params']

            self.init_reconcile_job()
        
        else:
            raise Exception(f'Incorrect value for <mode>: {mode}. It can take values "experiment" or "job".')


    def init_reconcile_experiment(self):
        """Given a reconciliation method, it executes all the required steps in order to correctly initialize the
        corresponding reconciliation Class."""
        # INIT HIERARCHICAL
        if self.apply_reconciler == 'hierarchical':
            # UPDATE SELF ONLY FOR HIERARCHICAL - TRAINING PREDICTIONS
            self.refit_params_train = self.params['refit_params_train']

            model = HierarchicalReconcileModel(model_name=self.model_specific_params['model_name'],
                                               S=self.model_specific_params['S'],
                                               tags=self.model_specific_params['tags'])
            
            model.best_reconciler(X_true=self.model_specific_params['X_train_true'], X_pred=self.model_specific_params['X_train_pred'],
                                  X_future_true=self.fit_params['X_true'], X_future_pred=self.fit_params['X_pred'])
            
            try:
                self.reconciler_filename = f'{model.reconciler.__class__.__name__}_method-{model.reconciler.method}'
                self.reconcile = f'{model.reconciler.__class__.__name__}(method="{model.reconciler.method}")'
            except AttributeError:
                self.reconciler_filename = f'{model.reconciler.__class__.__name__}'
                self.reconcile = f'{model.reconciler.__class__.__name__}()'

            # RE-INIT HIERARCHICAL WITH BEST RECONCILER
            self.model = HierarchicalReconcileModel(model_name=self.model_specific_params['model_name'],
                                                    S=self.model_specific_params['S'],
                                                    tags=self.model_specific_params['tags'], reconciler=self.reconcile)

        # INIT BOOSTING    
        elif self.apply_reconciler == 'boosting':
            self.model = BoostingReconcileModel()
            # SET PARAMETERS
            self.reconciler_filename = f'{self.model.__class__.__name__}'


    def init_reconcile_job(self):
        """Given a reconciliation method, it executes all the required steps in order to correctly use the stored
        reconciliation Class fitted during the experiment."""
        # INIT HIERARCHICAL
        if self.apply_reconciler.lower() == 'hierarchical':
            self.reconciler = self.model_specific_params['reconciler']
            try:
                reconcile = f'{self.reconciler[0].__class__.__name__}(method="{self.reconciler[0].method}")'
            except AttributeError:
                reconcile = f'{self.reconciler[0].__class__.__name__}()'
            
            self.model = HierarchicalReconcileModel(model_name=self.model_specific_params['model_name'], S=self.model_specific_params['S'], tags=self.model_specific_params['tags'], reconciler=reconcile)
        
        # INIT BOOSTING 
        elif self.apply_reconciler.lower() == 'boosting':
            self.model = self.model_specific_params['reconciler']


    def reconcile_experiment(self) -> Tuple[pd.DataFrame, pd.Series, pd.DataFrame,pd.DataFrame, 
                                            Union[Type[BoostingReconcileModel], Type[HierarchicalReconcileModel]], 
                                            Dict[str, datetime.datetime]]:
        """Executes the "experiment" mode Pipeline and returns the objects needed to be logged and stored.

        Returns
        -------
        Tuple[pd.DataFrame, pd.Series, pd.DataFrame,pd.DataFrame, Union[Type[BoostingReconcileModel], Type[HierarchicalReconcileModel]], Dict[str, datetime.datetime]]
            Returns the following objects:
            - The pandas DataFrame for reconciled predictions over the Test set
            - The pandas Series for reconciled Metrics
            - The pandas DataFrame for every reconciled Scores hierarchy
            - The pandas DataFrame for reconciled predictions over Validation set
            - The reconciliation model to be logged on mlflow
            - The execution time informations for fit and predict
        """
        test_rec_pred = self.fit_predict(fit_params=self.fit_params, pred_params=self.pred_params)

        self.score_params['X_pred'] = test_rec_pred
        metrics, scores = self.score(score_params=self.score_params)

        # SET UP ARTIFACTS & MODELS TO LOG ON MLFLOW
        if self.apply_reconciler == 'hierarchical':
            valid_rec_pred = self.model.fit_predict(**self.refit_params)
            train_rec_pred = self.model.fit_predict(**self.refit_params_train)
            # OBTAIN HIERARCHICAL MODEL TO LOG
            model_to_log = self.model.reconciler

        elif self.apply_reconciler == 'boosting':
            valid_rec_pred = self.model.predict(self.fit_params['X_val_pred'])
            train_rec_pred = self.model.predict(self.fit_params['X_train_pred'])
            # REFIT AND PREDICT MODEL ON ALL THE DATA
            self.model.refit(**self.refit_params)
            model_to_log = self.model

        exec_time_info = {"data_inizio_fit" : self.date_start_fit, "data_fine_fit" : self.date_end_fit, 
                          "data_inizio_pr" : self.date_start_predict, "data_fine_pr" : self.date_end_predict}

        return test_rec_pred, metrics, scores, valid_rec_pred, train_rec_pred, model_to_log, exec_time_info

        
    def reconcile_job(self) -> pd.DataFrame:
        """Executes the "job" mode Pipeline and returns the pandas DataFrame for the reconciled future predictions.

        Returns
        -------
        pd.DataFrame
            The pandas DataFrame for the reconciled future predictions.
        """
        # SET UP ARTIFACTS & MODELS TO LOG ON MLFLOW
        if self.apply_reconciler == 'hierarchical':
            output = self.model.fit_predict(**self.pred_params)

        elif self.apply_reconciler == 'boosting':
            output = self.model.predict(**self.pred_params)

        return output


    def fit(self, fit_params: Dict[str, Any], **kwargs):
        """Executes the specific reconciliation Class fit method.

        Parameters
        ----------
        fit_params : Dict[str, Any]
            All parameters required by the fit method.
        """
        # Fit reconciler and take computational time
        self.date_start_fit = datetime.datetime.now()
        self.model.fit(**fit_params, **kwargs)
        self.date_end_fit = datetime.datetime.now()

        return self

    def predict(self, pred_params: Dict[str, Any]) -> pd.DataFrame:
        """Executes the specific reconciliation Class predict method.

        Parameters
        ----------
        pred_params : Dict[str, Any]
            All parameters required by the predict method.

        Returns
        -------
        pd.DataFrame
            Pandas DataFrame with the reconciled predictions
        """
        # Predict reconciler and take computational time
        self.date_start_predict = datetime.datetime.now()
        output = self.model.predict(**pred_params)
        self.date_end_predict = datetime.datetime.now()

        return output
    
    def fit_predict(self, fit_params: Dict[str, Any], pred_params: Dict[str, Any], **kwargs) -> pd.DataFrame:
        """Executes the specific reconciliation Class fit and predict methods.

        Parameters
        ----------
        fit_params : Dict[str, Any]
            All parameters required by the fit method.
        pred_params : Dict[str, Any]
            All parameters required by the predict method.

        Returns
        -------
        pd.DataFrame
            Pandas DataFrame with the reconciled predictions
        """
        output = self.fit(fit_params=fit_params, **kwargs).predict(pred_params=pred_params)

        return output
    
    def score(self, score_params: Dict[str, Any], **kwargs) -> Tuple[pd.DataFrame, pd.Series]:
        """Executes the specific reconciliation Class score method.

        Parameters
        ----------
        score_params : Dict[str, Any]
            All parameters required by the score method.

        Returns
        -------
        Tuple[pd.DataFrame, pd.Series]
            Returns the following objects:
            - The pandas Series for reconciled Metrics
            - The pandas DataFrame for every reconciled Scores hierarchy
        """
        metrics, scores = self.model.score(**score_params, **kwargs)
        return metrics, scores
