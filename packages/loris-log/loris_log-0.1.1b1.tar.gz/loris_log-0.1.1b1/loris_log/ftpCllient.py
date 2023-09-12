"""
The library to push log message to FTP server.
"""

import io
import datetime
import ipaddress
from ftplib import FTP, all_errors
from .myException import FTPConnectionFailedException,\
    FTPFileCreationException,\
    NoneValueException,\
    InvalidAttributeException,\
    EmptyParameterException,\
    InvalidFTPHostNameException,\
    InvalidFTPPortNumberException,\
    InvalidFTPUserNameException,\
    InvalidFTPPasswordException

# pylint: disable=E0302
# pylint: disable=W0212
class FtpClient:
    """Class to establish connection and writing to FTP server.
    """

    def __init__(self, hostname, port_num, username, password):
        """
        Establish communication with the remote FTP server.

        Args:
            hostname (string): FTP server hostname.
            port_num (string): FTP server port number.
            username (string): FTP server username.
            password (string): FTP server password.

        Raises:
            error: The FTP server connection establishment error.
        """

        if isinstance(port_num, int) is False:
            raise InvalidFTPPortNumberException()

        if isinstance(username, str) is False\
            or username is None or\
            username == "":
            raise InvalidFTPUserNameException()

        if isinstance(password, str) is False\
            or password is None or\
            password == "":
            raise InvalidFTPPasswordException()

        self.ftp_client = FTP()

        try:
            ipaddress.ip_address(hostname)
            self.ftp_client.connect(hostname, port_num)
            self.ftp_client.login(username, password)
        except all_errors as exc:
            raise FTPConnectionFailedException() from exc
        except ValueError as valuerr:
            raise InvalidFTPHostNameException() from valuerr

    def __get_ftp_directories(self):
        """
        To retrieve all the directories and files that are present 
        in the current working directory inside this directory 
        in this FTP server.

        Returns:
            list: A complete list of directories and files that are 
                currently available in present working directory.
        """
        dir_list = []
        self.ftp_client.retrlines('NLST', dir_list.append)
        return [item.split(" ")[-1] for item in dir_list]

    def __get_datetime(self):
        """
        Get the today date.

        Returns:
            string: Today's date.
        """
        return datetime.datetime.now().strftime("%Y-%m-%d")

    def __set_data_file_name(self, file_name):
        """
        Set the complete filename of the desired csv file.

        Args:
            file_name (string): The name of the csv file that wanted
                to be named.

        Returns:
            string: The complete filename of a csv file.
        """
        return self.__get_datetime() + "_"  + str(file_name) + ".csv"

    def __set_log_file_name(self, file_name):
        """
        Get the complete filename of the desired log file.

        Args:
            file_name (string): The name of the log file that wanted
                to be named.

        Returns:
            string: The complete fiilename of a log file.
        """
        return self.__get_datetime() + "_"  + str(file_name) + ".log"

    def create_ftp_log_data(self, directory_path, file_name):
        """
        Create a csv log file inside a FTP server based on the 
        predefined path.

        Args:
            directory_path (string): The path to the csv log file.
            file_name (string): Filename of the csv log file.

        Returns:
            boolean: True if the csv log file was successfully created;
                False otherwise.
        """
        if file_name == "" or file_name is None or\
            isinstance(file_name, str) is False:
            raise FTPFileCreationException()

        if directory_path == "" or directory_path is None or\
            isinstance(directory_path, str) is False:
            raise FTPFileCreationException()

        try:
            # get all the directory names
            directories = directory_path.split('/')
            for directory in directories:
                # check if the directory name is present
                if directory not in self.__get_ftp_directories():
                    # if not present create the directory
                    # then move to the corresponding directory
                    self.ftp_client.mkd(directory)
                    self.ftp_client.cwd(directory)
                else:
                    # if already present,
                    # just switch to the corresponding directory
                    self.ftp_client.cwd(directory)

            # Then create the desired log file if the log file
            # was not present before. Otherwise done nothing.
            filename = self.__set_data_file_name(file_name)
            if filename not in self.__get_ftp_directories():
                buf = io.BytesIO()
                buf.write(b"uuid,start,end,result,groundtruth\n")
                buf.seek(0)
                self.ftp_client.storbinary(f"STOR {filename}", buf)
        except all_errors as error:
            raise FTPFileCreationException() from error

    def set_ftp_log_data(self, directory_path, file_name, log_data):
        """
        Set the csv log file with the desired log data.

        Args:
            directory_path (string): The path to the csv log file.
            file_name (string): The name of the csv log file.
            log_data (string): The data that wanted to be logged.

        Returns:
            boolean: True if data was successfully logged; False otherwise.
        """
        if directory_path is None or file_name is None or\
            log_data is None:
            raise NoneValueException()

        if isinstance(directory_path, str) is False or\
            isinstance(file_name, str) is False or\
            isinstance(log_data, bytes) is False:
            raise InvalidAttributeException()

        if len(directory_path) == 0 or len(file_name) == 0 or\
            log_data == b"":
            raise EmptyParameterException()

        # get the desired directory name
        directories = directory_path.split('/')
        # loop through all the directory name
        for directory in directories:
            # if the name present move to the next directory
            if directory in self.__get_ftp_directories():
                self.ftp_client.cwd(directory)

        filename = self.__set_data_file_name(file_name)
        # check if the corrresponding file name present
        if filename in self.__get_ftp_directories():
            # if present write the log message to the relevant log file
            buf=io.BytesIO()
            buf.write(log_data)
            buf.seek(0)
            self.ftp_client.storbinary(f"APPE {filename}", buf, 1)

    def create_ftp_log_file(self, directory_path, file_name):
        """
        Create the log file inside an FTP server.

        Args:
            directory_name (string): The path to the created log
                                        file.
            file_name (string): The name of the log file.

        Returns:
            boolean : True of the log file was successfully created;
                        False otherwise.
        """
        if file_name == "" or file_name is None or\
            isinstance(file_name, str) is False:
            raise FTPFileCreationException()

        if directory_path == "" or directory_path is None or\
            isinstance(directory_path, str) is False:
            raise FTPFileCreationException()

        try:
            # get all the directories
            directories = directory_path.split("/")
            for directory in directories:
                # check if the directory is present
                # if not present create the directory
                # then move to the newly create directory
                if directory not in self.__get_ftp_directories():
                    self.ftp_client.mkd(directory)
                    self.ftp_client.cwd(directory)
                # if the directory present
                # just move to the newly create directory
                else:
                    self.ftp_client.cwd(directory)

            filename = self.__set_log_file_name(file_name)
            # check if the log file exist. If not create the
            # log file. otherwise, done nothing.
            if filename not in self.__get_ftp_directories():
                buf = io.BytesIO()
                buf.seek(0)
                self.ftp_client.storbinary(f"STOR {filename}", buf)
                return True
            return False
        except all_errors as error:
            raise FTPFileCreationException from error

    def set_ftp_log_file(self, directory_path, file_name, message):
        """
        Set the log file with application or system log.

        Args:
            directory_path (string): The path to the log file.
            file_name (string): The log file name.
            message (string): The message of the data.
            
         Returns:
            boolean : True of the log message was successfully written;
                        False otherwise.
        """
        if directory_path is None or file_name is None or\
            message is None:
            raise NoneValueException()

        if isinstance(directory_path, str) is False or\
            isinstance(file_name, str) is False or\
            isinstance(message, str) is False:
            raise InvalidAttributeException()

        if len(directory_path) == 0 or len(file_name) == 0 or\
            len(message) == 0:
            raise EmptyParameterException()

        # get the directories name
        directories = directory_path.split('/')
        # move to the corresponding directory if it
        # present
        for directory in directories:
            if directory in self.__get_ftp_directories():
                self.ftp_client.cwd(directory)

        # check for log file existence. If it exist only
        # write the log onto the corresponding log file.
        filename = self.__set_log_file_name(file_name)
        if filename in self.__get_ftp_directories():
            buf = io.BytesIO()
            buf.write(bytes("["+datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')+"]"+message+"\n", 'utf-8'))
            buf.seek(0)
            self.ftp_client.storbinary(f"APPE {filename}", buf, 1)
