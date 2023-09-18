import os
import boto3

from circles_local_aws_s3_storage_python.StorageInterface import StorageInterface
from circles_local_aws_s3_storage_python.StorageDB import StorageDB
from circles_local_aws_s3_storage_python import StorageConstants


# TODO: use our DebugMode class to turn on/off debug messages

class AwsS3Storage(StorageInterface):

    def __init__(self, bucket_name, region):
        # TODO: Add logger.start() here
        self.region = region
        self.bucket_name = bucket_name
        self.database = StorageDB()
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID")
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY")
        self.client = boto3.client('s3',
                                   aws_access_key_id=aws_access_key_id,
                                   aws_secret_access_key=aws_secret_access_key)

    # uploads file to S3

    def upload_file(self, local_path, filename, remote_path, created_user_id, url = None):
        read_binary = 'rb'
        with open(local_path, read_binary) as file_obj:
            file_contents = file_obj.read()

        # Upload the file to S3 with the CRC32 checksum
        response = self.client.put_object(
            Bucket=self.bucket_name,
            Key=remote_path+filename,
            Body=file_contents,
            ChecksumAlgorithm='crc32'
        )
        if 'ETag' in response:
            id = self.database.uploadToDatabase(
                remote_path, filename, self.region, created_user_id, StorageConstants.STORAGE_TYPE_ID, StorageConstants.FILE_TYPE_ID, StorageConstants.EXTENSION_ID, url)  # Constants needs to be replaced by parameter
            return id
        return None

    # download a file from s3 to local_path
    def download_file(self, remote_path, local_path):
        print(self.bucket_name,remote_path,local_path)
        self.client.download_file(self.bucket_name, remote_path, local_path)

    # logical delete
    def delete_file(self, remote_path, filename, updated_user_id):
        self.database.logicalDelete(
            remote_path, filename, self.region, updated_user_id)
