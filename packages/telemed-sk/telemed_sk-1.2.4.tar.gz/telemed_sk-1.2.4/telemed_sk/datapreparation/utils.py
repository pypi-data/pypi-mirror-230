import itertools
import holidays
import pandas as pd
import numpy as np
from statsmodels.tsa.seasonal import seasonal_decompose
from sklearn.base import BaseEstimator, TransformerMixin
from typing_extensions import Self
from typing import List, Tuple, Union, Dict
from hierarchicalforecast.utils import aggregate
import itertools
import re


from ..utility.check_utils import check_not_isinstance, check_not_in_iterable, check_datatype_convertible,check_dates_complete
from ..utility.resources import get_module_and_function, logger
from ..utility.constants import code_to_region_name, code_to_speciality

################# Transformer Functions #################
def map_columns(hierarchy: Dict[str, str], df: pd.DataFrame, 
                conversion: Dict[str, str]) -> pd.DataFrame:
    
    """
    Change the columns in the dataframe <df> according to a given <hierarchy> and <conversion> dictionary.
    The hierarchy and the conversion dictionaries MUST be specifed in the configuration file.

    Parameters
    ----------
    hierarchy : Dict[str, str]
        A dictionary mapping levels to the <df> column names.
    df : pd.DataFrame
        The input DataFrame to be mapped.
    conversion : Dict[str, str]
        A dictionary mapping levels to conversion names.

    Returns
    -------
    pd.DataFrame
        Containing the modified dataframe if there is a conversion to apply
    """
    # Verify that hierarchy is of type dict
    check_not_isinstance(obj = hierarchy, data_type = dict, func = get_module_and_function())
    # Verify that conversion is of type dict
    check_not_isinstance(obj = conversion, data_type = dict, func = get_module_and_function())
    # Verify that df is of type pd.DataFrame
    check_not_isinstance(obj = df, data_type = pd.DataFrame, func = get_module_and_function())

    df = df.copy()

    for conversion_level in conversion.keys():
        if conversion[conversion_level]:
            name_column = hierarchy[conversion_level]

            # Verify that name_column is a column in df
            check_not_in_iterable(obj = name_column, iterable = df.columns, func = get_module_and_function())

            dict_mapping = eval(conversion[conversion_level]) # Takes the conversion level string and reads it from utility.constants
            df[name_column] = df[name_column].apply(lambda x: dict_mapping[x])
    return df


def column_to_int(hierarchy: Dict[str, str], df: pd.DataFrame, 
                conversion: Dict[str, str]) -> pd.DataFrame:
    
    """
    Change datatypes in the columns in the dataframe <df> according to a given <hierarchy> and <conversion> dictionary.
    The hierarchy and the conversion dictionaries MUST be specifed in the configuration file.

    Parameters
    ----------
    hierarchy : Dict[str, str]
        A dictionary mapping levels to the <df> column names.
    df : pd.DataFrame
        The input DataFrame to be mapped.
    conversion : Dict[str, str]
        A dictionary mapping levels to conversion names. 
        If a conversion name is provided for a level, the corresponding column in the DataFrame will be converted to int64.

    Returns
    -------
    pd.DataFrame
        Containing the modified dataframe if there is a conversion to apply
    """
    # Verify that hierarchy is of type dict
    check_not_isinstance(obj = hierarchy, data_type = dict, func = get_module_and_function())
    # Verify that conversion is of type dict
    check_not_isinstance(obj = conversion, data_type = dict, func = get_module_and_function())
    # Verify that df is of type pd.DataFrame
    check_not_isinstance(obj = df, data_type = pd.DataFrame, func = get_module_and_function())

    df = df.copy()

    for conversion_level in conversion.keys():
        if conversion[conversion_level]:
            name_column = hierarchy[conversion_level]
            for column_val in df[name_column].unique():
                check_datatype_convertible(obj = column_val, data_type_conversion = int, func = get_module_and_function())
            df[name_column] = df[name_column].astype(np.int64)
    return df

