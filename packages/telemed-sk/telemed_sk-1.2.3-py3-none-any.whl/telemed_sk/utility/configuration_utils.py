from typing import Dict, Any, List, Tuple, Union
import tomli
import os
import pandas as pd

from .exceptions import InputTypeError
from .check_utils import check_not_in_iterable, check_not_isinstance, check_datatype_convertible
from .resources import get_module_and_function, log_exception, logger


def get_configuration(config_path : str, config_file: str) -> Dict[str, Any]:
    """Read the configurations set in the toml file in the config folder and returns them
    as a dictionary

    Parameters
    ----------
    config_path : str
        Specifies the config path where the .toml configurations resides
    config_file : str
        Specifies the config file to read

    Returns
    -------
    Dict[str, Any]
        Dictionary containing the config file

    Raises
    ------
    Exception
        Raise error if .conf file is not found
    """

    if config_file not in os.listdir(config_path):
        raise Exception(f"File {config_file} not found in {config_path} please double check that the filename is correct.")

    config = tomli.load(open(os.path.join(config_path, config_file), "rb"))
    return config

def config_reading(config_dict: Dict[str, str], config_dict_parsing: Dict[str, str]) -> Tuple[dict, dict]:
    """
    Function which reads the two configuration files

    Parameters
    ----------
    config_dict : Dict[str, str]
        Dictionary of the configuration file {'config_path': path to the config file, 'config_file': config filename}
    config_dict_parsing : Dict[str, str]
        Dictionary of the REFERENCE configuration file {'config_path': path to the config file, 'config_file': config filename}

    Returns
    -------
    Tuple[dict, dict]
        Two dictionaries representing the two configuration files
    """
    config_file = get_configuration(config_dict['config_path'], config_dict['config_file'])
    config_file_parsing = get_configuration(os.path.join(config_dict_parsing['config_path'], 'config_check'), config_dict_parsing['config_file'])
    return config_file, config_file_parsing

def config_key_parsing(config_file: Dict[str, Any], config_file_parsing: Dict[str, Any]):
    """
    The function checks if the config file and the REFERENCE config file have the same keys

    Parameters
    ----------
    config_file : Dict[str, Any]
        Dictionary of the config file
    config_file_parsing : Dict[str, Any]
        Dictionary of the REFERENCE config file
    """
    for key in config_file.keys():
        check_not_in_iterable(obj = key, iterable = config_file_parsing.keys(), func = get_module_and_function())

def check_usecases(usecase: str, possible_usecases: List[str]):
    """
    Check if the usecase is in the possible usecase

    Parameters
    ----------
    usecase : str
        The usecase to check
    possible_usecases : List[str]
        The possible usecases
    """
    check_not_isinstance(obj =  usecase, data_type = str, func = get_module_and_function())
    check_not_isinstance(obj =  possible_usecases, data_type = list, func = get_module_and_function())
    check_not_in_iterable(obj = usecase, iterable = possible_usecases, func = get_module_and_function())

def check_model(model_name: str, reference_model_name: str, apply_reconciler: str, reference_apply_reconciler: List[str]):
    """
    Chek model_name and apply_reconciler constistency

    Parameters
    ----------
    model_name : str
        Model name to check
    reference_model_name : str
        Reference model name which MUST be equal to model_name
    apply_reconciler : str
        String value which specifies the reconcile method to apply
    reference_apply_reconciler : List[str]
        List of possible values for apply_reconciler
    """
    check_not_isinstance(obj =  model_name, data_type = str, func = get_module_and_function())
    check_not_isinstance(obj =  reference_model_name, data_type = str, func = get_module_and_function())
    check_not_isinstance(obj =  apply_reconciler, data_type = str, func = get_module_and_function())
    check_not_in_iterable(obj = apply_reconciler, iterable = reference_apply_reconciler, func = get_module_and_function())
    if model_name != reference_model_name:
        raise InputTypeError(func = get_module_and_function(), 
                             message=f"model_name {model_name} MUST be equal to reference_model_name {reference_model_name}")

def check_hyperparameters(hyperparameters: List[str], possible_hyperparameters: List[str]):
    """
    The function checks if the hyperparameters specified are allowed

    Parameters
    ----------
    hyperparameters : List[str]
        The hyperparameters specified
    possible_hyperparameters : List[str]
        The allowed hyperparameters
    """
    check_not_isinstance(obj = hyperparameters, data_type = list, func = get_module_and_function())
    check_not_isinstance(obj = possible_hyperparameters, data_type = list, func = get_module_and_function()) 
    for hyperparam in hyperparameters:
        check_not_isinstance(obj = hyperparam, data_type = str, func = get_module_and_function())
        check_not_in_iterable(obj = hyperparam, iterable = possible_hyperparameters, func = get_module_and_function())

