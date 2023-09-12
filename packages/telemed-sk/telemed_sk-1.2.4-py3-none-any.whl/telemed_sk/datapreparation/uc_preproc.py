from typing import Dict
import pandas as pd

from .utils import clean_df_columns, map_columns, filter_target_col, column_to_int
from ..utility.resources import logger

class TCPreprocess():
    def __init__(self, hierarchy: Dict[str, str], conversion: Dict[str, str], target_col: str):
        """
        Init of the preprocessing class for TC

        Parameters
        ----------
        hierarchy : Dict[str, str]
            The hierarchy dictionary from the configuration file 
        conversion : Dict[str, str]
            The conversion dictionary from the configuration file
        target_col : str
            The target col from the configuration file
            (e.g. id_teleconsulto for removing duplicates)
        """
        self.hierarchy = hierarchy
        self.conversion = conversion
        self.target_col = target_col

    def fit(self, X: pd.DataFrame = None):
        """
        Fit method of TCPreprocess

        Parameters
        ----------
        X : pd.DataFrame, optional
            The pandas dataframe to fit, by default None

        Returns
        -------
        Self
        """
        return self

    def transform(self, X: pd.DataFrame) -> pd.DataFrame:
        """
        Transform method which applies the pipeline of transformations for TC

        Parameters
        ----------
        X : pd.DataFrame
            The pandas dataframe to transform

        Returns
        -------
        pd.DataFrame
            The transformed dataframe
        """
        logger.info(message='Preparing Dataset for Model Specific Preprocessing.')
        X = clean_df_columns(df = X, hierarchy=self.hierarchy)
        X = column_to_int(df=X, hierarchy=self.hierarchy, conversion=self.conversion)
        X = map_columns(df=X, hierarchy=self.hierarchy, conversion=self.conversion)
        X = filter_target_col(df=X, target_col=self.target_col)
        return X
    

class TVPreprocess():
    def __init__(self, hierarchy, conversion):
        """
        Init of the preprocessing class for TC

        Parameters
        ----------
        hierarchy : Dict[str, str]
            The hierarchy dictionary from the configuration file 
        conversion : Dict[str, str]
            The conversion dictionary from the configuration file
        """
        self.hierarchy = hierarchy
        self.conversion = conversion

    def fit(self, X: pd.DataFrame =None):
        """
        Fit method of TCPreprocess

        Parameters
        ----------
        X : pd.DataFrame, optional
            The pandas dataframe to fit, by default None

        Returns
        -------
        Self
        """
        return self

    def transform(self, X: pd.DataFrame):
        logger.info(message='Preparing Dataset for Model Specific Preprocessing.')
        X = clean_df_columns(df = X, hierarchy=self.hierarchy)
        X = column_to_int(df=X, hierarchy=self.hierarchy, conversion=self.conversion)
        X = map_columns(df=X, hierarchy=self.hierarchy, conversion=self.conversion)
        return X
        

class TMPreprocess():
    def __init__(self, hierarchy, conversion):
        """
        Init of the preprocessing class for TC

        Parameters
        ----------
        hierarchy : Dict[str, str]
            The hierarchy dictionary from the configuration file 
        conversion : Dict[str, str]
            The conversion dictionary from the configuration file
        """
        self.hierarchy = hierarchy
        self.conversion = conversion

    def fit(self, X: pd.DataFrame =None):
        """
        Fit method of TCPreprocess

        Parameters
        ----------
        X : pd.DataFrame, optional
            The pandas dataframe to fit, by default None

        Returns
        -------
        Self
        """
        return self

    def transform(self, X: pd.DataFrame):
        logger.info(message='Preparing Dataset for Model Specific Preprocessing.')
        X = clean_df_columns(df = X, hierarchy=self.hierarchy)
        X = column_to_int(df=X, hierarchy=self.hierarchy, conversion=self.conversion)
        X = map_columns(df=X, hierarchy=self.hierarchy, conversion=self.conversion)
        return X
        

class TAPreprocess():
    def __init__(self, hierarchy, conversion):
        """
        Init of the preprocessing class for TC

        Parameters
        ----------
        hierarchy : Dict[str, str]
            The hierarchy dictionary from the configuration file 
        conversion : Dict[str, str]
            The conversion dictionary from the configuration file
        """
        self.hierarchy = hierarchy
        self.conversion = conversion

    def fit(self, X: pd.DataFrame =None):
        """
        Fit method of TCPreprocess

        Parameters
        ----------
        X : pd.DataFrame, optional
            The pandas dataframe to fit, by default None

        Returns
        -------
        Self
        """
        return self

    def transform(self, X: pd.DataFrame):
        """
        Transform method which applies the pipeline of transformations for TC

        Parameters
        ----------
        X : pd.DataFrame
            The pandas dataframe to transform

        Returns
        -------
        pd.DataFrame
            The transformed dataframe
        """
        logger.info(message='Preparing Dataset for Model Specific Preprocessing.')
        X = clean_df_columns(df = X, hierarchy=self.hierarchy)
        X = column_to_int(df=X, hierarchy=self.hierarchy, conversion=self.conversion)
        X = map_columns(df=X, hierarchy=self.hierarchy, conversion=self.conversion)
        return X
 