def generate_time_series(df: pd.DataFrame, date_col: str,
                         time_granularity: str, hierarchy: Dict[str, str]) -> Tuple[pd.DataFrame, pd.DataFrame, Dict[str, List[str]]]:
    """
    Sequential execution of transformations to obtain a DataFrame with a time series structure

    Parameters
    ----------
    df : pd.DataFrame
        Raw dataframe from which generates timeseries
    date_col : str
        Column name identifying the columns to index on
    time_granularity : str 
        Specifies temporal granularity
    hierarchy : Dict[str, str]
        A dictionary mapping levels to the <df> column names.

    Returns
    -------
    Tuple[pd.DataFrame, pd.DataFrame, Dict[str, List[str]]]
        Returns a tuple with the following elements:
            - Y_df dataframe with the hierarchies as indexes\n
            - S_df binary matrix to understand the hierarchy levels\n
            - tags maps the hierarchy level to the hierarchy values 
    """
    
    # Verify that df is of type pd.DataFrame
    check_not_isinstance(obj = df, data_type = pd.DataFrame, func = get_module_and_function())
    # Verify that date_col is a column in df
    check_not_in_iterable(obj = date_col, iterable = df.columns, func = get_module_and_function())
    # Verify time granularity date type
    check_not_isinstance(obj = time_granularity, data_type = str, func = get_module_and_function())
    # Verify hierarchy date type
    check_not_isinstance(obj = hierarchy, data_type = dict, func = get_module_and_function())

    # Raw dataset from which to generate the time series
    df = df.copy()
    
    # Starting generating the time series
    hier_df = get_hierarchical_df(df = df, hierarchy = hierarchy, time_granularity = time_granularity, date_col = date_col)
    Y_df, S_df, tags = get_hierarchical_info(hier_df = hier_df)

    Y_df['y'] = Y_df['y'].replace(0, np.nan)

    return Y_df, S_df, tags

def get_hierarchical_df(df: pd.DataFrame, hierarchy: Dict[str, str],
                        time_granularity: str, date_col: str) -> pd.DataFrame:
    """
    The function generates the dataframe suitable for obtaining hierarchical info. 
    It generates the dataframe starting from the input dataframe by using the information
    of the configuration file.

    Parameters
    ----------
    df : pd.DataFrame
        The input dataframe (typically inside .../data/input)
    hierarchy : Dict[str, str]
        Dictionary retrieved from the configuration file.
        it contains the hierarchy columns ordered by levels
    time_granularity : str
        String referring to the time granularity.
        Information retrieved from the configuration file.
    date_col : str
        The string referring to the date column of the dataframe

    Returns
    -------
    pd.DataFrame
        A dataframe of columns: ds|y|level0|level1|level2|level3\n
        level0 refers to Italia\n
        level1, level2, level3 are obtained from the hierarchy dict
    """
    
    output_df = df[[date_col]] # Grabs the time columns, output_df remains a dataframe
    output_df['level0'] = 'Italia' # Sets level0 as the macro hierarchy Italia
    output_df['y'] = 1 # Sets 1 for each observation

    # Transforms the dataframe based on a given time_granularity (e.g. 'H' (hours), 'D' (days), 'M' (months), ...)
    # and clips them to the said granularity in order to have multiple same dates to let the aggregate sum them up
    output_df[date_col] = output_df[date_col].dt.to_period(time_granularity).dt.to_timestamp()

    # For each level, attaches the column to the output_df
    for level, col_name in hierarchy.items():
        output_df[level] = df[col_name]
    output_df = output_df.rename(columns={date_col:'ds'}) # Normalize the date_col name into 'ds'
    return output_df

def get_hierarchical_info(hier_df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame, Dict[str, List[str]]]:
    """
    The function generates the hierarchical aggregation info
    starting from the hierarchical dataframe obtained by <get_hierarchical_df>

    Parameters
    ----------
    hier_df : pd.DataFrame
        Dataframe obtained by <get_hierarchical_df>

    Returns
    -------
    Tuple[pd.DataFrame, pd.DataFrame, Dict[str, List[str]])
        Returns a tuple with the following elements:
            - Y_df dataframe with the hierarchies as indexes\n
            - S_df binary matrix to understand the hierarchy levels\n
            - tags maps the hierarchy level to the hierarchy values 

    """
    # Filters and sorts the columns regarding hiherarchy's levels
    filtered_columns = [col for col in hier_df.columns if 'level' in col]
    filtered_columns.sort()

    spec = [filtered_columns[:i] for i in range(1, len(filtered_columns) + 1)] # Builds the spec needed for the aggregate function
    Y_df, S_df, tags = aggregate(df = hier_df, spec = spec) # Executes the aggregations based on timestamps

    return Y_df, S_df, tags

