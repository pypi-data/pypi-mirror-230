#!/usr/bin/env python
# coding: utf-8
import threading
import logging
import logging.handlers
import os

system_logger = None

default_level = logging.INFO
default_format = '[%(name)s] %(asctime)s.%(msecs)03d %(levelname)s %(filename)s:%(lineno)s: %(message)s'
default_data_format = '%Y-%m-%d %H:%M:%S'
log_path = './logs/'


class Logger():
    _instance_lock = threading.Lock()

    def __new__(cls):
        """ 单例,防止调用生成更多 """
        if not hasattr(Logger, "_instance"):
            with Logger._instance_lock:
                if not hasattr(Logger, "_instance"):
                    if not os.path.exists(log_path):
                        os.makedirs(log_path)
                    Logger._instance = object.__new__(cls)
                    Logger.__global_logger(cls)
        return Logger._instance

    def __global_logger(cls):
        root_logger = logging.getLogger()
        root_logger.setLevel(default_level)

        formatter = logging.Formatter(
            default_format, datefmt=default_data_format)

        # Set up the logger to write into file
        if os.access(log_path, os.W_OK):
            time_file_handler = logging.handlers.TimedRotatingFileHandler(
                os.path.join(log_path, 'iw-algo-fx.log'),
                when='MIDNIGHT',
                backupCount=2
            )
            time_file_handler.suffix = '%Y-%m-%d.log'
            time_file_handler.setLevel(default_level)
            time_file_handler.setFormatter(formatter)
            root_logger.addHandler(time_file_handler)

        # Set up the logger to write into stdout
        consoleHandler = logging.StreamHandler()
        consoleHandler.setFormatter(formatter)
        root_logger.addHandler(consoleHandler)

    def __init__(self):
        self.framework_logger = self._get_logger(
            "Framework Log", level=default_level, filename="intelliw-onnx.log")

    @staticmethod
    def _get_logger(logger_type, level=logging.INFO, _format=None, filename=None):
        logger = logging.getLogger(logger_type)
        if logger.handlers:
            return logger

        _format = _format or default_format
        if filename is not None:
            if os.access(log_path, os.W_OK):
                time_file_handler = logging.handlers.TimedRotatingFileHandler(
                    os.path.join(log_path, filename),
                    when='MIDNIGHT',
                    backupCount=15
                )
                formatter = logging.Formatter(
                    _format, datefmt=default_data_format)
                time_file_handler.suffix = '%Y-%m-%d.log'
                time_file_handler.setLevel(level)
                time_file_handler.setFormatter(formatter)
                logger.addHandler(time_file_handler)
        return logger


def get_logger(name: str = "user", level: str = "INFO", format: str = None, filename: str = None):
    """get custom logs

    Args:
        name (str, optional): Logger unique name. Defaults to "user".
        level (str, optional): Logger level. Defaults to "INFO".
        format (str, optional): Format the specified record. Defaults to None.
        filename (str, optional): Save the name of the log file. Defaults to None.

    Returns:
        logger
    """
    return Logger()._get_logger(name, level, format, filename)
