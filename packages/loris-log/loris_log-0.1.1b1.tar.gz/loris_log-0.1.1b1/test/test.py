import sys 
sys.path.append("..")

import unittest 
import uuid
import datetime 
import logging
import botocore
from loris_log.boto3Client import Boto3Client
from loris_log.customLog import CustomLog
from loris_log.ftpCllient import FtpClient
from loris_log.myException import InvalidFTPHostNameException, InvalidFTPPortNumberException,\
    InvalidMessageException, InvalidFTPUserNameException, InvalidRoleSecretException, \
    InvalidRoleAccessKeyException, InvalidFTPPasswordException, EmptyParameterException,\
    NoneValueException, InvalidAttributeException, FTPConnectionFailedException,\
    FTPFileCreationException, InvalidRegionNameException

        
class TestBoto3Client(unittest.TestCase):
    
    def test_boto3_client_with_empty_region_name(self):
        target_region_name = ""
        target_aws_key = ""
        target_aws_secret = ""
        
        with self.assertRaises(InvalidRegionNameException) as context:
            Boto3Client(target_region_name, target_aws_key, target_aws_secret)
        self.assertTrue("Invalid region name." in str(context.exception))
        
    def test_boto3_client_with_empty_access_key(self):
        target_region_name = ""
        target_aws_key = ""
        target_aws_secret = ""
        
        with self.assertRaises(InvalidRoleAccessKeyException) as context:
            Boto3Client(target_region_name, target_aws_key, target_aws_secret)
        self.assertTrue("Invalid role access key." in str(context.exception))
        
    def test_boto3_client_with_empty_secret(self):
        target_region_name = ""
        target_aws_key = ""
        target_aws_secret = ""
        
        with self.assertRaises(InvalidRoleSecretException) as context:
            Boto3Client(target_region_name, target_aws_key, target_aws_secret)
        self.assertTrue("Invalid role secret." in str(context.exception))
        
    def test_get_log_group(self):
        target_region_name = ""
        target_aws_key = "s"
        target_aws_secret = ""
        boto3Client = Boto3Client(target_region_name, target_aws_key, target_aws_secret)
        response = boto3Client.get_log_groups()
        self.assertTrue(len(response) > 0)
        
    def test_get_log_stream(self):
        target_region_name = ""
        target_aws_key = "s"
        target_aws_secret = ""
        boto3Client = Boto3Client(target_region_name, target_aws_key, target_aws_secret)
        response = boto3Client.get_log_stream()
        self.assertTrue(len(response) > 0)
        
    def test_boto3_client_with_other_attribute_secret(self):
        target_region_name = ""
        target_aws_key = 123
        target_aws_secret = ""
        with self.assertRaises(InvalidAttributeException) as context:
            Boto3Client(target_region_name, target_aws_key, target_aws_secret)
        self.assertTrue("Attribute error." in str(context.exception))
        
    def test_boto3_client_with_wrong_password(self):
        target_region_name = ""
        target_aws_key = "s"
        target_aws_secret = "123412"
        # with self.assertRaises(AWSConnectionException) as context:
        client = Boto3Client(target_region_name, target_aws_key, target_aws_secret)
        # self.assertTrue("AWS connection failure." in str(context.exception))

    def test_get_log_group(self):
        target_region_name = ""
        target_aws_key = ""
        target_aws_secret = ""
        boto3Client = Boto3Client(target_region_name, target_aws_key, target_aws_secret)

        response = boto3Client.get_log_groups()
        self.assertIsNot(len(response), 0)
        
    def test_get_log_stream(self):
        target_region_name = ""
        target_aws_key = ""
        target_aws_secret = ""
        target_log_group = "sample"
        boto3Client = Boto3Client(target_region_name, target_aws_key, target_aws_secret)
        response = boto3Client.get_log_stream(target_log_group)
        self.assertIsNotNone(response)
    
    def test_create_log_groups_stream_again(self):
        target_region_name = ""
        target_aws_key = ""
        target_aws_secret = ""
        boto3Client = Boto3Client(target_region_name, target_aws_key, target_aws_secret)
        target_log_group = "sample"
        target_log_stream = "sample-log"
        creation_response = boto3Client.create_log_group_stream(target_log_group, target_log_stream)
        self.assertIn(creation_response, [True, False])
        
        target_message = "target sample message"
        response = boto3Client.set_log_message(target_log_group, target_log_stream, target_message)
        self.assertIn(response, [True, False])
        
    def test_create_log_stream_with_empty_log_group(self):
        target_region_name = ""
        target_aws_key = ""
        target_aws_secret = ""
        boto3Client = Boto3Client(target_region_name, target_aws_key, target_aws_secret)
        target_log_group = "sample"
        target_log_stream = "sample-log"
        with self.assertRaises(EmptyParameterException) as context:
            creation_response = boto3Client.create_log_group_stream("", target_log_stream)
        self.assertTrue("Attempt to enter empty input." in str(context.exception))
        
    def test_create_log_stream_with_other_attribute_log_stream_name(self):
        target_region_name = ""
        target_aws_key = ""
        target_aws_secret = ""
        boto3Client = Boto3Client(target_region_name, target_aws_key, target_aws_secret)
        target_log_group = "sample"
        target_log_stream = "sample-log"
        with self.assertRaises(InvalidAttributeException) as context:
            creation_response = boto3Client.create_log_group_stream(target_log_group, None)
        self.assertTrue("Attribute error." in str(context.exception))
        
    def test_set_log_message_on_not_exist_log_group(self):
        target_region_name = ""
        target_aws_key = ""
        target_aws_secret = ""
        boto3Client = Boto3Client(target_region_name, target_aws_key, target_aws_secret)
        target_log_group = "sample1"
        target_log_stream = "sample-log"
        target_message = "target sample message"
        response = boto3Client.set_log_message(target_log_group, target_log_stream, target_message)
        self.assertFalse(response)
        
    def test_set_log_with_wrong_attribute(self):
        target_region_name = ""
        target_aws_key = ""
        target_aws_secret = ""
        boto3Client = Boto3Client(target_region_name, target_aws_key, target_aws_secret)
        target_log_group = None
        target_log_stream = "sample-log"
        target_message = "target sample message"
        
        with self.assertRaises(InvalidAttributeException) as context:
            response = boto3Client.set_log_message(target_log_group, target_log_stream, target_message)
        self.assertTrue("Attribute error." in str(context.exception))
        
    def test_set_log_with_empty_message(self):
        target_region_name = ""
        target_aws_key = ""
        target_aws_secret = ""
        boto3Client = Boto3Client(target_region_name, target_aws_key, target_aws_secret)
        target_log_group = "sample"
        target_log_stream = "sample-log"
        target_message = ""
        
        with self.assertRaises(EmptyParameterException) as context:
            response = boto3Client.set_log_message(target_log_group, target_log_stream, target_message)
        self.assertTrue("Attempt to enter empty input." in str(context.exception))
        
    def test_create_log_groups_stream(self):
        target_region_name = ""
        target_aws_key = ""
        target_aws_secret = ""
        boto3Client = Boto3Client(target_region_name, target_aws_key, target_aws_secret)
        target_log_group = "sample"
        target_log_stream = "sample-log"
        creation_response = boto3Client.create_log_group_stream(target_log_group, target_log_stream)
        self.assertIn(creation_response, [True, False])
        
        target_message = "target sample message"
        response = boto3Client.set_log_message(target_log_group, target_log_stream, target_message)
        self.assertIn(response, [True, False])
        
