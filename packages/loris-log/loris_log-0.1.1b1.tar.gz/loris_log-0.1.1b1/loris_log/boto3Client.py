"""
The boto3 client to establish connection to the AWS cloud.
"""

import time
import boto3
from .myException import InvalidRoleAccessKeyException,\
    InvalidRoleSecretException,\
    InvalidAttributeException,\
    InvalidRegionNameException,\
    EmptyParameterException

class Boto3Client:
    """Boto 3 client to communicate to the AWS Cloudwatch.
    """

    def __init__(self, region_name, aws_key, aws_secret):
        """

        Args:
            region_name (string): The AWS service region name.
            aws_key (string): The AWS service role access key.
            aws_secret (string): The AWS service role secret key.

        Raises:
            error: When there is a communication error with AWS server.
        """
        if isinstance(region_name, str) is False or\
            isinstance(aws_key, str) is False or\
            isinstance(aws_secret, str) is False:
            raise InvalidAttributeException()

        if region_name == "" or region_name is None:
            raise InvalidRegionNameException()

        if aws_key == "" or aws_key is None:
            raise InvalidRoleAccessKeyException()

        if aws_secret == "" or aws_secret is None:
            raise InvalidRoleSecretException()

        self.client  = boto3.client("logs",
                                        region_name=region_name,
                                        aws_access_key_id=aws_key,
                                        aws_secret_access_key=aws_secret)

    def get_log_groups(self):
        """
        Get all the log groups available in the AWS cloudwatch.

        Returns:
            list: A list of log group names.
        """
        response = self.client.describe_log_groups()
        return  [logGroup['logGroupName'] for logGroup in response['logGroups']]

    def get_log_stream(self, log_group_name):
        """
        Get all the log stream inside a log group.

        Args:
            log_group_name (string): The name of the log group.

        Returns:
            list:  All the log streams' name available in a log group.
        """
        response = self.client.describe_log_streams(
            logGroupName=log_group_name
        )

        return [logGroup['logStreamName'] for logGroup in response['logStreams']]

    def __create_log_groups(self, log_group_name):
        """
        Create the log group if the not group is not present.

        Args:
            log_group_name (string): the log group name that wanted to be created.

        Returns:
            bool: True if the operation to create the log group was a success or False
                  otherwise.
        """
        if log_group_name not in self.get_log_groups():
            response = self.client.create_log_group(
                logGroupName=log_group_name,
            )
            return response
        return None

    def create_log_group_stream(self, log_group_name, log_stream_name):
        """
        Create the log stream if the current log group is present. Otherwise,
        create a new log group then create the desire the log stream

        Args:
            log_group_name (string): the log group name.
            log_stream_name (string): the log stream name.

        Returns:
            bool: whether the operation is a success (True) or otherwise (False).
        """
        if isinstance(log_group_name, str) is False or\
            isinstance(log_stream_name, str) is False:
            raise InvalidAttributeException()

        if log_stream_name == "" or log_group_name == "":
            raise EmptyParameterException()

        # check if the relevant log stream or log group
        # is present
        if log_group_name in self.get_log_groups() and \
          log_stream_name not in self.get_log_stream(log_group_name):
          # if the log stream is not present
          # create the log stream.
            self.client.create_log_stream(
              logGroupName=log_group_name,
              logStreamName=log_stream_name
            )
            return True

        # If the log group is not present, create the log group
        log_group_response = self.__create_log_groups(log_group_name)
        # If the log group is successfully created
        if log_group_response is not None:
            # create the log stream and return the response
            self.create_log_group_stream(log_group_name, log_stream_name)
            return True

        # Otherwise, return None to show the log stream and log group was present
        return False

    def set_log_message(self, log_group_name, log_stream_name, log_message):
        """
        Allow the application to push the relevant log message to the cloudwatch.

        Args:
            log_group_name (string): The name of the log group.
            log_stream_name (string): The name of the log stream.
            log_message (list): A list of application/ service/ api message.

        Returns:
            response: A list of aws responses.
        """
        if isinstance(log_group_name, str) is False or\
            isinstance(log_stream_name, str) is False or\
            isinstance(log_message, str) is False:
            raise InvalidAttributeException()

        if log_group_name == "" or log_stream_name == "" or\
            log_message == "":
            raise EmptyParameterException()

        # check if the log_group name and log stream is present
        if log_group_name in self.get_log_groups() and \
            log_stream_name in self.get_log_stream(log_group_name):
            # if present only start to push the log message
            # onto the cloudwatch.
            self.client.put_log_events(
                logGroupName=log_group_name,
                logStreamName=log_stream_name,
                logEvents=[
                    {
                        'timestamp': int(round(time.time() * 1000)),
                        'message': time.strftime('%Y-%m-%d %H:%M:%S') + \
                            "\t" + log_message
                    }
                ]
            )
            return True
        return False
