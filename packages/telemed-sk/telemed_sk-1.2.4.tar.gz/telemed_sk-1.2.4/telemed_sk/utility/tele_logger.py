import sys
import os
import logging
from logging import INFO
from time import localtime, strftime
from typing import Dict

class Logger(logging.getLoggerClass()):
    """.. deprecated:: 0.2.0
    Deprecated since version 0.2.0 in favor of using the library telemedbasics.
    
    Logger class used to manage the log routing and writes logs on different files."""

    def __init__(self, format: str = "%(asctime)s | %(levelname)s | %(message)s", level: int = INFO):
        """Logger initialization, sets default logging format and log level 

        Parameters
        ----------
        format : str, optional
            Log message format, by default "%(asctime)s | %(levelname)s | %(message)s"
        level : int, optional
            Log level, by default INFO
        """

        self.logger = logging.getLogger("logger")
        self.important_logger = logging.getLogger("important_logger")

        # Initial construct.
        self.format = format
        self.level = level
        self.name = None
        self.log_path = None

    def initialize_logger(self, log_path : str, name: str):
        """Initialize the logging session by creating the logging files 
        <name>_<YYYYMMDD>.log and <name>_<YYYYMMDD>_verbose.log . If a new name 
        is passed then a new log session and files are created aswell

        Parameters
        ----------
        log_path : str
            Path where Logging will save the logs
        name : str
            Logging session name
        """
        self.name = name
        self.logging_folder = log_path

        # Logger configuration.
        self.console_formatter = logging.Formatter(self.format)
        self.console_logger = logging.StreamHandler(sys.stdout)
        self.console_logger.setFormatter(self.console_formatter)

        # Complete logging config.
        self.logger.setLevel(self.level)
        self.important_logger.setLevel(self.level)

        # Logger configuration.
        self.file_formatter = logging.Formatter(self.format)

        # check if folder exists
        if not os.path.exists(self.logging_folder):
            os.makedirs(self.logging_folder)
        self.file_logger = logging.FileHandler(os.path.join(
            self.logging_folder, self.name + "_verbose_" + strftime("%Y%m%d", localtime()) + ".log"))
        self.file_logger.setFormatter(self.file_formatter)
        self.important_file_logger = logging.FileHandler(
            os.path.join(self.logging_folder, self.name + "_" + strftime("%Y%m%d", localtime()) + ".log"))
        self.important_file_logger.setFormatter(self.file_formatter)

        # Complete logging config.
        handler_list = []
        for handler in self.logger.handlers:
            try:
                handler_list.append(os.path.split(handler.baseFilename)[1])

            except AttributeError:
                pass
        
        if self.name + "_verbose_" + strftime("%Y%m%d", localtime()) + ".log" not in handler_list:
            self.logger.addHandler(self.console_logger)
            self.logger.addHandler(self.file_logger)
        if self.name + "_" + strftime("%Y%m%d", localtime()) + ".log" not in handler_list:
            self.important_logger.addHandler(self.important_file_logger)

    def info(self, msg: str, extra: Dict = None, important: bool = False):
        """Generates a INFO log level row

        Parameters
        ----------
        msg : str
            Message associated to the log line
        extra : Dict, optional
            Dictionary containing the missing FORMAT attributes 
            needed to generate the log message, by default None
        important : bool, optional
           Specify wether to write or not on main .log file , by default False
        """
        self.logger.info(msg, extra=extra)
        if important:
            self.important_logger.info(msg, extra=extra)

    def error(self, msg: str, extra: Dict = None):
        """Generates an ERROR log level row

        Parameters
        ----------
        msg : str
            Message associated to the log line
        extra : Dict, optional
            Dictionary containing the missing FORMAT attributes 
            needed to generate the log message, by default None
        """
        self.logger.error(msg, extra=extra)
        self.important_logger.error(msg, extra=extra)

    def exception(self, msg: str, extra: Dict = None):
        """Generates an EXCEPTION log level row

        Parameters
        ----------
        msg : str
            Message associated to the log line
        extra : Dict, optional
            Dictionary containing the missing FORMAT attributes 
            needed to generate the log message, by default None
        """
        self.logger.exception(msg, extra=extra)
        self.important_logger.exception(msg, extra=extra)

    def warning(self, msg: str, extra: Dict = None):
        """Generates a WARNING log level row

        Parameters
        ----------
        msg : str
            Message associated to the log line
        extra : Dict, optional
            Dictionary containing the missing FORMAT attributes 
            needed to generate the log message, by default None
        """
        self.logger.warning(msg, extra=extra)

    def debug(self, msg: str, extra: Dict = None):
        """Generates a DEBUG log level row

        Parameters
        ----------
        msg : str
            Message associated to the log line
        extra : Dict, optional
            Dictionary containing the missing FORMAT attributes 
            needed to generate the log message, by default None
        """
        self.logger.debug(msg, extra=extra)

    # def profile_memory_usage(self):
    #     memory_usage = dict(psutil.virtual_memory()._asdict())
    #     memory_usage_log = str(
    #         {key: round(el / (1024 ** 3), 3) if key != "percent" else el for key, el in memory_usage.items()})
    #     self.logger.info("Memory usage: " + memory_usage_log)


logger = Logger()
