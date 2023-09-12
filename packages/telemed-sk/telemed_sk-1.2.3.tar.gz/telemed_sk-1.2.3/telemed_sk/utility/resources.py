from __future__ import annotations

import os
import sys
from typing import Any, Dict, Type
import inspect
import tomli
import traceback


from telemedbasics.configuration.global_var_logger import logger, AWSLoggingHandler

def get_configuration(name: str, config_path : str, config_file: str) -> Dict[str, Any]:
    """Read the configurations set in the properties.toml file in the config folder and returns them
    as a dictionary

    Parameters
    ----------
    name : str
        Section to be 
    config_path : str
        Specifies the config path where the .toml configurations resides
    config_file : str
        Specifies the config file to read

    Returns
    -------
    Dict[str, Any]
        Dictionary containing the properties read

    Raises
    ------
    Exception
        Raise error if .conf file is not found
    """

    if config_file not in os.listdir(config_path):
        raise Exception(
            f"File {config_file} not found in {config_path} please double check that the filename is correct."
        )

    config = tomli.load(open(os.path.join(config_path, config_file), "rb"))
    # Read from the specified file, the specified section
    if name in config:
        return config[name]
    else:
        raise Exception("System " + name + " not found in .conf file")

def log_exception(logger: Type[AWSLoggingHandler] =None):
    """
    A decorator that wraps the passed in function and logs
    exceptions should one occur.

    Parameters
    ----------
    logger : AWSLoggingHandler, default: None
        The logger to use, if None error and traceback will be printed anyway.
    """

    def decorator(func):
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except :
                # log the exception
                err = "There was an Error in "
                err += func.__name__ + f' -> {traceback.format_exc()}'

                if logger:
                    logger.error(message = err)
                sys.exit()

        return wrapper

    return decorator

def get_module_and_function() -> str:
    """Function that returns a string <module name>.<function> where
    this function is called.

    Returns
    -------
    str
        String of <module name>.<function>
    """
    frame = inspect.currentframe().f_back
    module = inspect.getmodule(frame)
    function_name = frame.f_code.co_name
    return f"{module.__name__}.{function_name}"