def check_hyperparameters_value(hyperparameters: Dict[str, Union[List[str], Dict[str, Union[int, float]]]]):
    """
    The function checks if the hyperparameters are Lists or Dicts

    Parameters
    ----------
    hyperparameters : Dict[str, Union[List[str], Dict[str, Union[int, float]]]]
        The hyperparameters dict specified in the config file

    Raises
    ------
    InputTypeError
        If the value of the hyperparameters are neither Lists nor Dicts
    """
    for hyperparam_val in hyperparameters.values():
        if not isinstance(hyperparam_val, dict) and not isinstance(hyperparam_val, list):
            raise InputTypeError(func = get_module_and_function(), 
                                 message='The hyperparameters to specify must be List or Dict')

def check_missing_data_strategy(missing_data_strategy:  Union[str,int,dict], possible_strategies: List[str], 
                                possible_dictionary_keys: List[str], possible_interpolation_methods: List[str]):
    """
    The function checks the missing data strategy

    Parameters
    ----------
    missing_data_strategy : Union[str,int,dict]
        Missing data strategy to check
    possible_strategies : List[str]
        Possible strategies if the missing_data_strategy is a string
    possible_dictionary_keys : List[str]
        Possible keys if the missing_data_strategy is a dict
    possible_interpolation_methods : List[str]
        Possible interpolation methods

    Raises
    ------
    TypeError
        If missing_data_strategy is not Union[str,int,dict]
    """
    if isinstance(missing_data_strategy, str):    
        check_not_in_iterable(obj = missing_data_strategy, iterable = possible_strategies, func = get_module_and_function())
    elif isinstance(missing_data_strategy, int):
        pass
        if missing_data_strategy != 0:
            raise TypeError('Invalid value for missing_data_strategy. It must be equal to 0')
    elif isinstance(missing_data_strategy, dict):
        for key, _ in missing_data_strategy.items():
            check_not_in_iterable(obj = key, iterable = possible_dictionary_keys, func = get_module_and_function())
        check_not_in_iterable(obj = missing_data_strategy['interpolation'], iterable = possible_interpolation_methods, func = get_module_and_function())
        check_not_isinstance(obj = missing_data_strategy['order'], data_type= int, func = get_module_and_function())
    else:
        raise TypeError("Invalid type for 'missing_data_strategy' in 'configuration_utils.check_missing_data_strategy'. It must be str or int or dict")

def check_time_granularity(time_granularity: str, possible_time_granularities: List[str]):
    """
    The function checks if time_granularity is in the possible_time_granularities

    Parameters
    ----------
    time_granularity : str
        Time granularity
    possible_time_granularities : List[str]
        List of possible time granularities
    """
    check_not_isinstance(obj = time_granularity, data_type = str, func = get_module_and_function())
    check_not_isinstance(obj = possible_time_granularities, data_type = list, func = get_module_and_function()) 
    check_not_in_iterable(obj = time_granularity, iterable = possible_time_granularities, func = get_module_and_function())

def check_preprocessing(target_col: str, date_col: str):
    """
    Check if the target_col and the date_col are strings

    Parameters
    ----------
    target_col : str
        target_col in the configuration file
    date_col : str
        date_col in the configuration file
    """
    check_not_isinstance(obj = target_col, data_type = str, func= get_module_and_function())
    check_not_isinstance(obj = date_col, data_type = str, func= get_module_and_function())

def check_split_forecasting(time_granularity: str, validation_obs: int, test_obs: int,
                            num_forecast_periods: int, start_date: str):
    """
    The function checks the consistency of the split (Train, Validation, Test) and the num_forecast_periods

    Parameters
    ----------
    time_granularity : str
        Time_granularity
    validation_obs : int
        Number of observations in the validation set
    test_obs : int
        Number of observations in the test set
    num_forecast_periods : int
        Number of observations for the future
    start_date : str
        String representing the start date for future forecasting
    """
    check_not_isinstance(obj = time_granularity, data_type = str, func = get_module_and_function())
    check_not_isinstance(obj = validation_obs, data_type = int, func = get_module_and_function())
    check_not_isinstance(obj = test_obs, data_type = int, func = get_module_and_function())
    check_not_isinstance(obj = num_forecast_periods, data_type = int, func = get_module_and_function())
    check_not_isinstance(obj = start_date, data_type = str, func = get_module_and_function())
    check_datatype_convertible(obj = start_date, data_type_conversion = pd.to_datetime, func = get_module_and_function())
    
    # Check val - test - future consistency
    if validation_obs == 0 or test_obs == 0 or num_forecast_periods == 0:
        raise InputTypeError(func = get_module_and_function(), 
                             message=f"Validation size {validation_obs}, Test size {test_obs} and Future forecast periods {num_forecast_periods} MUST be greater than 0.")
    
    if test_obs >= validation_obs or num_forecast_periods >= validation_obs:
        raise InputTypeError(func = get_module_and_function(), 
                             message=f'Validation size {validation_obs} MUST be greater than Test size {test_obs} and Future forecast periods {num_forecast_periods}')

    # Check proportion consistency val - test - future depending on the time granularity
    if time_granularity == 'M':
        difference = 3
    if time_granularity == 'W': 
        difference = 4
    if time_granularity == 'D':
        difference = 7
    if time_granularity == 'H':
        difference = 24
    if (validation_obs - test_obs) < difference or (validation_obs - num_forecast_periods) < difference:
        raise InputTypeError(func = get_module_and_function(), 
                             message=f'Validation size {validation_obs} MUST be greater than Test size {test_obs} and Future forecast periods {num_forecast_periods} ' + 
                             f'of at least {difference} for time granularity {time_granularity}')

