import pandas as pd
import numpy as np
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error, mean_absolute_percentage_error

from ..utility.check_utils import check_not_isinstance
from ..utility.exceptions import ColumnNotFound
from ..utility.resources import get_module_and_function, logger


class EvaluateModel():
    def __init__(self, date_true: str, date_pred: str, y_true: str, y_pred: str, upper_95: str, lower_95: str):
        """Initialize the Evaluate class with the columns from which are take the informations

        Parameters
        ----------
        date_true : str
            Column name for the timestamps of the real dataset
        date_pred : str
            Column name for the timestamps of the predicted dataset
        y_true : str
            Target column name for the real datasets
        y_pred : str
            Target column name for the predicted datasets
        upper_95 : str
            Column name for Upper CI at 95%
        lower_95 : str
            Column name for Lower CI at 95%
        """
        check_not_isinstance(obj = date_true, data_type = str, func= get_module_and_function())
        check_not_isinstance(obj = date_pred, data_type = str, func= get_module_and_function())
        check_not_isinstance(obj = y_true, data_type = str, func= get_module_and_function())
        check_not_isinstance(obj = y_pred, data_type = str, func= get_module_and_function())
        check_not_isinstance(obj = upper_95, data_type = str, func= get_module_and_function())
        check_not_isinstance(obj = lower_95, data_type = str, func= get_module_and_function())
        self.date_true = date_true
        self.date_pred = date_pred
        self.y_true = y_true
        self.y_pred = y_pred
        self.upper_95 = upper_95
        self.lower_95 = lower_95

    def make_evaluation(self, df_real: pd.DataFrame, df_pred: pd.DataFrame, id_pred: str, verbose: bool =True) -> pd.DataFrame:
        """
        Create a DataFrame representing the evaluation metrics

        Parameters
        ----------
        df_real : pd.DataFrame
            Dataframe containing the real values
        df_pred : pd.DataFrame
            Dataframe containing the predicted values
        id_pred : str
            Hierarchys ID to be evaluated
        suppress_log : bool
            Decide to log or not the messages from the function, by default False

        Returns
        -------
        pd.DataFrame
            A pd.DataFrame containing the results for MAE, RMSE, MSE and R2
        """
        if self.date_true not in df_real.columns:
            raise ColumnNotFound(func='evaluations', column=self.date_true, data=df_real)
        if self.date_pred not in df_pred.columns:
            raise ColumnNotFound(func='evaluations', column=self.date_pred, data=df_pred)
        if self.y_true not in df_real.columns:
            raise ColumnNotFound(func='evaluations', column=self.y_true, data=df_real)
        if self.y_pred not in df_pred.columns:
            raise ColumnNotFound(func='evaluations', column=self.y_pred, data=df_pred)

        if verbose:
            logger.info(message=f'Evaluating results for {id_pred}')

        df_real= df_real.set_index(self.date_true).dropna()
        df_pred= df_pred.set_index(self.date_pred).dropna()
        inter = df_real.index.intersection(df_pred.index)

        if len(inter) == 0:
            logger.warning(message=f'Length of intersection between Predictions and Ground Truth Datasets for {id_pred} is Null. Probably one of the two Datasets has not available data (all NaN).')
            scores = {'id_pred': id_pred, 'MAE':[np.nan], 'MAPE':[np.nan], 'RMSE': [np.nan], 'MSE':[np.nan], 'R2':[np.nan], 'Percentage Coverage':[np.nan]}
        else:    
            df_real = df_real.loc[inter]
            df_pred = df_pred.loc[inter]

            # Mean Absolute Error
            # if verbose:
            #     logger.info('Evaluating MAE')
            mae = round(mean_absolute_error(df_real[self.y_true], df_pred[self.y_pred]),2)
            # Mean Absolute Error
            # if verbose:
            #     logger.info('Evaluating MAPE')
            mape = round(mean_absolute_percentage_error(df_real[self.y_true], df_pred[self.y_pred]),2)
            # Root Mean Square Error
            # if verbose:
            #     logger.info('Evaluating RMSE')
            rmse = round(mean_squared_error(df_real[self.y_true], df_pred[self.y_pred], squared = False),2)
            # Mean Square Error
            # if verbose:
            #     logger.info('Evaluating MSE')
            mse = round(mean_squared_error(df_real[self.y_true], df_pred[self.y_pred]),2)
            # Coefficient of Determination
            # if verbose:
            #     logger.info('Evaluating R2')
            r2 = round(r2_score(df_real[self.y_true], df_pred[self.y_pred]),2)
            # Forecast Coverage Percentage
            # if verbose:
            #     logger.info('Evaluating Forecast Coverage Percentage')
            coverage = self.forecast_coverage(df_real=df_real, df_pred=df_pred)

            scores = {'id_pred': id_pred, 'MAE':[mae], 'MAPE':[mape], 'RMSE': [rmse], 'MSE':[mse], 'R2':[r2], 'Percentage Coverage':[coverage]}

            # if verbose:
            #     logger.info(f'Finished Evaluating results for {id_pred}')

        # Saving the scores in a DF
        return pd.DataFrame(scores)
    
    def forecast_coverage(self, df_real : pd.DataFrame, df_pred : pd.DataFrame) -> float:
        """
        Calculate the forecast coverage metric.

        Parameters
        ----------
        df_real : pd.DataFrame
            DataFrame of real values with columns self.date and self.y_true.
        df_pred : pd.DataFrame
            DataFrame of predicted values with columns self.date, self.y_pred,
            'pi_lower_95', and 'pi_upper_95'.

        Returns
        -------
        Float
            Forecast coverage as a percentage.
        """
        # Check if the actual values fall within the prediction intervals
        within_interval = (df_real[self.y_true] >= df_pred[self.lower_95]) & (df_real[self.y_true] <= df_pred[self.upper_95])
        
        # Calculate the forecast coverage as the percentage of actual values within the prediction intervals
        forecast_coverage = within_interval.mean() * 100
        
        return forecast_coverage
