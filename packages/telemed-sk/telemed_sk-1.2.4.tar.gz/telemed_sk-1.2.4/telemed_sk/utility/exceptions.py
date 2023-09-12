import pandas as pd
from tabulate import tabulate

class InputTypeError(Exception):
    """Exception raised for errors in the function inputs."""

    def __init__(self, func : str, message : str = 'Wrong input types have been given to the function.'):
        """
        Parameters
        ----------
        func : str
            Function which is throwing the error
        message : str, optional
            Message to show 
        """
        self.message = f'{func} encountered an error: {message}'
        super().__init__(self.message)

class ColumnNotFound(Exception):
    """Exception raised when a column is not found inside the data"""
    def __init__(self, func : str, column : str, data : pd.DataFrame, message : str = 'The following column is not in the data columns list -> '):
        """
        Parameters
        ----------
        func : str
            Function which is throwing the error
        column : str
            Column not found in the data columns list
        data : pd.DataFrame
            Pandas DataFrame that thrown the error
        message : str, optional
            Message to show 
        """
        self.message = f"{func} encountered an error: {message}{column}\n\n{tabulate(data.head(4), headers='keys', tablefmt='psql')}"
        super().__init__(self.message)

class ConversionError(Exception):
    """Exception raised when two objects have not the same values"""
    def __init__(self, func : str, message : str = 'The object cannot be converted'):
        """
        Parameters
        ----------
        func : str
            Function which is throwing the error
        message : str, optional
            Message to show 
        """
        self.message = f'{func} encountered an error: {message}'
        super().__init__(self.message)