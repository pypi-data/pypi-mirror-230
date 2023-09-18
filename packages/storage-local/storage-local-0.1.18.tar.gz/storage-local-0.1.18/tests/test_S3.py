
import sys
import time
import boto3
import os
import unittest
from dotenv.main import load_dotenv
sys.path.append(os.getcwd())
from circles_local_aws_s3_storage_python.AWSStorage import AwsS3Storage # noqa: E402
from circles_local_aws_s3_storage_python.StorageDB import StorageDB # noqa: E402
load_dotenv()

# TODO: Get the debug from Environment using our method in Python util/SDK
debug=False


PROFILE_ID = 1


class s3_test(unittest.TestCase):

    def setUp(self) -> None:
        # TODO: Write to Logger with Storage_Testing Component Id
        if (debug): print('Bucket=', end='')
        if (debug): print(os.getenv("BUCKET_NAME")) # TODO: Change to AWS_STORAGE_BUCKET_NAME
        if (debug): print('Region=',  end='')
        if (debug): print(os.getenv("REGION"))

        self.s3_resource = boto3.resource('s3')
        self.awsS3 = AwsS3Storage(
            os.getenv("BUCKET_NAME"), os.getenv("REGION"))
        self.test_file_contents = b'this it a file test!'
        self.database = StorageDB()

    def test_upload(self):
        cwd = os.getcwd()
        # TODO: Use consts
        filepath = os.path.join(cwd, 'tests/test.txt')
        # TODO: Use consts
        functionId = self.awsS3.upload_file(
            filepath, 'test.txt', 'python/', PROFILE_ID)
        s3_object = self.s3_resource.Object(
            os.getenv("BUCKET_NAME"), 'python/test.txt')
        s3_file_contents = s3_object.get()['Body'].read()
        self.assertEqual(s3_file_contents, self.test_file_contents)
        actualId = self.database.getLastId()
        self.assertEqual(functionId, actualId)

    def test_download(self):
        # As I'm not sure setUp was running and we need to run test_upload() before running test_download()
        self.setUp()
        self.test_upload()
        
        cwd = os.getcwd()
        self.awsS3.download_file(
            'python/test.txt', cwd+'/test.txt')
        assert os.path.isfile(
            cwd+'/test.txt')

    def test_logical_delete(self):
        self.awsS3.delete_file('python/', 'test.txt', PROFILE_ID)
        time.sleep(1)
        result = self.database.getEndTimeStampFromDB(
            'python/', 'test.txt', os.getenv("REGION"))
        self.assertIsNone(result)


if __name__ == '__main__':
    unittest.main()