class TestCustomLog(unittest.TestCase):
    
    def test_error_log_message(self):
        target_error_message = ["system failed", "exception"]
        target_name = "app"
        id = uuid.uuid4()
        
        error_message = CustomLog.set_error_message(id, target_name, target_error_message)
        self.assertNotEqual(len(error_message), 0)
        
    def test_error_empty_name(self):
        target_error_message = ["system failed", "exception"]
        target_name = ""
        id = uuid.uuid4()
        
        with self.assertRaises(EmptyParameterException) as context:
            CustomLog.set_error_message(id, target_name, target_error_message)
        self.assertTrue("Attempt to enter empty input." in str(context.exception))
        
    def test_error_number_name(self):
        target_error_message = ["system failed", "exception"]
        target_name = 123.1938484
        id = uuid.uuid4()
        
        with self.assertRaises(InvalidAttributeException) as context:
            CustomLog.set_error_message(id, target_name, target_error_message)
        self.assertTrue("Attribute error." in str(context.exception))
        
    def test_error_log_none_uuid(self):
        target_error_message = ["system failed", "exception"]
        target_name = "app"
        id = None
        
        with self.assertRaises(NoneValueException) as context:
            CustomLog.set_error_message(id, target_name, target_error_message)
        self.assertTrue("The input value should not be none." in str(context.exception))
        
    def test_error_log_NaN_uuid(self):
        import math
        target_error_message = ["system failed", "exception"]
        target_name = "app"
        id = math.nan
        
        with self.assertRaises(EmptyParameterException) as context:
            CustomLog.set_error_message(id, target_name, target_error_message)
        self.assertTrue("Attempt to enter empty input." in str(context.exception))
        
    def test_error_log_incomplete_uuid(self):
        import math
        target_error_message = ["system failed", "exception"]
        target_name = "app"
        id = math.nan
        
        with self.assertRaises(EmptyParameterException) as context:
            CustomLog.set_error_message(id, target_name, target_error_message)
        self.assertTrue("Attempt to enter empty input." in str(context.exception))
        
        
    def test_error_log_empty_uuid(self):
        target_error_message = ["system failed", "exception"]
        target_name = "app"
        id = ""
        
        with self.assertRaises(EmptyParameterException) as context:
            CustomLog.set_error_message(id, target_name, target_error_message)
        self.assertTrue("Attempt to enter empty input." in str(context.exception))
        
    def test_error_log_empty_message(self):
        target_error_message = [""]
        target_name = "app"
        id = uuid.uuid4()
    
        
        error_message = CustomLog.set_error_message(id, target_name, target_error_message)
        self.assertTrue(len(error_message) > 0)
        
    def test_error_log_empty_list_message(self):
        target_error_message = []
        target_name = "app"
        id = uuid.uuid4()
        
        with self.assertRaises(NoneValueException) as context:
            CustomLog.set_error_message(id, target_name, target_error_message)
        self.assertTrue("The input value should not be none." in str(context.exception))
        
    def test_error_log_empty_list_message(self):
        target_error_message = None
        target_name = "app"
        id = uuid.uuid4()
        
        with self.assertRaises(NoneValueException) as context:
            CustomLog.set_error_message(id, target_name, target_error_message)
        self.assertTrue("The input value should not be none." in str(context.exception))
        
    def test_info_log_empty_message_weird_message(self):
        target_error_message = [None, 123]
        target_name = "app"
        id = uuid.uuid4()
        
        with self.assertRaises(InvalidMessageException) as context:
            CustomLog.set_info_message(id, target_name, target_error_message)
        self.assertTrue("Invalid message." in str(context.exception))
        
    def test_fatal_log_empty_message_weird_message(self):
        target_error_message = [None, 123]
        target_name = "app"
        id = uuid.uuid4()
        
        with self.assertRaises(InvalidMessageException) as context:
            CustomLog.set_fatal_message(id, target_name, target_error_message)
        self.assertTrue("Invalid message." in str(context.exception))
        
    def test_debug_log_empty_message_weird_message(self):
        target_error_message = [None, 123]
        target_name = "app"
        id = uuid.uuid4()
        
        with self.assertRaises(InvalidMessageException) as context:
            CustomLog.set_debug_message(id, target_name, target_error_message)
        self.assertTrue("Invalid message." in str(context.exception))
        
    def test_error_log_empty_message_weird_message(self):
        target_error_message = [None, 123]
        target_name = "app"
        id = uuid.uuid4()
        
        with self.assertRaises(InvalidMessageException) as context:
            CustomLog.set_error_message(id, target_name, target_error_message)
        self.assertTrue("Invalid message." in str(context.exception))
        
    def test_error_log_number_message(self):
        target_error_message = [1, 2, 3]
        target_name = "app"
        id = uuid.uuid4()
        with self.assertRaises(InvalidAttributeException) as context:
            CustomLog.set_error_message(id, target_name, target_error_message)
        self.assertTrue("Attribute error." in str(context.exception))
        
    def test_error_log_number_message(self):
        target_error_message = 12
        target_name = "app"
        id = uuid.uuid4()
        with self.assertRaises(InvalidAttributeException) as context:
            CustomLog.set_error_message(id, target_name, target_error_message)
        self.assertTrue("Attribute error." in str(context.exception))
    # #########################################################################################
    # TEST set_debug_message function
    def test_debug_log_message(self):
        target_error_message = ["system failed", "exception"]
        target_name = "app"
        id = uuid.uuid4()
        
        debug_message = CustomLog.set_debug_message(id, target_name, target_error_message)
        self.assertNotEqual(len(debug_message), 0)
        
    def test_debug_empty_name(self):
        target_error_message = ["system failed", "exception"]
        target_name = ""
        id = uuid.uuid4()
        
        with self.assertRaises(EmptyParameterException) as context:
            CustomLog.set_debug_message(id, target_name, target_error_message)
        self.assertTrue("Attempt to enter empty input." in str(context.exception))
        
    def test_debug_number_name(self):
        target_error_message = ["system failed", "exception"]
        target_name = 123.1938484
        id = uuid.uuid4()
        
        with self.assertRaises(InvalidAttributeException) as context:
            CustomLog.set_debug_message(id, target_name, target_error_message)
        self.assertTrue("Attribute error." in str(context.exception))
        
    def test_debug_log_none_uuid(self):
        target_error_message = ["system failed", "exception"]
        target_name = "app"
        id = None
        
        with self.assertRaises(NoneValueException) as context:
            CustomLog.set_debug_message(id, target_name, target_error_message)
        self.assertTrue("The input value should not be none." in str(context.exception))
        
    def test_debug_log_NaN_uuid(self):
        import math
        target_error_message = ["system failed", "exception"]
        target_name = "app"
        id = math.nan
        
        with self.assertRaises(EmptyParameterException) as context:
            CustomLog.set_debug_message(id, target_name, target_error_message)
        self.assertTrue("Attempt to enter empty input." in str(context.exception))
        
    def test_error_debug_incomplete_uuid(self):
        import math
        target_error_message = ["system failed", "exception"]
        target_name = "app"
        id = math.nan
        
        with self.assertRaises(EmptyParameterException) as context:
            CustomLog.set_debug_message(id, target_name, target_error_message)
        self.assertTrue("Attempt to enter empty input." in str(context.exception))
        
        
    def test_debug_log_empty_uuid(self):
        target_error_message = ["system failed", "exception"]
        target_name = "app"
        id = ""
        
        with self.assertRaises(EmptyParameterException) as context:
            CustomLog.set_debug_message(id, target_name, target_error_message)
        self.assertTrue("Attempt to enter empty input." in str(context.exception))
        
    def test_debug_log_empty_message(self):
        target_error_message = [""]
        target_name = "app"
        id = uuid.uuid4()
    
        
        error_message = CustomLog.set_debug_message(id, target_name, target_error_message)
        self.assertTrue(len(error_message) > 0)
        
    def test_debug_log_empty_list_message(self):
        target_error_message = []
        target_name = "app"
        id = uuid.uuid4()
        
        with self.assertRaises(NoneValueException) as context:
            CustomLog.set_debug_message(id, target_name, target_error_message)
        self.assertTrue("The input value should not be none." in str(context.exception))
        
    def test_debug_log_empty_list_message(self):
        target_error_message = None
        target_name = "app"
        id = uuid.uuid4()
        
        with self.assertRaises(NoneValueException) as context:
            CustomLog.set_debug_message(id, target_name, target_error_message)
        self.assertTrue("The input value should not be none." in str(context.exception))
        
    def test_debug_log_number_message(self):
        target_error_message = [1, 2, 3]
        target_name = "app"
        id = uuid.uuid4()
        with self.assertRaises(InvalidMessageException) as context:
            CustomLog.set_debug_message(id, target_name, target_error_message)
        self.assertTrue("Invalid message." in str(context.exception))
        
    def test_debug_log_number_message(self):
        target_error_message = 12
        target_name = "app"
        id = uuid.uuid4()
        with self.assertRaises(InvalidAttributeException) as context:
            CustomLog.set_debug_message(id, target_name, target_error_message)
        self.assertTrue("Attribute error." in str(context.exception))
    
    # ##########################################################################################
    # Test set_fatal_message function
    
    def test_fatal_log_message(self):
        target_error_message = ["system failed", "exception"]
        target_name = "app"
        id = uuid.uuid4()
        
        fatal_message = CustomLog.set_fatal_message(id, target_name, target_error_message)
        self.assertNotEqual(len(fatal_message), 0)
        
    def test_fatal_empty_name(self):
        target_error_message = ["system failed", "exception"]
        target_name = ""
        id = uuid.uuid4()
        
        with self.assertRaises(EmptyParameterException) as context:
            CustomLog.set_fatal_message(id, target_name, target_error_message)
        self.assertTrue("Attempt to enter empty input." in str(context.exception))
        
    def test_fatal_number_name(self):
        target_error_message = ["system failed", "exception"]
        target_name = 123.1938484
        id = uuid.uuid4()
        
        with self.assertRaises(InvalidAttributeException) as context:
            CustomLog.set_fatal_message(id, target_name, target_error_message)
        self.assertTrue("Attribute error." in str(context.exception))
        
    def test_fatal_log_none_uuid(self):
        target_error_message = ["system failed", "exception"]
        target_name = "app"
        id = None
        
        with self.assertRaises(NoneValueException) as context:
            CustomLog.set_fatal_message(id, target_name, target_error_message)
        self.assertTrue("The input value should not be none." in str(context.exception))
        
    def test_fatal_log_NaN_uuid(self):
        import math
        target_error_message = ["system failed", "exception"]
        target_name = "app"
        id = math.nan
        
        with self.assertRaises(EmptyParameterException) as context:
            CustomLog.set_fatal_message(id, target_name, target_error_message)
        self.assertTrue("Attempt to enter empty input." in str(context.exception))
        
    def test_fatal_debug_incomplete_uuid(self):
        import math
        target_error_message = ["system failed", "exception"]
        target_name = "app"
        id = math.nan
        
        with self.assertRaises(EmptyParameterException) as context:
            CustomLog.set_fatal_message(id, target_name, target_error_message)
        self.assertTrue("Attempt to enter empty input." in str(context.exception))
        
        
    def test_fatal_log_empty_uuid(self):
        target_error_message = ["system failed", "exception"]
        target_name = "app"
        id = ""
        
        with self.assertRaises(EmptyParameterException) as context:
            CustomLog.set_fatal_message(id, target_name, target_error_message)
        self.assertTrue("Attempt to enter empty input." in str(context.exception))
        
    def test_fatal_log_empty_message(self):
        target_error_message = [""]
        target_name = "app"
        id = uuid.uuid4()
    
        
        error_message = CustomLog.set_fatal_message(id, target_name, target_error_message)
        self.assertTrue(len(error_message) > 0)
        
    def test_fatal_log_empty_list_message(self):
        target_error_message = []
        target_name = "app"
        id = uuid.uuid4()
        
        with self.assertRaises(NoneValueException) as context:
            CustomLog.set_fatal_message(id, target_name, target_error_message)
        self.assertTrue("The input value should not be none." in str(context.exception))
        
    def test_fatal_log_empty_list_message(self):
        target_error_message = None
        target_name = "app"
        id = uuid.uuid4()
        
        with self.assertRaises(NoneValueException) as context:
            CustomLog.set_fatal_message(id, target_name, target_error_message)
        self.assertTrue("The input value should not be none." in str(context.exception))
        
    def test_fatal_log_number_message(self):
        target_error_message = [1, 2, 3]
        target_name = "app"
        id = uuid.uuid4()
        with self.assertRaises(InvalidAttributeException) as context:
            CustomLog.set_fatal_message(id, target_name, target_error_message)
        self.assertTrue("Attribute error." in str(context.exception))
        
    def test_fatal_log_number_message(self):
        target_error_message = 12
        target_name = "app"
        id = uuid.uuid4()
        with self.assertRaises(InvalidAttributeException) as context:
            CustomLog.set_fatal_message(id, target_name, target_error_message)
        self.assertTrue("Attribute error." in str(context.exception))
        
    # ######################################################################################
    # Test set_info_message function
    
    def test_info_log_message(self):
        target_error_message = ["system failed", "exception"]
        target_name = "app"
        id = uuid.uuid4()
        
        info_message = CustomLog.set_fatal_message(id, target_name, target_error_message)
        self.assertNotEqual(len(info_message), 0)
        
    def test_info_empty_name(self):
        target_error_message = ["system failed", "exception"]
        target_name = ""
        id = uuid.uuid4()
        
        with self.assertRaises(EmptyParameterException) as context:
            CustomLog.set_info_message(id, target_name, target_error_message)
        self.assertTrue("Attempt to enter empty input." in str(context.exception))
        
    def test_info_number_name(self):
        target_error_message = ["system failed", "exception"]
        target_name = 123.1938484
        id = uuid.uuid4()
        
        with self.assertRaises(InvalidAttributeException) as context:
            CustomLog.set_info_message(id, target_name, target_error_message)
        self.assertTrue("Attribute error." in str(context.exception))
        
    def test_info_log_none_uuid(self):
        target_error_message = ["system failed", "exception"]
        target_name = "app"
        id = None
        
        with self.assertRaises(NoneValueException) as context:
            CustomLog.set_info_message(id, target_name, target_error_message)
        self.assertTrue("The input value should not be none." in str(context.exception))
        
    def test_info_log_NaN_uuid(self):
        import math
        target_error_message = ["system failed", "exception"]
        target_name = "app"
        id = math.nan
        
        with self.assertRaises(EmptyParameterException) as context:
            CustomLog.set_info_message(id, target_name, target_error_message)
        self.assertTrue("Attempt to enter empty input." in str(context.exception))
        
    def test_info_log_incomplete_uuid(self):
        import math
        target_error_message = ["system failed", "exception"]
        target_name = "app"
        id = math.nan
        
        with self.assertRaises(EmptyParameterException) as context:
            CustomLog.set_info_message(id, target_name, target_error_message)
        self.assertTrue("Attempt to enter empty input." in str(context.exception))
        
        
    def test_info_log_empty_uuid(self):
        target_error_message = ["system failed", "exception"]
        target_name = "app"
        id = ""
        
        with self.assertRaises(EmptyParameterException) as context:
            CustomLog.set_info_message(id, target_name, target_error_message)
        self.assertTrue("Attempt to enter empty input." in str(context.exception))
        
    def test_info_log_empty_message(self):
        target_error_message = [""]
        target_name = "app"
        id = uuid.uuid4()
    
        
        error_message = CustomLog.set_info_message(id, target_name, target_error_message)
        self.assertTrue(len(error_message) > 0)
        
    def test_info_log_empty_list_message(self):
        target_error_message = []
        target_name = "app"
        id = uuid.uuid4()
        
        with self.assertRaises(NoneValueException) as context:
            CustomLog.set_info_message(id, target_name, target_error_message)
        self.assertTrue("The input value should not be none." in str(context.exception))
        
    def test_info_log_empty_list_message(self):
        target_error_message = None
        target_name = "app"
        id = uuid.uuid4()
        
        with self.assertRaises(NoneValueException) as context:
            CustomLog.set_info_message(id, target_name, target_error_message)
        self.assertTrue("The input value should not be none." in str(context.exception))
        
    
        
    def test_info_log_number_message(self):
        target_error_message = [1, 2, 3]
        target_name = "app"
        id = uuid.uuid4()
        with self.assertRaises(InvalidMessageException) as context:
            CustomLog.set_info_message(id, target_name, target_error_message)
        self.assertTrue("Invalid message." in str(context.exception))
        
    def test_info_log_number_message(self):
        target_error_message = 12
        target_name = "app"
        id = uuid.uuid4()
        with self.assertRaises(InvalidAttributeException) as context:
            CustomLog.set_info_message(id, target_name, target_error_message)
        self.assertTrue("Attribute error." in str(context.exception))
        
    # ######################################################################################
    # Test set_ftp_log_message function 
    
    def test_ftp_log_message(self):
        start_time = datetime.datetime.now()
        target_start_time = start_time.strftime("%H:%M:%S")
        end_time = datetime.datetime.now()
        target_end_time = end_time.strftime("%H:%M:%S")
        target_result = b"32"
        target_ground_truth = b"3"
        id = uuid.uuid4()
        file_data_message = CustomLog.set_ftp_log_data(id,
                                    target_start_time, 
                                    target_end_time, 
                                    target_result, 
                                    target_ground_truth)
        self.assertIn(target_result, file_data_message)
        self.assertIn(target_ground_truth, file_data_message)
        
    def test_frp_log_message_other_attribute_result(self):
        start_time = datetime.datetime.now()
        target_start_time = start_time.strftime("%H:%M:%S")
        end_time = datetime.datetime.now()
        target_end_time = end_time.strftime("%H:%M:%S")
        target_result = b"7890-cm,"
        target_ground_truth = b"12"
        id = uuid.uuid4()
        with self.assertRaises(InvalidMessageException) as context:
            CustomLog.set_ftp_log_data(id,
                                    target_start_time, 
                                    target_end_time, 
                                    target_result, 
                                    target_ground_truth)
        self.assertTrue("Invalid message." in str(context.exception))
        
    def test_ftp_log_message_other_attribute_groundtruth(self):
        import math
        start_time = datetime.datetime.now()
        target_start_time = start_time.strftime("%H:%M:%S")
        end_time = datetime.datetime.now()
        target_end_time = end_time.strftime("%H:%M:%S")
        target_result = b"32"
        target_ground_truth = b"wwertyuio"
        id = uuid.uuid4()
        with self.assertRaises(InvalidMessageException) as context:
            CustomLog.set_ftp_log_data(id,
                                    target_start_time, 
                                    target_end_time, 
                                    target_result, 
                                    target_ground_truth)
        self.assertTrue("Invalid message." in str(context.exception))
        
        
    def test_ftp_log_message_empty_groundtruth(self):
        start_time = datetime.datetime.now()
        target_start_time = start_time.strftime("%H:%M:%S")
        end_time = datetime.datetime.now()
        target_end_time = end_time.strftime("%H:%M:%S")
        target_result = b"32"
        target_ground_truth = ""
        id = uuid.uuid4()
        with self.assertRaises(EmptyParameterException) as context:
            CustomLog.set_ftp_log_data(id,
                                    target_start_time, 
                                    target_end_time, 
                                    target_result, 
                                    target_ground_truth)
        self.assertTrue("Attempt to enter empty input." in str(context.exception))
        
    def test_ftp_log_message_none_groundtruth(self):
        start_time = datetime.datetime.now()
        target_start_time = start_time.strftime("%H:%M:%S")
        end_time = datetime.datetime.now()
        target_end_time = end_time.strftime("%H:%M:%S")
        target_result = b"32"
        target_ground_truth = None
        with self.assertRaises(NoneValueException) as context:
            CustomLog.set_ftp_log_data(id,
                                    target_start_time, 
                                    target_end_time, 
                                    target_result, 
                                    target_ground_truth)
        self.assertTrue("The input value should not be none." in str(context.exception))
        
    def test_ftp_log_message_empty_result(self):
        start_time = datetime.datetime.now()
        target_start_time = start_time.strftime("%H:%M:%S")
        end_time = datetime.datetime.now()
        target_end_time = end_time.strftime("%H:%M:%S")
        target_result = ""
        target_ground_truth = b"3"
        id = uuid.uuid4()
        with self.assertRaises(EmptyParameterException) as context:
            CustomLog.set_ftp_log_data(id,
                                    target_start_time, 
                                    target_end_time, 
                                    target_result, 
                                    target_ground_truth)
        self.assertTrue("Attempt to enter empty input." in str(context.exception))
        
    def test_ftp_log_message_other_attribute_end_time(self):
        start_time = datetime.datetime.now()
        target_start_time = start_time.strftime("%H:%M:%S")
        end_time = datetime.datetime.now()
        target_end_time = []
        target_result = b"32"
        target_ground_truth = b"3"
        id = uuid.uuid4()
        with self.assertRaises(InvalidAttributeException) as context:
            CustomLog.set_ftp_log_data(id,
                                    target_start_time, 
                                    target_end_time, 
                                    target_result, 
                                    target_ground_truth)
        self.assertTrue("Attribute error." in str(context.exception))
        
    
    def test_ftp_log_message_empty_end_time(self):
        start_time = datetime.datetime.now()
        target_start_time = start_time.strftime("%H:%M:%S")
        end_time = datetime.datetime.now()
        target_end_time = ""
        target_result = b"32"
        target_ground_truth = b"3"
        id = uuid.uuid4()
        with self.assertRaises(EmptyParameterException) as context:
            CustomLog.set_ftp_log_data(id,
                                    target_start_time, 
                                    target_end_time, 
                                    target_result, 
                                    target_ground_truth)
        self.assertTrue("Attempt to enter empty input." in str(context.exception))
        
    def test_ftp_log_message_none_end_time(self):
        start_time = datetime.datetime.now()
        target_start_time = start_time.strftime("%H:%M:%S")
        end_time = datetime.datetime.now()
        target_end_time = None
        target_result = b"32"
        target_ground_truth = b"3"
        id = uuid.uuid4()
        with self.assertRaises(NoneValueException) as context:
            CustomLog.set_ftp_log_data(id,
                                    target_start_time, 
                                    target_end_time, 
                                    target_result, 
                                    target_ground_truth)
        self.assertTrue("The input value should not be none." in str(context.exception))
        
    def test_ftp_log_message_wrong_start_time(self):
        start_time = datetime.datetime.now()
        target_start_time = start_time
        end_time = datetime.datetime.now()
        target_end_time = end_time.strftime("%H:%M:%S")
        target_result = b"32"
        target_ground_truth = b"3"
        id = uuid.uuid4()
        with self.assertRaises(InvalidAttributeException) as context:
            CustomLog.set_ftp_log_data(id,
                                    target_start_time, 
                                    target_end_time, 
                                    target_result, 
                                    target_ground_truth)
        self.assertTrue("Attribute error." in str(context.exception))
        
    def test_ftp_log_message_empty_start_time(self):
        start_time = datetime.datetime.now()
        target_start_time = ""
        end_time = datetime.datetime.now()
        target_end_time = end_time.strftime("%H:%M:%S")
        target_result = b"32"
        target_ground_truth = b"3"
        id = uuid.uuid4()
        with self.assertRaises(EmptyParameterException) as context:
            CustomLog.set_ftp_log_data(id,
                                    target_start_time, 
                                    target_end_time, 
                                    target_result, 
                                    target_ground_truth)
        self.assertTrue("Attempt to enter empty input." in str(context.exception))
        
    def test_ftp_log_message_none_start_time(self):
        target_start_time = None
        end_time = datetime.datetime.now()
        target_end_time = end_time.strftime("%H:%M:%S")
        target_result = b"32"
        target_ground_truth = b"3"
        id = uuid.uuid4()
        with self.assertRaises(NoneValueException) as context:
            CustomLog.set_ftp_log_data(id,
                                    target_start_time, 
                                    target_end_time, 
                                    target_result, 
                                    target_ground_truth)
        self.assertTrue("The input value should not be none." in str(context.exception))
        
    def test_ftp_log_message_other_attribute_start_time(self):
        target_start_time = []
        end_time = datetime.datetime.now()
        target_end_time = end_time.strftime("%H:%M:%S")
        target_result = b"32"
        target_ground_truth = b"3"
        id = uuid.uuid4()
        with self.assertRaises(InvalidAttributeException) as context:
            CustomLog.set_ftp_log_data(id,
                                    target_start_time, 
                                    target_end_time, 
                                    target_result, 
                                    target_ground_truth)
        self.assertTrue("Attribute error." in str(context.exception))
        
    def test_ftp_log_message_none_uuid(self):
        start_time = datetime.datetime.now()
        target_start_time = start_time.strftime("%H:%M:%S")
        end_time = datetime.datetime.now()
        target_end_time = end_time.strftime("%H:%M:%S")
        target_result = b"32"
        target_ground_truth = b"3"
        id = None
        
        with self.assertRaises(NoneValueException) as context:
            CustomLog.set_ftp_log_data(id,
                                    target_start_time, 
                                    target_end_time, 
                                    target_result, 
                                    target_ground_truth)
        self.assertTrue("The input value should not be none." in str(context.exception))
        
    def test_ftp_log_message_empty_uuid(self):
        start_time = datetime.datetime.now()
        target_start_time = start_time.strftime("%H:%M:%S")
        end_time = datetime.datetime.now()
        target_end_time = end_time.strftime("%H:%M:%S")
        target_result = b"32"
        target_ground_truth = b"3"
        id = ""
        
        with self.assertRaises(InvalidAttributeException) as context:
            CustomLog.set_ftp_log_data(id,
                                    target_start_time, 
                                    target_end_time, 
                                    target_result, 
                                    target_ground_truth)
        self.assertTrue("Attribute error." in str(context.exception))
        
    def test_ftp_log_message_other_uuid(self):
        start_time = datetime.datetime.now()
        target_start_time = start_time.strftime("%H:%M:%S")
        end_time = datetime.datetime.now()
        target_end_time = end_time.strftime("%H:%M:%S")
        target_result = b"32"
        target_ground_truth = b"3"
        id = [9, 8]
        
        with self.assertRaises(InvalidAttributeException) as context:
            CustomLog.set_ftp_log_data(id,
                                    target_start_time, 
                                    target_end_time, 
                                    target_result, 
                                    target_ground_truth)
        self.assertTrue("Attribute error." in str(context.exception))
        