def missing_data_imputation(missing_data_strategy: Union[str,int,dict], df: pd.DataFrame) -> pd.DataFrame:
    """
    The function imputes the missing values of the dataframe <df> with a given strategy <missing_data_strategy>

    Parameters
    ----------
    missing_data_strategy : dict, str or int
        Identifies whether to impute missing values and if so using which strategy/value
        Allowed parameters: 
            if str:
                - s""      : none of the missing values are replaced\n
                - s"mean"  : missing values are replaced with the mean of the known values in the dataset.\n
                - s"median": missing values are replaced with the median of the known values in the dataset.\n
                - s"zero"  : missing values are replaced with the 0.\n
                - s"bfill" : missing values are replaced with the next available value in the dataset.\n
                - s"ffill" : missing values are replaced with the most recent preceding value in the dataset.\n
            if int:
                replace NaN with the specified integer
            if dict:
                replace NaN using the specified interpolation method (allowed "polynomial" or "spline") and its order.

    df : pd.DataFrame
        The dataframe which target column will be filled with a given strategy

    Returns
    -------
    pd.DataFrame
        The dataframe afer the imputation

    Raises
    ------
    ValueError
        Invalid value for spline order
    """

    df = df.copy()
    if isinstance(missing_data_strategy, dict): 
        if missing_data_strategy['interpolation'] == "spline" and (df['y'].notna().sum() < missing_data_strategy['order'] or missing_data_strategy['order'] >5):
            logger.error(message='The number of data points must be larger than the spline degree k or k should be 1 <= k <= 5.')
            raise ValueError("Invalid value for spline order in 'datapreparation_utils.generate_time_series'")
        
    if missing_data_strategy == "":
        logger.info(message='No Missing Data Imputation applied.')
    else:
        logger.info(message=f'Missing Data Imputation with Strategy: {missing_data_strategy}')
        fillna = ReplacerNA(missing_data_strategy)
        df = fillna.fit_transform(df)
        df['y'] = df['y'].clip(lower=0)

    return df

def completing_calendar(df: pd.DataFrame, time_granularity: str) -> pd.DataFrame:
    """
    Fill missing dates in the given DataFrame 'df' to complete the calendar,
    considering the specified 'time_granularity'.

    Parameters
    ----------
    df : pd.DataFrame
        The input DataFrame containing a temporal column 'ds' and a value column 'y'.
    
    time_granularity : str 
        The frequency level to consider for completing the calendar (e.g., 'D' for daily, 'H' for hourly, 'W' for weekly, etc.).

    Returns
    ------
    pd.DataFrame
        The DataFrame with the calendar completed, with missing dates filled with NaNs (or 0s).
    """

    df = df.copy()
    index_col = df.index.name
    ds, y = df.columns

    # Check if the dates are already complete at the specified granularity, if not refill df
    if not check_dates_complete(date_series=df[ds], freq=time_granularity):

        df = df.reset_index()
        df.set_index(ds, inplace=True)
        # Pivot the DataFrame to create a complete calendar at the specified granularity
        df = df.pivot(columns=index_col, values=y).resample(time_granularity).sum()
        # Reset the index and melt the DataFrame to bring it back to the original format
        df = df.reset_index().melt(id_vars=ds, var_name=index_col, value_name=y)
        df = df.sort_values(by=[index_col, ds]).set_index(index_col)
        df[y] = df[y].replace(0, np.nan)

    return df

