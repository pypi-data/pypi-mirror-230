# -*- coding: utf-8 -*-
# pylint: disable=line-too-long

import logging
import os
import datetime
import shutil

LOG_FMT = "%(asctime)s.%(msecs)03d | %(processName)s | %(threadName)s | %(levelname)s | %(filename)s:%(lineno)d | %(message)s"
LOG_TIME_FMT = "%Y-%m-%d | %H:%M:%S"


class Logger:
    """Custom logger class."""

    def __init__(self, log_name="logger", log_file="", delete_old_log=True, file_log_level=logging.DEBUG, stream_log_level=logging.INFO):
        """Initialize the Logger.

        :param str log_name: Logger Name. (default: logger).
        :param str log_file: Log file path. (default: "").
        :param bool delete_old_log: Option for delete a old log files automatically. (default:True)
        :param int file_log_level: File log level (default: logging.DEBUG).
        :param int stream_log_level: Stream log level (default: logging.INFO).
        """
        self._logger = logging.getLogger(log_name)
        self._logger.root.setLevel(logging.DEBUG)
        _formatter = logging.Formatter(LOG_FMT, LOG_TIME_FMT)

        # Init StreamHandler
        _stream_handler = logging.StreamHandler()
        _stream_handler.setFormatter(_formatter)
        _stream_handler.setLevel(stream_log_level)
        self._logger.addHandler(_stream_handler)

        if log_file != "":
            self._backup_log(log_file)

            # Init FildHandler
            _file_handler = logging.FileHandler(filename=log_file, encoding='utf-8')
            _file_handler.setFormatter(_formatter)
            _file_handler.setLevel(file_log_level)
            self._logger.addHandler(_file_handler)

            if delete_old_log:
                self._delete_old_log(log_file)

    def _backup_log(self, log_file):
        """Backup the recent log file.

        :param str log_file: Log file path.
        """
        if os.path.exists(log_file) is True:
            _log_format = os.path.basename(log_file).split(".")[-1]
            _temp_name = os.path.basename(log_file).replace(f".{_log_format}", "")

            # Convert file's create time to string (timestamp -> datetime -> string)
            _time = datetime.datetime.fromtimestamp(os.path.getctime(log_file)).strftime("%Y%m%d_%H%M%S")

            _file_name = f"{_temp_name}_{_time}.{_log_format}"
            shutil.move(log_file, os.path.join(os.path.dirname(log_file), _file_name))

            # Clear log file
            open(log_file, 'w').close()

    def _delete_old_log(self, log_file):
        """Delete logs older than 14 days.

        :param str log_file: Log file path.
        """
        _log_directory = os.path.dirname(log_file)
        _files = os.listdir(_log_directory)
        _log_format = os.path.basename(log_file).split(".")[-1]

        _now_timestamp = datetime.datetime.now().timestamp()
        for _file in _files:
            if _log_format in _file:
                _path = os.path.join(_log_directory, _file)
                _modified_time = os.path.getmtime(_path)
                if datetime.timedelta(seconds=(_now_timestamp - _modified_time)) > datetime.timedelta(days=14):
                    os.remove(_path)
                    self._logger.debug(f"Delete Old log: {_path}")

    @property
    def logger(self):
        """Get logger.

        :return: logger.
        :rtype: logger.
        """
        return self._logger
