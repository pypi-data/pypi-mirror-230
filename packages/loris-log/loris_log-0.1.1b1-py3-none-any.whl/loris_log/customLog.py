"""
The CustomLogMessage that contains the custom log message
"""
import os
import inspect
import uuid
import sys
from .myException import InvalidMessageException,\
    EmptyParameterException,\
    NoneValueException,\
    InvalidAttributeException

# pylint: disable=W0212
class CustomLog:
    """
    Class to construct the log message (info, error, debug, fatal, log data).
    """

    @staticmethod
    def set_error_message(uu_id, name, message):
        """
        Set up the format of the error message.

        Args:
            uu_id (string): The generated uuid.
            name (string): The name of the application or API.
            message (array): The error message.

        Returns:
            string: The custom error message.
        """
        if uu_id is None or name is None or message is None:
            raise NoneValueException()

        if len(str(uu_id)) != 36 or len(str(name)) == 0:
            raise EmptyParameterException()

        if isinstance(uu_id, uuid.UUID) is False or\
            isinstance(name, str) is False or\
            isinstance(message, list) is False:
            raise InvalidAttributeException()

        try:
            error_message = f"[ERROR] [{str(uu_id)}] [{str(name)}] [{os.path.basename(inspect.stack()[1].filename)}] [line {sys._getframe().f_back.f_lineno}]: {' '.join(word for word in message)}"
            return error_message
        except TypeError as exc:
            raise InvalidMessageException() from exc

    @staticmethod
    def set_debug_message(uu_id, name, message):
        """
        Set up the format of the debug message

        Args:
            uu_id (string): The generated uuid.
            name (string): The name of the application/ API/ function/ feature.
            message (list): The error message.

        Returns:
            string: The custom debug message.
        """
        if uu_id is None or name is None or message is None:
            raise NoneValueException()

        if len(str(uu_id)) != 36 or len(str(name)) == 0:
            raise EmptyParameterException()

        if isinstance(uu_id, uuid.UUID) is False or\
            isinstance(name, str) is False or\
            isinstance(message, list) is False:
            raise InvalidAttributeException()

        try:
            debug_message = f"[DEBUG] [{uu_id}] [{name}] [{os.path.basename(inspect.stack()[1].filename)}] [line {sys._getframe().f_back.f_lineno}]: {' '.join(word for word in message)}"
            return debug_message
        except TypeError as exc:
            raise InvalidMessageException() from exc

    @staticmethod
    def set_fatal_message(uu_id, name, message):
        """
        Set up the format of the fatal message.

        Args:
            uu_id (string): The generated uuid.
            name (string): The name of the application/api/function/feature.
            message (list): The error message.

        Returns:
            string: The custom fatal message.
        """
        if uu_id is None or name is None or message is None:
            raise NoneValueException()

        if len(str(uu_id)) != 36 or len(str(name)) == 0:
            raise EmptyParameterException()

        if isinstance(uu_id, uuid.UUID) is False or\
            isinstance(name, str) is False or\
            isinstance(message, list) is False:
            raise InvalidAttributeException()

        try:
            fatal_message = f"[FATAL] [{uu_id}] [{name}] [{os.path.basename(inspect.stack()[1].filename)}] [line {sys._getframe().f_back.f_lineno}]: {' '.join(word for word in message)}"
            return fatal_message
        except TypeError as exc:
            raise InvalidMessageException() from exc

    @staticmethod
    def set_info_message(uu_id, name, message):
        """
        Set up the format of the info message.

        Args:
            uu_id (string): The generated uuid.
            name (string): The name of the application or API
            message (list): The error message.

        Returns:
            string: The custom info message.
        """
        if uu_id is None or name is None or message is None:
            raise NoneValueException()

        if len(str(uu_id)) != 36 or len(str(name)) == 0:
            raise EmptyParameterException()

        if isinstance(uu_id, uuid.UUID) is False or\
            isinstance(name, str) is False or\
            isinstance(message, list) is False:
            raise InvalidAttributeException()

        try:
            info_message = f"[INFO] [{uu_id}] [{name}] [{os.path.basename(inspect.stack()[1].filename)}] [line {sys._getframe().f_back.f_lineno}]: {' '.join(word for word in message)}"
            return info_message
        except TypeError as exc:
            raise InvalidMessageException() from exc

    @staticmethod
    def set_ftp_log_data(uu_id, starttime, endtime, result, groundtruth):
        """
        Set up the log message for the FTP system.

        Args:
            uuid (string): The generated uuid.
            starttime (string): the start time of an operation.
            endtime (string): the end time of an operation.
            result (string): the result of the embedded device/ system/ model etc.
            groundtruth (string): the result of the embedded device/ system/ model etc.

        Returns:
            string: a list of log data.
        """
        if uu_id is None or starttime is None\
           or endtime is None or result is None or\
           groundtruth is None:
            raise NoneValueException()

        if isinstance(uu_id, uuid.UUID) is False or\
            isinstance(starttime, str) is False or\
            isinstance(endtime, str) is False:
            raise InvalidAttributeException()

        if len(str(uu_id)) == 0 or len(str(starttime)) == 0\
            or len(str(endtime)) == 0 or len(result) == 0\
            or len(str(groundtruth)) == 0:
            raise EmptyParameterException()

        try:
            data_message = bytes(f"{str(uuid)},{str(starttime)},\
                {str(endtime)},{float(result)},{float(groundtruth)}\n", encoding='utf-8')
            return data_message
        except ValueError as exc:
            raise InvalidMessageException() from exc