################# Utils Teleconsulto  #################
def filter_target_col(df: pd.DataFrame, target_col: Union[str, List[str]]) -> pd.DataFrame:
    """
    The function filters the rows of the dataframe on the unique target_col 

    Parameters
    ----------
    df : pd.DataFrame
        The input dataframe
    target_col : Union[str, List[str]]
        The target column

    Returns
    -------
    pd.DataFrame
        The dataframe with the unique values for the target col
    """
    df = df.copy()
    df = df.drop_duplicates(subset=target_col)
    return df

################# Transformer Classes #################
class Normalizer(BaseEstimator, TransformerMixin):
    def __init__(self):
        """
        Normalize data to the range [0, 1].
        """
        pass

    def fit(self, X: np.array, y=None) -> Self:
        """
        Fit the Normalizer to the data. No computations are needed in this case.

        Parameters
        -----------
        X : np.array
            Input data.

        Returns
        --------
        Self
            Fitted Normalizer object.
        """
        
        self.min = np.min(X)
        self.max = np.max(X)
        return self

    def transform(self, X: np.array) -> np.array:
        """
        Normalize the input data to the range [0, 1].

        Parameters
        -----------
        X : np.array
            Input data.

        Returns
        --------
        X_normalized : np.array
            Normalized data obtained by scaling the values to the range [0, 1].
        """
        X_normalized = (X - self.min) / (self.max - self.min)
        return X_normalized

    def inverse_transform(self, X_normalized: np.array) -> np.array:
        """
        Reconstruct the original data from the normalized data by applying the inverse transformation.

        Parameters
        -----------
        X_normalized : np.array
            Normalized data.

        Returns
        --------
        X : np.array
            Reconstructed data obtained by applying the inverse transformation.
        """
        X = X_normalized * (self.max -self.min) + self.min
        return X
  

class ReplacerNA(TransformerMixin, BaseEstimator):

    def __init__(self, method: Union[str, int, Dict[str, Union[str, int]]]) -> Self:

        """
        Class for handling of NA

        Parameters
        ----------
        method : Union[str, int, Dict[str, Union[str, int]]]]
            - If str specify the method to replace NA value (mean,median,zero), if int specify the value to replace NA value\n
            - If dict specify which interpolation method to use between polynomial and spline and its order
        """
        
        self.method = method

    def fit(self, X: pd.DataFrame) -> Self:

        """
        Compute value useful for replacing NA

        Parameters
        ----------
        X : pd.DataFrame
            Dataframe containing two columns (timestamp and volumes of time series)         

        Returns
        -------
        Self
            Fitted replacer
        """
        
        if self.method == "mean":
            self.value = X.iloc[:,1].mean()
            self.method_for_df = None
        elif self.method == "median":
            self.value = X.iloc[:,1].median()
            self.method_for_df = None
        elif self.method == "zero":
            self.value = 0
            self.method_for_df = None
        elif self.method == "bfill":
            self.value = None
            self.method_for_df = "bfill"
        elif self.method == "ffill":
            self.value = None
            self.method_for_df = "ffill"
        elif self.method == "interpolate":
            self.value = None
            self.method_for_df = "interpolate"
        elif isinstance(self.method, dict):
            self.value = self.method["order"]
            self.method_for_df = self.method["interpolation"].lower()

        else:
            self.value = self.method
            self.method_for_df = None

        return self

    def transform(self, X: pd.DataFrame) -> pd.DataFrame:

        """
        Perform replacement of missing values

        Parameters
        ----------
        X : pd.DataFrame
            Dataframe containing two columns (timestamp and volumes of time series)

        Returns
        -------
        X : pd.DataFrame
            Transformed time series
        """
        if self.method_for_df in ["polynomial", "spline"]:
            # Create a temporary DataFrame with a DatetimeIndex
            temp_df = pd.DataFrame({X.columns[1]: X.iloc[:, 1]})
            temp_df.index = pd.to_datetime(X.iloc[:, 0])

            # Perform time-based interpolation in the temporary DataFrame
            temp_df.iloc[:, 0] = temp_df.iloc[:, 0].interpolate(method=self.method_for_df, order = self.value)

            # Assign the interpolated values to the original column in the X DataFrame
            X.iloc[:, 1] = temp_df.iloc[:, 0].values
        else:
            X.fillna(self.value, method=self.method_for_df, inplace=True)
        return X
    

