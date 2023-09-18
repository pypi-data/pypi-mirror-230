import os
import boto3

from circles_local_aws_s3_storage_python.StorageInterface import StorageInterface
from circles_local_aws_s3_storage_python.StorageDB import StorageDB
from circles_local_aws_s3_storage_python import StorageConstants

debug = False
class AwsS3Storage(StorageInterface):

    def __init__(self, bucket_name, region):
        # TODO: Add logger.start() here
        if (debug): print("Initializing AwsS3Storage bucket_name="+str(bucket_name)+' region='+str(region))
        self.region = region
        self.bucket_name = bucket_name
        self.database = StorageDB()
        if (debug): print("AWS_ACCESS_KEY_ID: " +os.getenv("AWS_ACCESS_KEY_ID"))
        if (debug): print("AWS_SECRET_ACCESS_KEY: " +os.getenv("AWS_SECRET_ACCESS_KEY"))
        aws_access_key_id = os.getenv("AWS_ACCESS_KEY_ID")
        aws_secret_access_key = os.getenv("AWS_SECRET_ACCESS_KEY")
        self.client = boto3.client('s3',
                                   aws_access_key_id=aws_access_key_id,
                                   aws_secret_access_key=aws_secret_access_key)

    # uploads file to S3

    # TODO: We should remove the created_user_id parameter and use the user-context.get_effective_profile()
    # TODO Please add types to all methods/functions
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
            # id->storage_id
            id = self.database.uploadToDatabase(
                # TODO Remove the created_user_id parameter
                # TODO Please send all parameters by name and not by location
                remote_path, filename, self.region, created_user_id, StorageConstants.STORAGE_TYPE_ID, StorageConstants.FILE_TYPE_ID, StorageConstants.EXTENSION_ID, url)  # Constants needs to be replaced by parameter
            return id
        return None

    # download a file from s3 to local_path
    def download_file(self, remote_path, local_path):
        print(self.bucket_name,remote_path,local_path)
        self.client.download_file(self.bucket_name, remote_path, local_path)

    # logical delete
    # TODO Remove updated_user_id and use user-context.get_effective_profile() instead
    # TODO Rename to delete_by_remote_path_filename()
    # TODO Make sure we have we also have delete_by_storage_id() 
    def delete_file(self, remote_path, filename, updated_user_id):
        # TODO change to delete()
        self.database.logicalDelete(
            remote_path, filename, self.region, updated_user_id)
