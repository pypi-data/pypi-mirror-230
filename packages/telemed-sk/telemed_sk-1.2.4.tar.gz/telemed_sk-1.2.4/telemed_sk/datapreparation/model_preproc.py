from typing import Any, Dict, Tuple, Union, List
import pandas as pd

from .utils import datepart, divide_by_father, generate_time_series, get_hierarchy_column, get_lagged_column, missing_data_imputation, completing_calendar
from ..utility.resources import logger

class ProphetPreprocess():
    def __init__(self, hierarchy: Dict[str, str], time_granularity: str, 
                 date_col: str, missing_data_strategy: Union[str, int, Dict[str, Union[str, int]]]):
        """
        Init of the preprocessing class for the prophet model

        Parameters
        ----------
        hierarchy : Dict[str, str]
            The hierarchy dictionary from the configuration file 
        time_granularity : str
            The time granularity to aggregate <date_col>
        date_col : str
            The date col to aggregate with <time_granularity>
        missing_data_strategy : Union[str, int, Dict[str, Union[str, int]]]
            The missing data strategy specified in the configuration file
        """
        self.hierarchy = hierarchy
        self.time_granularity = time_granularity
        self.date_col = date_col
        self.missing_data_strategy = missing_data_strategy

    def fit(self):
        """
        Fit method of ProphetPreprocess

        Returns
        -------
        Self
        """
        return self
    
    def transform(self, X: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame, Dict[str, List[str]]]:
        """
        Transform method which applies the pipeline of transformations for Prophet

        Parameters
        ----------
        X : pd.DataFrame
            The dataframe to transform

        Returns
        -------
        Tuple[pd.DataFrame, pd.DataFrame, Dict[str, List[str]]]
            Tuple containing (X, S, tags)
            - X: The processed dataframe after preprocessing
            - S: Dataframe of binary values resulting from the aggregation (incidence matrix of undirected graph)
            - tags: Dictionary containing the information about the hierarchies
        """
        logger.info(message='Preparing Dataset for Prophet Modelling.')
        X, S, tags = generate_time_series(df = X, date_col = self.date_col, 
                                          time_granularity = self.time_granularity, hierarchy = self.hierarchy)
        X = completing_calendar(df = X, time_granularity = self.time_granularity)
        X = missing_data_imputation(missing_data_strategy = self.missing_data_strategy, df = X)

        return X, S, tags

class PreprocessBoosting():
    def __init__(self, datepart: bool = True, preds: bool = True, target: bool = True, conf_inter: bool = True,
                 lags: list = None, n_hier: int = None,
                 father_preds: bool = False, sons_preds: bool = False, father_target: bool = False,
                 sons_target: bool = False, divide_target: bool = False):

        """Preprocessing class to obtain dataset input for boosting models.

        Parameters
        ----------
        datepart : bool,
            if True adds date information to dataset
        preds : bool
            if True adds predictions to dataset
        target : bool,
            if True adds Target value to dataset
        conf_inter : bool,
            if True adds confidence intervals to dataset
        lags : list
            if True lags the predictions columns and adds them to the dataset
        n_hier : int
            level of hierarchy considered, if None considers all levels
        father_preds : bool
            if True adds father column of the predictions of the hierarchy level (selected by n_hier) to dataset
        sons_preds : bool
            if True adds all sons of the predictions of the hierarchy level (selected by n_hier) to dataset
        father_target : bool
            if True adds father of target of the hierarchy level (selected by n_hier) to dataset
        sons_target : bool
            if True adds all sons of target of the hierarchy level (selected by n_hier) to dataset
        divide_target : bool
            if True divide all target sons by target father
        """
        self.datepart = datepart
        self.preds = preds
        self.target = target
        self.conf_inter = conf_inter
        self.lags = lags
        self.n_hier = n_hier
        self.father_preds = father_preds
        self.sons_preds = sons_preds
        self.father_target = father_target
        self.sons_target = sons_target
        self.divide_target = divide_target

    def transform(self, df_real: pd.DataFrame, df_preds: pd.DataFrame,
                  date_real: str = "ds", date_preds: str = "timestamp",
                  values_real: str = "y", values_preds: str = "pred_mean",
                  hier_real: str = "unique_id", hier_preds: str = "id_pred") -> pd.DataFrame:
        """Transforms a DataFrame

        Parameters
        ----------
        df_real : pd.DataFrame
            dataframe of target values
        df_preds : pd.DataFrame
            dataframe of prediction values
        date_real : str
            name of date column (target dataframe)
        date_preds : str
            name of date column (prediction dataframe)
        values_real : str
            name of value (y_true) column (target dataframe)
        values_preds : str
            name of value prediction (y_hat) column (prediction dataframe)
        hier_real : str
            name of hierarchy id column (target dataframe)
        hier_preds : str
            name of hierarchy id column (prediction dataframe)

        Returns
        -------
        list[pd.DataFrame]
            list of dataframes with extracted features for boosting models.
            Each dataframe in the list contains the features for each node in
            the considered hierarchy (specified in the init)
        """

        dfs = []

        # Add target cols
        if self.target:
            target_list = get_hierarchy_column(df_real,date_real,values_real,hier_real,self.n_hier,sons=self.sons_target,
                                               father=self.father_target,type_="Target")

            if self.divide_target:
                target_list = [divide_by_father(target) for target in target_list]

            dfs.append(target_list)

        # Add predictions cols
        if self.preds:
            preds_list = get_hierarchy_column(df_preds,date_preds,values_preds,hier_preds,self.n_hier,sons=self.sons_preds,
                                            father=self.father_preds,type_="Prophet")

            dfs.append(preds_list)

            if self.lags:
                dfs.append([get_lagged_column(pro,self.lags) for pro in preds_list])

        # Add confidence interval cols
        if self.conf_inter:
            dfs.append(get_hierarchy_column(df_preds,date_preds,"pi_lower_95",hier_preds,self.n_hier,sons=self.sons_preds,
                                            father=self.father_preds,type_="pi_lower"))
            dfs.append(get_hierarchy_column(df_preds,date_preds,"pi_upper_95",hier_preds,self.n_hier,sons=self.sons_preds,
                                            father=self.father_preds,type_="pi_upper"))

        if self.target or self.preds or self.conf_inter:
            dfs = [pd.concat([i[j] for i in dfs],axis=1) for j in range(0,len(dfs[0]))]


        if self.datepart:
            timestamp = pd.Series(df_real[date_real].unique()).sort_values()
            date_col = datepart(timestamp)
            dfs = [pd.concat([i,date_col],axis=1) for i in dfs]

            if dfs == []:
                dfs += [date_col]

        return dfs

    @staticmethod
    def get_X_y(df: pd.DataFrame, n_hier: int) -> tuple[pd.DataFrame, pd.DataFrame]:
        """
        Splits a DataFrame into feature columns and target columns.
        The feature columns are the ones not containing the word "Target",
        and the target columns are the ones containing "Target".

        Parameters
        ----------
        df : pd.DataFrame
            Input DataFrame containing all the columns.
        n_hier : int
            Hierarchy level to consider. It is used to determine the target columns.

        Returns
        -------
        Tuple[pd.DataFrame, pd.DataFrame]
            The feature DataFrame (X) and the target DataFrame (y).

        Examples
        --------
        >>> df = pd.DataFrame(...)
        >>> X, y = BoostingReconcileModel.get_X_y(df, n_hier=2)
        """
        target_cols = [c for c in df.columns if c.count("/") == n_hier - 1 and "Target" in c]
        feature_cols = [c for c in df.columns if "Target" not in c]

        X = df[feature_cols]
        y = df[target_cols]
        return X, y