class Detrender(TransformerMixin, BaseEstimator):

    def __init__(self, period: int) -> Self:

        """
        Detrending time series

        Parameters
        ----------
        period : int
            Specify period considered for compute additive decomposition

        Returns
        -------
        Self
        """

        self.period = period


    def fit(self, X: pd.DataFrame) -> Self:

        """
        Compute additive decomposition useful to detrend time series

        Parameters
        ----------
        X : pd.DataFrame
            Dataframe containing two columns (timestamp and volumes of time series)         

        Returns
        -------
        Self
            Fitted detrender
        """

        additive_decomp = seasonal_decompose(X.iloc[:,1], model="additive", period=self.period, extrapolate_trend="freq")
        self.trend = additive_decomp.trend

        return self

    def transform(self, X: pd.DataFrame) -> pd.DataFrame:
        """
        Perform detrending of time series

        Parameters
        ----------
        X : pd.DataFrame
            Dataframe containing two columns (timestamp and volumes of time series)

        Returns
        -------
        X : pd.DataFrame
            Transformed time series
        """

        detrend_time_series = X.iloc[:,1] - self.trend
        ris = pd.concat([X.iloc[:,0],detrend_time_series],axis=1)
        ris.columns = X.columns

        return  ris
    

class Deseasoner(TransformerMixin, BaseEstimator):

    def __init__(self, period: int) -> Self:
        """
        Deseasonalises time series

        Parameters
        ----------
        period : int
            Specify period considered for compute additive decomposition
        """

        self.period = period


    def fit(self, X: pd.DataFrame) -> Self:
        """
        Compute additive decomposition useful to deseasonalises time series

        Parameters
        ----------
        X : pd.DataFrame
            Dataframe containing two columns (timestamp and volumes of time series)         

        Returns
        -------
        Self
            Fitted deseasoner
        """
        
        additive_decomp = seasonal_decompose(X.iloc[:,1], model="additive", period=self.period, extrapolate_trend="freq")
        self.seasonal = additive_decomp.seasonal

        return self

    def transform(self, X: pd.DataFrame) -> pd.DataFrame:
        """
        Perform deseasonalises of time series

        Parameters
        ----------
        X : pd.DataFrame
            Dataframe containing two columns (timestamp and volumes of time series)

        Returns
        -------
        X : pd.DataFrame
            Transformed time series
        """

        deseason_time_series = X.iloc[:,1] - self.seasonal
        ris = pd.concat([X.iloc[:,0],deseason_time_series],axis=1)
        ris.columns = X.columns

        return ris


class Differencer(TransformerMixin, BaseEstimator):

    def __init__(self, lag: int) -> Self:
        """
        Differencing time series
        
        Parameters
        ----------
        lag : int
            Differencing time series lag

        Returns
        -------
        Self
        """

        self.lag = lag

    def fit(self, X: pd.DataFrame) -> Self:
        """
        Compute value useful to compute differencing time series

        Parameters
        ----------
        X : pd.DataFrame
            Dataframe containing two columns (timestamp and volumes of time series)         

        Returns
        -------
        Self
            Fitted normalizer
        """

        self.shape = X.shape[0]
        self.lag_time_series = X.iloc[:self.shape-self.lag,1]
        self.timestamp = X.iloc[self.lag:,0].reset_index(drop=True)

        return self
    
    def transform(self, X: pd.DataFrame) -> pd.DataFrame:
        """
        Perform differencing time series

        Parameters
        ----------
        X : pd.DataFrame
            Dataframe containing two columns (timestamp and volumes of time series)

        Returns
        -------
        X : pd.DataFrame
            Transformed time series
        """

        time_series_lagged = X.iloc[self.lag:,1].reset_index(drop=True) - self.lag_time_series
        ris = pd.concat([self.timestamp,time_series_lagged], axis=1)
        ris.columns = X.columns
        
        return ris


