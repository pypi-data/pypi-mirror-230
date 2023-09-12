import os
import mlflow
import pandas as pd
import json
import numpy as np

from ..utility.resources import log_exception, get_module_and_function, logger
from ..utility.check_utils import check_not_in_iterable, check_not_isinstance
from ..algorithms.reconcile import ReconcileClass


@log_exception(logger)
class JobClass():
    def __init__(self, model_name: str, time_granularity: str, mlflow_runs: pd.DataFrame, apply_reconciler: str):
        """
        Init of JobClass

        Parameters
        ----------
        model_name : str
            Represents the name of the model which predictions must be reconciled
        time_granularity : str
            Time aggregation on which the date column is converted
        mlflow_runs : pd.DataFrame
            The selected runs loaded from mlflow
        apply_reconciler : bool
            String value which specifies the reconcile method to apply
        """
        
        self.model_name = model_name
        self.runs = mlflow_runs
        self.apply_reconciler = apply_reconciler
        self.time_granularity = time_granularity


    def find_best_run(self, decision_function: str):
        """
        Returns the best model from a set of experiments given two metrics

        Parameters
        ----------
        decision_function : str
            Decision function to minimize in order to find the best parameters.

            The Decision function can use ONLY the evaluation parameters, beware that if an evaluation parameter
            has a space " " in its name, inside the evaluation it MUST be written as a "_", for example if using half
            Percentage Coverage and half RMSE the function will be 'percentage_coverage*0.5 + rmse*0.5'
        """
        logger.info(message = "Parsing and Selecting MLFlow runs.")
        slicer =[]
        for idx, row in self.runs.iterrows():
            try:
                num_models = len(json.loads(row['tags.mlflow.log-model.history']))
                if self.apply_reconciler in ["hierarchical", "boosting"] and num_models == 2:
                    slicer.append(idx)
                elif self.apply_reconciler == "" and num_models == 1:
                    slicer.append(idx)
            except:
                logger.warning(message = f'An Error has been encountered while reading run {row.run_id} for experiment {row.experiment_id}. Skipping the run.')
        
        if len(slicer) != 0:
            sliced_runs = self.runs.iloc[slicer]
        else:
            raise Exception('Trying to get a best run, but none available are found in the runs history. Check the if the model you are trying to use to predict has ever been executed before.')  

        logger.info(message = "Evaluating Best MLFlow run.")
        min = np.inf
        best_run = None

        if self.apply_reconciler in ["hierarchical", "boosting"]:
            metrics = [c for c in sliced_runs.columns if c.startswith('metrics.') and c.lower().split(' ')[-1] == self.apply_reconciler.lower()]
        else:
            metrics = [c for c in sliced_runs.columns if c.startswith('metrics.') and c.lower().split(' ')[-1] not in ["hierarchical", "boosting"]]

        for idx, row in sliced_runs.iterrows():
            for metric in metrics:
                if self.apply_reconciler in ["hierarchical", "boosting"]:
                    exec(f'{"_".join(metric.split(".")[1].split(" ")[:-1]).lower()}=row[metric]')
                else:
                    exec(f'{metric.split(".")[1].replace(" ","_").lower()}=row[metric]')

            score = eval(decision_function)

            if score < min:
                min = score
                best_run = row

        # Load model
        logger.info(message = "Retrieving best Model.")

        check_not_isinstance(obj=best_run, data_type=pd.Series, func=get_module_and_function(), attached_message='Something went wrong. The retrieved best run inside mlflow is not a pandas Series')
        model_uri = f"runs:/{best_run['run_id']}/{self.model_name}.pkl"
        self.Model = mlflow.sklearn.load_model(model_uri)

        if self.apply_reconciler in ["hierarchical", "boosting"]:
            folder_best_reconcile = 'best_reconciler'
            best_reconciler = os.listdir(os.path.join(best_run.artifact_uri, folder_best_reconcile))[0]
            reconciler_uri = f"runs:/{best_run['run_id']}/{folder_best_reconcile}/{best_reconciler}"
            self.best_reconciler = mlflow.sklearn.load_model(reconciler_uri)

            if self.apply_reconciler == 'hierarchical':
                path_artifacts = os.path.join(best_run.artifact_uri, 'dataframes')

                valid_true = pd.read_parquet(os.path.join(path_artifacts, 'valid_real.parquet'))
                valid_pred = pd.read_parquet(os.path.join(path_artifacts, 'valid_pred.parquet'))
                test_true  = pd.read_parquet(os.path.join(path_artifacts, 'test_real.parquet'))
                test_pred  = pd.read_parquet(os.path.join(path_artifacts, 'test_pred.parquet'))

                self.X_true = pd.concat([valid_true, test_true])
                self.X_pred = pd.concat([valid_pred, test_pred])

                with open(os.path.join(path_artifacts, 'tags.json'), 'r') as f:
                    tmp = json.load(f)
                self.S = pd.read_parquet(os.path.join(path_artifacts, 'summing_matrix.parquet'))
                self.tags = {k: np.array(v,dtype=object) for k,v in tmp.items()}


    def make_future_dataset(self, start_date: str, num_forecast_periods: str):
        """
        Generates a dataframe on which the predictions are applied starting from a given date

        Parameters
        ----------
        start_date : str
            The starting date
        num_forecast_periods : str
            The number of forecast periods to generate

        Returns
        -------
        pd.DataFrame
            The dataframe with future values
        """

        logger.info(message = "Generating Future data.")

        dates = pd.date_range(start = start_date, periods = num_forecast_periods, freq = self.time_granularity)
        id_preds = list(self.Model.models_dict.keys())

        future_df = pd.DataFrame(columns=['ds', 'unique_id'])
        for id_pred in id_preds:
            tmp = pd.DataFrame({"ds": dates, 'unique_id':[id_pred]*num_forecast_periods})
            future_df = pd.concat([future_df, tmp])

        self.future_df = future_df.set_index('unique_id')
    
    
    def predict(self, start_date: str, num_forecast_periods: str, decision_function: str ='rmse*0.5 + mae*0.5') -> pd.DataFrame:
        """
        Method for generate future predictions

        Parameters
        ----------
        start_date : str
            The starting date
        num_forecast_periods : str
            The number of forecast periods to generate
        decision_function : str
            Decision function to minimize in order to find the best parameters, by default 'rmse*0.5 + mape*0.5'

            The Decision function can use ONLY the evaluation parameters, beware that if an evaluation parameter
            has a space " " in its name, inside the evaluation it MUST be written as a "_", for example if using
            Percentage Coverage instead of the rmse inside the default function, this becomes 'percentage_coverage*0.5 + mape*0.5'
        
        Returns
        -------
        pd.DataFrame
            Output dataframe
        """

        logger.info(message = "START Predicting Future data.")

        self.find_best_run(decision_function=decision_function)
        self.make_future_dataset(start_date=start_date, num_forecast_periods=num_forecast_periods)

        forecast_model = self.Model.predict(self.future_df)

        if self.apply_reconciler.lower() in ['hierarchical', 'boosting']:

            logger.info(message = f'Applying {self.apply_reconciler.title()} Reconciliation Model')

            if self.apply_reconciler.lower() == 'hierarchical':
                params = {'model_specific_params': {'model_name': self.model_name, 'S': self.S, 
                                                    'tags': self.tags, 'reconciler': self.best_reconciler},
                          'pred_params': {'X_true': self.X_true, 'X_pred': self.X_pred, 
                                          'X_future_pred': forecast_model, 'as_output': True}}

            elif self.apply_reconciler.lower() == 'boosting':
                params = {'model_specific_params': {'reconciler': self.best_reconciler},
                          'pred_params': {'X_pred': forecast_model}}
            
        

            RC = ReconcileClass(apply_reconciler=self.apply_reconciler, mode='job', params=params)
            forecast_rec = RC.reconcile_job()

            return forecast_model, forecast_rec
        else:
            return forecast_model, None