# #####################################################################################
class TestFtpClient(unittest.TestCase):
    
    def test_ftp_push_log_with_none_path(self):
        target_hostname = ""
        target_port = 00
        target_username = ""
        target_password = ""
        target_path = "log_testing/example"
        target_filename = "2023-09-06_sample"
        client = FtpClient(target_hostname, target_port,\
            target_username, target_password)
        client.create_ftp_log_file(target_path, target_filename)
        customLog = CustomLog()
        ids = uuid.uuid5(uuid.NAMESPACE_DNS, 'python.org')
        log = customLog.set_debug_message(ids, "name", ["The sample debug message."])
        with self.assertRaises(NoneValueException) as context:
            response = client.set_ftp_log_file(None, 
                                    target_filename,
                                    log)
        self.assertTrue("The input value should not be none." in str(context.exception))
        
    def test_ftp_push_log_with_wrong_empty_filename(self):
        target_hostname = ""
        target_port = 00
        target_username = ""
        target_password = ""
        target_path = "log_testing/example"
        target_filename = "2023-09-06_sample"
        client = FtpClient(target_hostname, target_port,\
            target_username, target_password)
        client.create_ftp_log_file(target_path, target_filename)
        customLog = CustomLog()
        ids = uuid.uuid5(uuid.NAMESPACE_DNS, 'python.org')
        log = customLog.set_debug_message(ids, "name", ["The sample debug message."])
        with self.assertRaises(EmptyParameterException) as context:
            response = client.set_ftp_log_file(target_path, 
                                    "",
                                    log)
        self.assertTrue("Attempt to enter empty input." in str(context.exception))
        
    def test_ftp_push_log_with_wrong_attribute_log(self):
        target_hostname = ""
        target_port = 00
        target_username = ""
        target_password = ""
        target_path = "log_testing/example"
        target_filename = "2023-09-06_sample"
        client = FtpClient(target_hostname, target_port,\
            target_username, target_password)
        client.create_ftp_log_file(target_path, target_filename)
        customLog = CustomLog()
        ids = uuid.uuid5(uuid.NAMESPACE_DNS, 'python.org')
        log = customLog.set_debug_message(ids, "name", ["The sample debug message."])
        with self.assertRaises(InvalidAttributeException) as context:
            response = client.set_ftp_log_file(target_path, 
                                    target_filename,
                                    123)
        self.assertTrue("Attribute error." in str(context.exception))
    
    def test_ftp_push_log(self):
        target_hostname = ""
        target_port = 00
        target_username = ""
        target_password = ""
        target_path = "log_testing/example"
        target_filename = "2023-09-06_sample"
        client = FtpClient(target_hostname, target_port,\
            target_username, target_password)
        client.create_ftp_log_file(target_path, target_filename)
        customLog = CustomLog()
        ids = uuid.uuid5(uuid.NAMESPACE_DNS, 'python.org')
        log = customLog.set_debug_message(ids, "name", ["The sample debug message."])
        response = client.set_ftp_log_file(target_path, 
                                target_filename,
                                log)
        self.assertTrue(response)
        
    def test_ftp_push_log_same_directory_again(self):
        target_hostname = ""
        target_port = 00
        target_username = ""
        target_password = ""
        target_path = "log_testing/example"
        target_filename = "2023-09-06_sample"
        client = FtpClient(target_hostname, target_port,\
            target_username, target_password)
        client.create_ftp_log_file(target_path, target_filename)
        customLog = CustomLog()
        ids = uuid.uuid5(uuid.NAMESPACE_DNS, 'python.org')
        log = customLog.set_debug_message(ids, "name", ["The sample debug message again."])
        response = client.set_ftp_log_file(target_path, 
                                target_filename,
                                log)
        self.assertTrue(response)
        
    def test_ftp_push_log_new_directory(self):
        target_hostname = ""
        target_port = 00
        target_username = ""
        target_password = ""
        target_path = "log_testing/example_new"
        target_filename = "2023-09-06_sample"
        client = FtpClient(target_hostname, target_port,\
            target_username, target_password)
        client.create_ftp_log_file(target_path, target_filename)
        customLog = CustomLog()
        ids = uuid.uuid5(uuid.NAMESPACE_DNS, 'python.org')
        log = customLog.set_debug_message(ids, "name", ["The sample debug message."])
        response = client.set_ftp_log_file(target_path, 
                                target_filename,
                                log)
        self.assertTrue(response)
        
    def test_ftp_push_log_data_with_other_attribute_data(self):
        target_hostname = ""
        target_port = 00
        target_username = ""
        target_password = ""
        target_path = "/log_testing/example"
        target_filename = "2023-09-06_sample"
        client = FtpClient(target_hostname, target_port,\
            target_username, target_password)
        
        customLog = CustomLog()
        id = uuid.uuid4()
        start_time = datetime.datetime.now()
        target_start_time = start_time.strftime("%H:%M:%S")
        end_time = datetime.datetime.now()
        target_end_time = end_time.strftime("%H:%M:%S")
        target_result = b"32"
        target_ground_truth = b"3"
        data_message = customLog.set_ftp_log_data(
            id, 
            target_start_time,
            target_end_time,
            target_result,
            target_ground_truth
        )
        with self.assertRaises(LogWritingException) as context:
            response = client.set_ftp_log_data(target_path, target_filename,
                                    data_message)
        self.assertTrue("Writing log failure." in str(context.exception))
    
    def test_ftp_push_log_data_with_other_attribute_data(self):
        target_hostname = ""
        target_port = 00
        target_username = ""
        target_password = ""
        target_path = "log_testing/example"
        target_filename = "2023-09-06_sample"
        client = FtpClient(target_hostname, target_port,\
            target_username, target_password)
        
        customLog = CustomLog()
        id = uuid.uuid4()
        start_time = datetime.datetime.now()
        target_start_time = start_time.strftime("%H:%M:%S")
        end_time = datetime.datetime.now()
        target_end_time = end_time.strftime("%H:%M:%S")
        target_result = b"32"
        target_ground_truth = b"3"
        data_message = customLog.set_ftp_log_data(
            id, 
            target_start_time,
            target_end_time,
            target_result,
            target_ground_truth
        )
        with self.assertRaises(InvalidAttributeException) as context:
            response = client.set_ftp_log_data(target_path, target_filename,
                                    12234)
        self.assertTrue("Attribute error." in str(context.exception))
    
    def test_ftp_push_log_data_with_none_data(self):
        target_hostname = ""
        target_port = 00
        target_username = ""
        target_password = ""
        target_path = "log_testing/example"
        target_filename = "2023-09-06_sample"
        client = FtpClient(target_hostname, target_port,\
            target_username, target_password)
        
        customLog = CustomLog()
        id = uuid.uuid4()
        start_time = datetime.datetime.now()
        target_start_time = start_time.strftime("%H:%M:%S")
        end_time = datetime.datetime.now()
        target_end_time = end_time.strftime("%H:%M:%S")
        target_result = b"32"
        target_ground_truth = b"3"
        data_message = customLog.set_ftp_log_data(
            id, 
            target_start_time,
            target_end_time,
            target_result,
            target_ground_truth
        )
        with self.assertRaises(NoneValueException) as context:
            response = client.set_ftp_log_data(target_path, target_filename,
                                    None)
        self.assertTrue("The input value should not be none." in str(context.exception))
    
    def test_ftp_push_log_data_with_empty_data(self):
        target_hostname = ""
        target_port = 00
        target_username = ""
        target_password = ""
        target_path = "log_testing/example"
        target_filename = "2023-09-06_sample"
        client = FtpClient(target_hostname, target_port,\
            target_username, target_password)
        
        customLog = CustomLog()
        id = uuid.uuid4()
        start_time = datetime.datetime.now()
        target_start_time = start_time.strftime("%H:%M:%S")
        end_time = datetime.datetime.now()
        target_end_time = end_time.strftime("%H:%M:%S")
        target_result = b"32"
        target_ground_truth = b"3"
        data_message = customLog.set_ftp_log_data(
            id, 
            target_start_time,
            target_end_time,
            target_result,
            target_ground_truth
        )
        with self.assertRaises(EmptyParameterException) as context:
            response = client.set_ftp_log_data(target_path, target_filename,
                                    b"")
        self.assertTrue("Attempt to enter empty input." in str(context.exception))
    
    def test_ftp_push_log_data_with_other_attribute_filename(self):
        target_hostname = ""
        target_port = 00
        target_username = ""
        target_password = ""
        target_path = "log_testing/example"
        target_filename = 100344
        client = FtpClient(target_hostname, target_port,\
            target_username, target_password)
        
        customLog = CustomLog()
        id = uuid.uuid4()
        start_time = datetime.datetime.now()
        target_start_time = start_time.strftime("%H:%M:%S")
        end_time = datetime.datetime.now()
        target_end_time = end_time.strftime("%H:%M:%S")
        target_result = b"32"
        target_ground_truth = b"3"
        data_message = customLog.set_ftp_log_data(
            id, 
            target_start_time,
            target_end_time,
            target_result,
            target_ground_truth
        )
        with self.assertRaises(InvalidAttributeException) as context:
            response = client.set_ftp_log_data(target_path, target_filename,
                                    data_message)
        self.assertTrue("Attribute error." in str(context.exception))
        
    def test_ftp_push_log_data_with_none_filename(self):
        target_hostname = ""
        target_port = 00
        target_username = ""
        target_password = ""
        target_path = "log_testing/example"
        target_filename = None
        client = FtpClient(target_hostname, target_port,\
            target_username, target_password)
        
        customLog = CustomLog()
        id = uuid.uuid4()
        start_time = datetime.datetime.now()
        target_start_time = start_time.strftime("%H:%M:%S")
        end_time = datetime.datetime.now()
        target_end_time = end_time.strftime("%H:%M:%S")
        target_result = b"32"
        target_ground_truth = b"3"
        data_message = customLog.set_ftp_log_data(
            id, 
            target_start_time,
            target_end_time,
            target_result,
            target_ground_truth
        )
        with self.assertRaises(NoneValueException) as context:
            response = client.set_ftp_log_data(target_path, target_filename,
                                    data_message)
        self.assertTrue("The input value should not be none." in str(context.exception))
    
    def test_ftp_push_log_data_with_empty_filename(self):
        target_hostname = ""
        target_port = 00
        target_username = ""
        target_password = ""
        target_path = "log_testing/example"
        target_filename = ""
        client = FtpClient(target_hostname, target_port,\
            target_username, target_password)
        
        customLog = CustomLog()
        id = uuid.uuid4()
        start_time = datetime.datetime.now()
        target_start_time = start_time.strftime("%H:%M:%S")
        end_time = datetime.datetime.now()
        target_end_time = end_time.strftime("%H:%M:%S")
        target_result = b"32"
        target_ground_truth = b"3"
        data_message = customLog.set_ftp_log_data(
            id, 
            target_start_time,
            target_end_time,
            target_result,
            target_ground_truth
        )
        with self.assertRaises(EmptyParameterException) as context:
            response = client.set_ftp_log_data(target_path, target_filename,
                                    data_message)
        self.assertTrue("Attempt to enter empty input." in str(context.exception))
    
    def test_ftp_push_log_data_with_other_attribute_path(self):
        target_hostname = ""
        target_port = 00
        target_username = ""
        target_password = ""
        target_path = 123445
        target_filename = "2023-09-06_sample"
        client = FtpClient(target_hostname, target_port,\
            target_username, target_password)
        
        customLog = CustomLog()
        id = uuid.uuid4()
        start_time = datetime.datetime.now()
        target_start_time = start_time.strftime("%H:%M:%S")
        end_time = datetime.datetime.now()
        target_end_time = end_time.strftime("%H:%M:%S")
        target_result = b"32"
        target_ground_truth = b"3"
        data_message = customLog.set_ftp_log_data(
            id, 
            target_start_time,
            target_end_time,
            target_result,
            target_ground_truth
        )
        with self.assertRaises(InvalidAttributeException) as context:
            response = client.set_ftp_log_data(target_path, target_filename,
                                    data_message)
        self.assertTrue("Attribute error." in str(context.exception))
    
    def test_ftp_push_log_data_with_none_path(self):
        target_hostname = ""
        target_port = 00
        target_username = ""
        target_password = ""
        target_path = None
        target_filename = "2023-09-06_sample"
        client = FtpClient(target_hostname, target_port,\
            target_username, target_password)
        
        customLog = CustomLog()
        id = uuid.uuid4()
        start_time = datetime.datetime.now()
        target_start_time = start_time.strftime("%H:%M:%S")
        end_time = datetime.datetime.now()
        target_end_time = end_time.strftime("%H:%M:%S")
        target_result = b"32"
        target_ground_truth = b"3"
        data_message = customLog.set_ftp_log_data(
            id, 
            target_start_time,
            target_end_time,
            target_result,
            target_ground_truth
        )
        with self.assertRaises(NoneValueException) as context:
            response = client.set_ftp_log_data(target_path, target_filename,
                                    data_message)
        self.assertTrue("The input value should not be none." in str(context.exception))
    
    def test_ftp_push_log_data_with_empty_path(self):
        target_hostname = ""
        target_port = 00
        target_username = ""
        target_password = ""
        target_path = ""
        target_filename = "2023-09-06_sample"
        client = FtpClient(target_hostname, target_port,\
            target_username, target_password)
        
        customLog = CustomLog()
        id = uuid.uuid4()
        start_time = datetime.datetime.now()
        target_start_time = start_time.strftime("%H:%M:%S")
        end_time = datetime.datetime.now()
        target_end_time = end_time.strftime("%H:%M:%S")
        target_result = b"32"
        target_ground_truth = b"3"
        data_message = customLog.set_ftp_log_data(
            id, 
            target_start_time,
            target_end_time,
            target_result,
            target_ground_truth
        )
        with self.assertRaises(EmptyParameterException) as context:
            response = client.set_ftp_log_data(target_path, target_filename,
                                    data_message)
        self.assertTrue("Attempt to enter empty input." in str(context.exception))
    
    def test_ftp_push_log_data(self):
        target_hostname = ""
        target_port = 00
        target_username = ""
        target_password = ""
        target_path = "log_testing/example"
        target_filename = "ABCD-2345-CDFR"
        client = FtpClient(target_hostname, target_port,\
            target_username, target_password)
        client.create_ftp_log_data(target_path, target_filename)
        
        customLog = CustomLog()
        id = uuid.uuid4()
        start_time = datetime.datetime.now()
        target_start_time = start_time.strftime("%H:%M:%S")
        end_time = datetime.datetime.now()
        target_end_time = end_time.strftime("%H:%M:%S")
        target_result = b"32"
        target_ground_truth = b"3"
        data_message = customLog.set_ftp_log_data(
            id, 
            target_start_time,
            target_end_time,
            target_result,
            target_ground_truth
        )
        
        response = client.set_ftp_log_data(target_path, target_filename,
                                data_message)
        self.assertTrue(response)
    
    def test_ftp_log_file_creation_with_other_none_filename(self):
        target_hostname = ""
        target_port = 00
        target_username = ""
        target_password = ""
        client = FtpClient(target_hostname, target_port,\
            target_username, target_password)
        target_path = "example/sa"
        target_filename = None
        with self.assertRaises(FTPFileCreationException) as context:
            client.create_ftp_log_file(target_path, target_filename)
        self.assertTrue("File or folder creation error." in str(context.exception))
    
    def test_ftp_log_file_creation_with_other_attribute_filename(self):
        target_hostname = ""
        target_port = 00
        target_username = ""
        target_password = ""
        client = FtpClient(target_hostname, target_port,\
            target_username, target_password)
        target_path = "example/sa"
        target_filename = []
        with self.assertRaises(FTPFileCreationException) as context:
            client.create_ftp_log_file(target_path, target_filename)
        self.assertTrue("File or folder creation error." in str(context.exception))
    
    def test_ftp_log_file_creation_with_empty_filename(self):
        target_hostname = ""
        target_port = 00
        target_username = ""
        target_password = ""
        client = FtpClient(target_hostname, target_port,\
            target_username, target_password)
        target_path = "example/sa"
        target_filename = ""
        with self.assertRaises(FTPFileCreationException) as context:
            client.create_ftp_log_file(target_path, target_filename)
        self.assertTrue("File or folder creation error." in str(context.exception))
    
    def test_ftp_log_file_creation_with_other_attribute_file_path2(self):
        target_hostname = ""
        target_port = 00
        target_username = ""
        target_password = ""
        client = FtpClient(target_hostname, target_port,\
            target_username, target_password)
        target_path = 1234
        target_filename = "sample"
        with self.assertRaises(FTPFileCreationException) as context:
            client.create_ftp_log_file(target_path, target_filename)
        self.assertTrue("File or folder creation error." in str(context.exception))
    
    def test_ftp_log_file_creation_with_other_attribute_file_path(self):
        target_hostname = ""
        target_port = 00
        target_username = ""
        target_password = ""
        client = FtpClient(target_hostname, target_port,\
            target_username, target_password)
        target_path = []
        target_filename = "sample"
        with self.assertRaises(FTPFileCreationException) as context:
            client.create_ftp_log_file(target_path, target_filename)
        self.assertTrue("File or folder creation error." in str(context.exception))
    
    def test_ftp_log_file_creation_with_none_file_path(self):
        target_hostname = ""
        target_port = 00
        target_username = ""
        target_password = ""
        client = FtpClient(target_hostname, target_port,\
            target_username, target_password)
        target_path = None
        target_filename = "sample"
        with self.assertRaises(FTPFileCreationException) as context:
            client.create_ftp_log_file(target_path, target_filename)
        self.assertTrue("File or folder creation error." in str(context.exception))
    
    def test_ftp_log_file_creation_with_invalid_path(self):
        target_hostname = ""
        target_port = 00
        target_username = ""
        target_password = ""
        client = FtpClient(target_hostname, target_port,\
            target_username, target_password)
        target_path = "/log_testing/testing"
        target_filename = "sample"
        with self.assertRaises(FTPFileCreationException) as context:
            client.create_ftp_log_file(target_path, target_filename)
        self.assertTrue("File or folder creation error." in str(context.exception))
    
    def test_ftp_log_file_creation(self):
        target_hostname = ""
        target_port = 00
        target_username = ""
        target_password = ""
        client = FtpClient(target_hostname, target_port,\
            target_username, target_password)
        target_path = "log_testing/testing"
        target_filename = "sample"
        response = client.create_ftp_log_file(target_path, target_filename)
        self.assertIn(response, [True, False])
    
    def test_ftp_file_server_creation_with_other_attribute_filename(self):
        target_hostname = ""
        target_port = 00
        target_username = ""
        target_password = ""
        client = FtpClient(target_hostname, target_port,\
            target_username, target_password)
        target_path = "log_testing/testing"
        target_filename = []
        with self.assertRaises(FTPFileCreationException) as context:
            client.create_ftp_log_data(target_path, target_filename)
        self.assertTrue("File or folder creation error." in str(context.exception))
    
    def test_ftp_file_server_creation_with_none_filename(self):
        target_hostname = ""
        target_port = 00
        target_username = ""
        target_password = ""
        client = FtpClient(target_hostname, target_port,\
            target_username, target_password)
        target_path = "log_testing/testing"
        target_filename = None
        with self.assertRaises(FTPFileCreationException) as context:
            client.create_ftp_log_data(target_path, target_filename)
        self.assertTrue("File or folder creation error." in str(context.exception))
    
    def test_ftp_file_server_creation_with_empty_filename(self):
        target_hostname = ""
        target_port = 00
        target_username = ""
        target_password = ""
        client = FtpClient(target_hostname, target_port,\
            target_username, target_password)
        target_path = "log_testing/testing"
        target_filename = ""
        with self.assertRaises(FTPFileCreationException) as context:
            client.create_ftp_log_data(target_path, target_filename)
        self.assertTrue("File or folder creation error." in str(context.exception))
    
    def test_ftp_file_server_creation_with_empty_path(self):
        target_hostname = ""
        target_port = 00
        target_username = ""
        target_password = ""
        client = FtpClient(target_hostname, target_port,\
            target_username, target_password)
        target_path = ""
        target_filename = "ABCD_12345_EDFT"
        with self.assertRaises(FTPFileCreationException) as context:
            client.create_ftp_log_data(target_path, target_filename)
        self.assertTrue("File or folder creation error." in str(context.exception))
    
    def test_ftp_file_server_creation_with_none_path(self):
        target_hostname = ""
        target_port = 00
        target_username = ""
        target_password = ""
        client = FtpClient(target_hostname, target_port,\
            target_username, target_password)
        target_path = None
        target_filename = "ABCD_12345_EDFT"
        with self.assertRaises(FTPFileCreationException) as context:
            client.create_ftp_log_data(target_path, target_filename)
        self.assertTrue("File or folder creation error." in str(context.exception))
    
    def test_ftp_file_server_creation_with_invalid_path(self):
        target_hostname = ""
        target_port = 00
        target_username = ""
        target_password = ""
        client = FtpClient(target_hostname, target_port,\
            target_username, target_password)
        target_path = "/log_testing/log"
        target_filename = "ABCD_12345_EDFT"
        with self.assertRaises(FTPFileCreationException) as context:
            client.create_ftp_log_data(target_path, target_filename)
        self.assertTrue("File or folder creation error." in str(context.exception))
    
    def test_ftp_file_server_creation(self):
        target_hostname = ""
        target_port = 00
        target_username = ""
        target_password = ""
        client = FtpClient(target_hostname, target_port,\
            target_username, target_password)
        target_path = "log_testing/log"
        target_filename = "ABCD_12345_EDFT"
        response = client.create_ftp_log_data(target_path, target_filename)
        self.assertIn(response, [True, False, None])
    
    def test_ftp_log_file_creation_with_wrong_file_path(self):
        target_hostname = ""
        target_port = 00
        target_username = ""
        target_password = ""
        client = FtpClient(target_hostname, target_port,\
            target_username, target_password)
        target_path = 1234
        target_filename = "ABCD_12345_EDFT"
        with self.assertRaises(FTPFileCreationException) as context:
            client.create_ftp_log_file(target_path, target_filename)
        self.assertTrue("File or folder creation error." in str(context.exception))
        
    def test_ftp_file_creation_with_wrong_file_path(self):
        target_hostname = ""
        target_port = 00
        target_username = ""
        target_password = ""
        client = FtpClient(target_hostname, target_port,\
            target_username, target_password)
        target_path = 1234
        target_filename = "ABCD_12345_EDFT"
        with self.assertRaises(FTPFileCreationException) as context:
            client.create_ftp_log_data(target_path, target_filename)
        self.assertTrue("File or folder creation error." in str(context.exception))
        
    def test_ftp_file_server_creation_again(self):
        target_hostname = ""
        target_port = 00
        target_username = ""
        target_password = ""
        client = FtpClient(target_hostname, target_port,\
            target_username, target_password)
        target_path = "log_testing/log"
        target_filename = "ABCD_12345_EDFT"
        response = client.create_ftp_log_data(target_path, target_filename)
        self.assertIn(response, [True, False, None])
    
    def test_ftp_connection(self):
        target_hostname = ""
        target_port = 00
        target_username = ""
        target_password = ""
        client = FtpClient(target_hostname, target_port,\
            target_username, target_password)
        self.assertIsNotNone(client)
    
    def test_ftp_connection_with_wrong_username(self):
        target_hostname = ""
        target_port = 00
        target_username = ""
        target_password = None
        with self.assertRaises(FTPConnectionFailedException) as context:
            FtpClient(target_hostname, target_port,\
            target_username, target_password)
        self.assertTrue("FTP Server Connection Failure." in str(context.exception))    
    
    def test_ftp_connection_with_wrong_username(self):
        target_hostname = ""
        target_port = 00
        target_username = None
        target_password = "JtP$dsds887hP"
        with self.assertRaises(InvalidFTPUserNameException) as context:
            FtpClient(target_hostname, target_port,\
            target_username, target_password)
        self.assertTrue("Invalid FTP Username." in str(context.exception))
        
    def test_ftp_connection_with_num_password(self):
        target_hostname = ""
        target_port = 00
        target_username = ""
        target_password = 876
        with self.assertRaises(InvalidFTPPasswordException) as context:
            FtpClient(target_hostname, target_port,\
            target_username, target_password)
        self.assertTrue("Invalid FTP Password." in str(context.exception))
        
    def test_ftp_connection_with_wrong_password(self):
        target_hostname = ""
        target_port = 00
        target_username = ""
        target_password = "sdfg"
        with self.assertRaises(FTPConnectionFailedException) as context:
            FtpClient(target_hostname, target_port,\
                target_username, target_password)
        self.assertTrue("FTP Server Connection Failure." in str(context.exception))
        
    def test_ftp_connection_with_none_username(self):
        target_hostname = ""
        target_port = 00
        target_username = None
        target_password = ""
        with self.assertRaises(InvalidFTPUserNameException) as context:
            FtpClient(target_hostname, target_port,\
            target_username, target_password)
        self.assertTrue("Invalid FTP Username." in str(context.exception))
        
    def test_ftp_connection_with_none_port(self):
        target_hostname = ""
        target_port = None
        target_username = ""
        target_password = ""
        with self.assertRaises(InvalidFTPPortNumberException) as context:
            FtpClient(target_hostname, target_port,\
            target_username, target_password)
        self.assertTrue("Invalid FTP Port Number." in str(context.exception)) 
        
    def test_fto_connection_wrong_port(self):
        target_hostname = ""
        target_port = 290
        target_username = ""
        target_password = ""
        with self.assertRaises(FTPConnectionFailedException) as context:
            FtpClient(target_hostname, target_port,\
            target_username, target_password)
        self.assertTrue("FTP Server Connection Failure." in str(context.exception)) 
    
    def test_ftp_connection_with_wrong_hostname(self):
        target_hostname = "1.2.3.323"
        target_port = 00
        target_username = ""
        target_password = ""
        with self.assertRaises(InvalidFTPHostNameException) as context:
            FtpClient(target_hostname, target_port,\
            target_username, target_password)
        self.assertTrue("Invalid FTP Host name." in str(context.exception))    
    
    def test_ftp_connection_with_other_attribute_hostname(self):
        target_hostname = []
        target_port = 00
        target_username = ""
        target_password = ""
        with self.assertRaises(InvalidFTPHostNameException) as context:
            FtpClient(target_hostname, target_port,\
            target_username, target_password)
        self.assertTrue("Invalid FTP Host name." in str(context.exception))
    
    def test_ftp_connection_with_none_hostname(self):
        target_hostname = None
        target_port = 00
        target_username = ""
        target_password = ""
        with self.assertRaises(InvalidFTPHostNameException) as context:
            FtpClient(target_hostname, target_port,\
            target_username, target_password)
        self.assertTrue("Invalid FTP Host name." in str(context.exception))
        
    def test_ftp_connection_with_empty_hostname(self):
        target_hostname = ""
        target_port = 00
        target_username = ""
        target_password = ""
        with self.assertRaises(InvalidFTPHostNameException) as context:
            FtpClient(target_hostname, target_port,\
            target_username, target_password)
        self.assertTrue("Invalid FTP Host name." in str(context.exception))
        
if __name__ == "__main__":
    logging.basicConfig(stream=sys.stderr)
    logging.getLogger("logTest").setLevel(logging.DEBUG)
    unittest.main() 