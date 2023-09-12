import os
from typing import Any

import geopandas as gpd
import pandas as pd
from typing_extensions import Self

from ..utility.exceptions import InputTypeError
from ..utility.resources import log_exception, logger

class DataHandler:
    """
    .. deprecated:: 0.2.0
    Deprecated since version 0.2.0 in favor of using the library telemedbasics.
    """
    def __init__(self, data_folder : str):
        """
        Class which will handle the read and write of .parquet data

        Parameters
        ----------
        data_folder : str
            Main folder where to find the data, if given as a parameter
        """
        if type(data_folder) != str:
            raise InputTypeError('DataHandler')

        self.data_folder = data_folder

    @log_exception(logger)
    def read(self, filename: str, folder: str = "input", in_attr: bool = False, **kwargs: Any) -> pd.DataFrame:
        """
        Read datafile given a folder from <data_folder>/<folder> and the filename. Supported extensions are
        csv and parquet. See: https://pandas.pydata.org/docs/reference/api/pandas.read_parquet.html
        and https://pandas.pydata.org/docs/reference/api/pandas.read_csv.html for more info
        regarding the additional parameters

        Parameters
        ----------
        filename : str
            File name to read
        folder : str, optional
            Folder where the file resides starting from <data_folder>, the path to the default folder will be
            /../../data/<folder>, by default 'input'
        in_attr : bool, optional
            Whether to save the dataset in the Class attributes or not, by default False

        Returns
        -------
        pd.DataFrame
            Pandas datafreame read

        Raises
        ------
        Exception
            Returns an error if the file estension is not supported
        """

        if type(filename) != str or type(folder) != str or type(in_attr) != bool:
            raise InputTypeError('DataHandler.read')

        datatype = os.path.splitext(filename)[-1].lower()
        supp_datatype = [".parquet", ".csv"]

        if datatype not in supp_datatype:
            raise Exception(
                f'File extension "{datatype}" not supported. Supported extensions are {supp_datatype}'
            )

        logger.info(message=f"START loading {os.path.join(self.data_folder, folder, filename)}")

        # path = os.path.dirname(os.path.abspath(__file__))
        path = os.path.join(self.data_folder, folder, filename)

        if datatype == ".csv":
            df = pd.read_csv(filepath_or_buffer=path, **kwargs)

        elif datatype == ".parquet":
            if "engine" not in kwargs.keys():
                kwargs["engine"] = "fastparquet"

            df = pd.read_parquet(path=path, **kwargs)

        logger.info(message=f"DONE loading {os.path.join(self.data_folder, folder, filename)}")
        
        if in_attr:
            self.df = df

        return df

    @log_exception(logger)
    def read_geodataframe(self, filename: str, folder: str = "input", in_attr: bool = False, **kwargs: Any) -> gpd.GeoDataFrame:
        """
        Read datafile given a folder from /../../data/<folder> and the filename. Supported extensions are
        parquet. See: https://geopandas.org/en/stable/docs/reference/api/geopandas.read_parquet.html
        for more info regarding the additional parameters

        Parameters
        ----------
        filename : str
            File name to read
        folder : str, optional
            Folder where the file resides starting from <data_folder>, the path to the default folder will be
            /../../data/<folder>, by default 'input'
        in_attr : bool, optional
            Whether to save the dataset in the Class attributes or not, by default False

        Returns
        -------
        pd.DataFrame
            Pandas datafreame read

        Raises
        ------
        Exception
            Raises an error if the file estension is not supported
        """

        if type(filename) != str or type(folder) != str or type(in_attr) != bool:
            raise InputTypeError('DataHandler.read_geodataframe')
        
        datatype = os.path.splitext(filename)[-1].lower()
        supp_datatype = [".parquet"]

        if datatype not in supp_datatype:
            raise Exception(
                f'File extension "{datatype}" not supported. Supported extensions are {supp_datatype}'
            )

        logger.info(message=f"START loading {os.path.join(self.data_folder, folder, filename)}")

        path = os.path.join(self.data_folder, folder, filename)
        gdf = gpd.read_parquet(path=path, **kwargs)

        logger.info(message=f"DONE loading {os.path.join(self.data_folder, folder, filename)}")

        if in_attr:
            self.gdf = gdf

        return gdf

    @log_exception(logger)
    def write(
        self, data: pd.DataFrame, filename: str, folder: str = "output", **kwargs: Any
    ) -> None:
        """
        Writes a pandas DataFrame into the selected folder. Supported extensions are
        csv and parquet. See: https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.to_parquet.html
        and https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.to_csv.html for more info
        regarding the additional parameters

        Parameters
        ----------
        data : pd.DataFrame
            Pandas DataFrame to be written
        filename : str
            Filename to be writter. It must contain the correct extension, currently supported
            extensions are csv and parquet
        folder : str, optional
            Folder where the file will be written into starting from <data_folder>, the path to the default folder will be
            /../../data/<folder>, by default 'output'
        """
        if  type(data) != pd.DataFrame or type(filename) != str or type(folder) != str:
            raise InputTypeError('DataHandler.write')
        
        datatype = os.path.splitext(filename)[-1].lower()
        supp_datatype = [".parquet", ".csv"]

        if datatype not in supp_datatype:
            raise Exception(
                f'File extension "{datatype}" not supported. Supported extensions are {supp_datatype}'
            )
        if not os.path.isdir(os.path.join(self.data_folder, folder)):
            raise Exception(
                f'Can not write "{filename}" because folder "{os.path.join(self.data_folder, folder)}". Please create it.'
            )

        path = os.path.join(self.data_folder, folder, filename)

        logger.info(message=f"START writing {os.path.join(self.data_folder, folder, filename)}")

        if datatype == ".csv":
            if "infex" not in kwargs.keys():
                kwargs["index"] = False

            data.to_csv(path_or_buf=path, **kwargs)

        elif datatype == ".parquet":
            if "engine" not in kwargs.keys():
                kwargs["engine"] = "fastparquet"

            data.to_parquet(path=path, **kwargs)

        logger.info(message=f"DONE writing {os.path.join(self.data_folder, folder, filename)}")