def check_hierarchy(hierarchy: Dict[str, str]):
    """
    The function checks if the values of the hierarhcy are strings

    Parameters
    ----------
    hierarchy : Dict[str, str]
        The heirarchy dictionary from the configuration file
    """
    for hier_val in hierarchy.values():
        check_not_isinstance(obj = hier_val, data_type = str, func= get_module_and_function())

def check_conversion(conversion: Dict[str, str]):
    """
        The function checks if the values of the conversion are strings

    Parameters
    ----------
    conversion : Dict[str, str]
        The conversion dictionary from the configuration file
    """
    for conversion_val in conversion.values():
        check_not_isinstance(obj = conversion_val, data_type = str, func= get_module_and_function())

# PARSING THE CONFIGURATION FILE
@log_exception(logger)
def config_parsing(config_path: str, 
                   config_filename: str, config_filename_parsing: str):
    """
    The function aggregates all the checks specified in the functions above

    Parameters
    ----------
    config_path : str
        The path to the folder which contains the configuration files
    config_filename : str
        The filename of the configuration file
    config_filename_parsing : str
        The filename of the REFERENCE configuration file
    """
    check_not_isinstance(obj = config_path, data_type = str, func = get_module_and_function)
    check_not_isinstance(obj = config_filename, data_type = str, func = get_module_and_function)
    check_not_isinstance(obj = config_filename_parsing, data_type = str, func = get_module_and_function)

    config_file, config_file_parsing = config_reading(config_dict = {'config_path': config_path, 'config_file': config_filename}, 
                                                      config_dict_parsing = {'config_path': config_path, 'config_file': config_filename_parsing})  
    config_key_parsing(config_file = config_file, config_file_parsing = config_file_parsing)
    logger.info(message = 'Check Config Sections - OK')
    check_usecases(usecase = config_file['usecase']['usecase'], possible_usecases = config_file_parsing['usecase']['usecase'])
    logger.info(message = 'Check Config Section <usecase> - OK')
    check_model(model_name = config_file['model']['model_name'], reference_model_name = config_file_parsing['model']['model_name'], 
                apply_reconciler = config_file['model']['apply_reconciler'], reference_apply_reconciler = config_file_parsing['model']['apply_reconciler'] )
    logger.info(message = 'Check Config Section <model> - OK')
    check_hyperparameters(hyperparameters = list(config_file['hyperparameters'].keys()), possible_hyperparameters = config_file_parsing['hyperparameters']['possible_hyperparameters'])
    check_hyperparameters_value(hyperparameters = config_file['hyperparameters'])
    logger.info(message = 'Check Config Section <hyperparameters> - OK')
    check_missing_data_strategy(missing_data_strategy = config_file['preprocessing']['missing_data_strategy'], possible_strategies = config_file_parsing['preprocessing']['missing_data_strategy_strings'],
                                possible_dictionary_keys = config_file_parsing['preprocessing']['missing_data_strategy_dict_keys'], possible_interpolation_methods = config_file_parsing['preprocessing']['allowed_interpolation_methods'])
    check_time_granularity(time_granularity = config_file['preprocessing']['time_granularity'], possible_time_granularities = config_file_parsing['preprocessing']['time_granularity'])
    check_preprocessing(target_col = config_file['preprocessing']['target_col'], date_col = config_file['preprocessing']['date_col'])
    logger.info(message = 'Check Config Section <Preprocessing> - OK')
    check_split_forecasting(time_granularity = config_file['preprocessing']['time_granularity'], validation_obs = config_file['validation_test_split']['validation_obs'],
                            test_obs = config_file['validation_test_split']['test_obs'], num_forecast_periods = config_file['forecasting']['num_forecast_periods'],
                            start_date =  config_file['forecasting']['start_date'])
    logger.info(message = 'Check Config Section <Forecasting - Preprocessig> - OK')