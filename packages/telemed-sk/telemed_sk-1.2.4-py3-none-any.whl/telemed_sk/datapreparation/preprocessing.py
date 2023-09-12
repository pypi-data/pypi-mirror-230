from typing import Tuple, Dict, List
import pandas as pd
from ..utility.resources import log_exception, logger
from .uc_preproc import TCPreprocess, TVPreprocess, TMPreprocess, TAPreprocess
from .model_preproc import ProphetPreprocess


# Since this class wraps other classes based on if-else statements, the typehint could not coincide with the real output type
# When we implement the other trasnformations for the other usecases, we need to check it
@log_exception(logger)
class PreprocessingClass():
    def __init__(self, usecase: str, model: str, **kwargs):
        """ Pass all the parameters that can be set as explicit keyword
        arguments.
        
        Parameters
        ----------
        usecase : str
            Parameter identifying usecase into account
        model : str
            Parameter identifying model to use
            
        """
        if usecase.lower() == 'teleconsulto':
            self.uc_preproc = TCPreprocess(hierarchy=kwargs['hierarchy'], 
                                           conversion=kwargs['conversion'], 
                                           target_col=kwargs['target_col'])
        elif usecase.lower() == 'televisita':
            self.uc_preproc = TVPreprocess(hierarchy=kwargs['hierarchy'], 
                                           conversion=kwargs['conversion'])
        elif usecase.lower() == 'telemonitoraggio':
            self.uc_preproc = TMPreprocess(hierarchy=kwargs['hierarchy'], 
                                           conversion=kwargs['conversion'])
        elif usecase.lower() == 'teleassistenza':
            self.uc_preproc = TAPreprocess(hierarchy=kwargs['hierarchy'], 
                                           conversion=kwargs['conversion'])
        else:
            raise Exception(f'Usecase "{usecase}" not managed by the Preprocessing procedures.')
        

        if model.lower() == 'prophet':
            self.model_preproc = ProphetPreprocess(hierarchy=kwargs['hierarchy'],
                                                   time_granularity=kwargs['time_granularity'],
                                                   date_col=kwargs['date_col'],
                                                   missing_data_strategy=kwargs['missing_data_strategy'])
        else:
            raise Exception(f'Model "{model}" not managed by the Preprocessing procedures.')
        
        logger.info(message = f'Instantiated the Preprocessing class for usecase: {usecase} and model: {model}.')
    
    def fit(self):
        """
        Fit method of PreprocessingClass
        """
        self.uc_preproc.fit()
        self.model_preproc.fit()

    def transform(self, X: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame, Dict[str, List[str]]]:
        """
        Transform method which applies the pipeline of transformations for UC and Model 

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
        X_uc = self.uc_preproc.transform(X)
        X_model = self.model_preproc.transform(X_uc)

        return X_model

    def fit_transform(self, X: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame, Dict[str, List[str]]]:
        """
        fit_transform method which applies the pipeline of transformations for UC and Model 

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
        X_uc = self.uc_preproc.fit().transform(X)
        X_model = self.model_preproc.fit().transform(X_uc)
        
        return X_model