class OutlierRemover(BaseEstimator, TransformerMixin):
    def __init__(self, lower_threshold_percentile: Union[int, float] =5, upper_threshold_percentile: Union[int, float]=95):
        """
        Remove outliers from a dataset by capping values above and below thresholds.

        Parameters
        -----------
        lower_threshold_percentile : Union[int, float], optional 
            Percentile threshold below which values will be capped, by default 5
        upper_threshold_percentile : Union[int, float], optional
            Percentile threshold above which values will be capped, by default 95
        """
        self.upper_threshold_percentile = upper_threshold_percentile
        self.lower_threshold_percentile = lower_threshold_percentile
        self.upper_threshold = None
        self.lower_threshold = None

    def fit(self, X: np.array, y=None) -> Self:
        """
        Compute the upper and lower thresholds based on percentiles of the input data.

        Parameters
        -----------
        X : np.array
            Input data.

        Returns
        --------
        Self
            Fitted OutlierRemover object.
        """
        self.upper_threshold = np.percentile(X, self.upper_threshold_percentile)
        self.lower_threshold = np.percentile(X, self.lower_threshold_percentile)
        return self

    def transform(self, X: np.array) -> np.array:
        """
        Cap the values above the upper threshold and below the lower threshold.

        Parameters
        -----------
        X : np.array
            Input data.

        Returns
        --------
        X_transformed : np.array
            Transformed data with capped outlier values.
        """
        X[X > self.upper_threshold] = self.upper_threshold
        X[X < self.lower_threshold] = self.lower_threshold
        return X
    

class Smoother(BaseEstimator, TransformerMixin):
    def __init__(self, window_size: int):
        """
        Smoothes a time series by applying a moving average window.

        Parameters:
        -----------
        window_size : int
            Size of the moving average window.
        """
        self.window_size = window_size

    def fit(self, X: np.array, y=None) -> Self:
        """
        Fit the Smoother to the data. No computations are needed in this case.

        Parameters
        -----------
        X : np.array
            Input data.

        Returns
        --------
        Self
            Fitted Smoother object.
        """
        return self

    def transform(self, X: np.array) -> np.array:
        """
        Smooth the input data by applying a moving average window.

        Parameters
        -----------
        X : np.array
            Input data.

        Returns
        --------
        X_smoothed : np.array
            Smoothed data obtained by applying the moving average window.
        """
        
        X_smoothed = X.rolling(window=self.window_size, min_periods=1).mean()
        return X_smoothed


class Differentiator(BaseEstimator, TransformerMixin):
    def __init__(self, order: int):
        """
        Differentiates "order" times a time series by taking differences between consecutive values.

        Parameters
        -----------
        order : int
            Order of differentiation.
        """
        self.order = order

    def fit(self, X: np.array, y=None) -> Self:
        """
        Fit the Differentiator to the data. No computations are needed in this case.

        Parameters
        -----------
        X : np.array
            Input data.

        Returns
        --------
        Self
            Fitted Differentiator object.
        """
        return self

    def transform(self, X: np.array) -> np.array:
        """
        Apply differentiation to the input data by taking differences between consecutive values.
 
        Parameters
        -----------
        X : np.array
            Input data.

        Returns
        --------
        X_transformed : np.array
            Transformed data obtained by taking differences between consecutive values.
        """
        X_transformed = X.copy()
        for _ in range(self.order):
            X_transformed = X_transformed.diff()
        X_transformed = np.nan_to_num(X_transformed, nan=0.0)
        return X_transformed


class LogTransformer(BaseEstimator, TransformerMixin):
    def __init__(self):
        """
        Logarithmic transformation of data.
        """
        pass

    def fit(self, X: np.array, y=None) -> Self:
        """
        Fit the LogTransformer to the data. No computations are needed in this case.

        Parameters
        -----------
        X : np.array
            Input data.

        Returns
        --------
        Self
            Fitted LogTransformer object.
        """
        return self

    def transform(self, X: np.array) -> np.array:
        """
        Apply the logarithmic transformation to the input data.

        Parameters:
        -----------
        X : np.array
            Input data.

        Returns:
        --------
        X_transformed : np.array
            Transformed data obtained by applying the logarithmic transformation.
        """
        X_transformed = np.log1p(X)
        return X_transformed

    def inverse_transform(self, X_transformed: np.array) -> np.array:
        """
        Reconstruct the original data from the transformed data by applying the inverse logarithmic transformation.

        Parameters
        -----------
        X_transformed : np.array
            Transformed data.

        Returns
        --------
        X_reconstructed : np.array
            Reconstructed data obtained by applying the inverse logarithmic transformation.
        """
        X_reconstructed = np.expm1(X_transformed)
        return X_reconstructed


##################### Transform function for xgboost input data ########################
def datepart(df: pd.Series) -> pd.DataFrame:
    """
    Extracts various date/time parts from a pandas Series of datetime values,
    and returns them as a new DataFrame.

    Parameters
    ----------
    df : pd.Series
        A pandas Series of datetime values to extract date/time parts from.

    Returns
    -------
    pd.DataFrame
        A new pandas DataFrame containing the extracted date/time parts,
        with the same index as the input Series.

    Examples
    --------
    >>> dates = pd.Series(['2022-01-01 12:00:00', '2022-01-02 18:00:00'])
    >>> datepart(dates)
                        dayofmonth  dayofweek  dayofyear  hour  year  month  quarter  holiday  weekend
    2022-01-01 12:00:00           1          5          1    12  2022      1        1     True     True
    2022-01-02 18:00:00           2          6          2    18  2022      1        1    False     True
    """
    it_holidays = holidays.country_holidays('IT')
    df_ds = pd.to_datetime(df.values)
    new_df = pd.DataFrame()
    new_df['dayofmonth'] = df_ds.day
    new_df['dayofweek'] = df_ds.dayofweek
    new_df['dayofyear'] = df_ds.dayofyear
    # new_df['hour'] = df_ds.hour
    new_df['year'] = df_ds.year
    new_df['month'] = df_ds.month
    new_df['quarter'] = df_ds.quarter
    new_df['holiday'] = df_ds.map(lambda x: x in it_holidays)
    new_df['weekend'] = df_ds.dayofweek.map(lambda x: x in [5, 6])
    
    new_df.index = df.values

    return new_df


def get_hierarchy_column(df: pd.DataFrame, data: str, values: str, hier: str, n_hier: int = None, fill_value: int = 0,
                         sons: bool = False, father: bool = False,type_: str="") -> list[pd.DataFrame]:
    """
    Extracts hierarchy-specific columns from a DataFrame based on the specified parameters.

    Parameters
    ----------
    df : pd.DataFrame
        The DataFrame containing the data.
    data : str
        The column name in `df` to be used as the index for the pivot table.
    values : str
        The column name in `df` to be used as the values for the pivot table.
    hier : str
        The column name in `df` to be used for creating the hierarchy in the pivot table.
    n_hier : int, optional
        The level of hierarchy to consider. (default is None)
    fill_value : int, optional
        The value to fill missing entries in the pivot table. (default is 0)
    sons : bool, optional
        Boolean value indicating whether to include only the columns at the same hierarchy level or include sub-columns as well. (default is False)
    father : bool, optional
        Boolean value indicating whether to include the father column along with the selected columns. (default is False)
    type_ : str, optional
        A prefix to be added to the column names in the resulting pivot table. (default is "")

    Returns
    -------
    List[pd.DataFrame]
        A list of DataFrames, each containing the selected hierarchy-specific columns.

    Examples
    --------
    >>> df = pd.DataFrame(...)
    >>> hierarchy_columns = get_hierarchy_column(df, 'data_column', 'values_column', 'hierarchy_column', n_hier=2, sons=True)
    """
        
    pivot = pd.pivot_table(df.fillna(0),values=values,index=data,columns=hier,fill_value=fill_value)
    pivot.columns = [type_ + "_" + i for i in pivot.columns]
    n_hiers = np.array([n_hier-1,n_hier,n_hier+1])[[father,True,sons]]
    
    if n_hier:
        col = [i for i in pivot.columns if len(i.split("/")) in n_hiers]
        pivot = pivot.loc[:,col]
    
    if sons:
        cols = [list(filter(lambda x : i in x,pivot.columns)) if not father else [i.rsplit("/")[0]] + list(filter(lambda x : i in x,pivot.columns))
                for i in np.unique([i.rsplit("/",1)[0] for i in pivot.columns if len(i.split("/")) == n_hiers[-1]])]
    else:
        cols = [list(filter(lambda x : i in x,pivot.columns)) if not father else [i] + list(filter(lambda x : i in x,pivot.columns))
                for i in np.unique([i.rsplit("/",1)[0] for i in pivot.columns if len(i.split("/")) == n_hiers[-1]])]
    
    return [pivot.loc[:,np.unique(i)] for i in cols]


def divide_by_father(df: pd.DataFrame) -> pd.DataFrame:
    """
    Divides all columns in a pandas DataFrame by a "father" column,
    and returns the result as a new DataFrame. The father column is
    the one with the least number of "/"

    Parameters
    ----------
    df : pd.DataFrame
        A pandas DataFrame containing the columns to be divided,
        as well as a "father" column to divide by.

    Returns
    -------
    pd.DataFrame
        A new pandas DataFrame containing the resulting values of the division.
        The "father" column is included in the new DataFrame.

    Examples
    --------
    >>> data = {'A/B': [1, 2, 3], 'A/C': [4, 5, 6], 'A': [7, 8, 9]}
    >>> df = pd.DataFrame(data)
    >>> divide_by_father(df)
              A/B       A/C    A
    0  0.142857  0.571429  7
    1  0.250000  0.625000  8
    2  0.333333  0.666667  9
    """
    father_index = np.argmin([i.count("/") for i in df.columns])
    father = df.columns[father_index]
    
    df_div = df.div(df[father].values,axis=0)
    df_div[father] = df[father]
    
    df_div.fillna(1/(len(df.columns)-1),inplace=True)
    
    return df_div

def get_lagged_column(df: pd.DataFrame, lags: list[int], columns: list[str] = None) -> pd.DataFrame:
    """
    Computes lagged versions of one or more columns in a pandas DataFrame,
    and returns them as a new DataFrame.

    Parameters
    ----------
    df : pd.DataFrame
        A pandas DataFrame containing the original columns to be lagged.
    lags : list[int]
        A list of integer values indicating the number of lags to compute.
    columns : list[str], optional
        The name of the columns to be lagged. If not specified, all columns in
        the input DataFrame will be lagged.

    Returns
    -------
    pd.DataFrame
        A new pandas DataFrame containing the lagged versions of the specified column(s).

    Examples
    --------
    >>> data = {'A': [1, 2, 3, 4], 'B': [5, 6, 7, 8]}
    >>> df = pd.DataFrame(data)
    >>> get_lagged_column(df, [1, 2], 'A')
       Lag1_A  Lag2_A
    0     NaN     NaN
    1     1.0     NaN
    2     2.0     1.0
    3     3.0     2.0
    """
    if columns:
        cols = [columns]
    else:
        cols = df.columns
        
    col_lagged = [df[cols].shift(lag) for lag in lags]
    col_names = ["_".join(i) for i in itertools.product(["Lag"+str(i) for i in lags],cols)]
    
    df_lag = pd.concat(col_lagged,axis=1)
    df_lag.columns = col_names
    
    return df_lag


def clean_df_columns(df: pd.DataFrame, hierarchy: Dict[str, str]) -> pd.DataFrame:
    """
    The function cleans the dataframes columns specified in the hierarchy dict.
    It removes special characters and truncate the length of the column value to a maximum of 200 characters

    Parameters
    ----------
    df : pd.DataFrame
        The dataframe which the cleaning procedure is applied
    hierarchy : Dict[str, str]
        A dictionary mapping levels to the <df> column names.

    Returns
    -------
    pd.DataFrame
        Cleaned dataframe
    """

    # Verify that hierarchy is of type dict
    check_not_isinstance(obj = hierarchy, data_type = dict, func = get_module_and_function())
    
    for name_column in hierarchy.values():
        check_not_in_iterable(obj = name_column, iterable = df.columns, func = get_module_and_function())
        if df[name_column].convert_dtypes().dtype == 'string[python]':
            df[name_column] = df[name_column].str.replace(r'[^0-9a-zA-Z]+', '', regex=True).str.slice(start = 0, stop = 200)
    return df

