import os
import sys

script_directory = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(script_directory, '../circles_local_aws_s3_storage_python'))
from StorageConstants import * # noqa: E402
from CirclesStorage import circles_storage # noqa: E402
from StorageDB import StorageDB # noqa: E402

import unittest
from dotenv.main import load_dotenv
import pytest
load_dotenv()
debug = False;

PROFILE_ID = 1
#Change this after each test
URL = "https://picsum.photos/156/300"

class circles_storage_test(unittest.TestCase):
    def setUp(self) -> None:
        self.circles_storage = circles_storage(True)
        self.db=StorageDB()
        self.test = 0
        if (debug): print("REGION:"+str(os.getenv("REGION")))

    def test_get_folder(self):
        actual_folder = self.circles_storage._get_folder(
            PROFILE_IMAGE)
        expected_folder = 'Profile Image'
        self.assertEqual(actual_folder, expected_folder)

    def test_get_region_and_folder(self):
        actual = self.circles_storage._get_region_and_folder(profile_id=PROFILE_ID,
                                                             entity_type_id=PROFILE_IMAGE)
        actual = str(actual).replace(" ", "")
        # TODO Support multi region
        expected = "['ProfileImage','us-east-1']"
        self.assertEqual(actual, expected)

    def test_put(self):
        cwd = os.getcwd()
        filepath = os.path.join(cwd, 'tests/test.txt')
        id = self.circles_storage.put(profile_id=PROFILE_ID, entity_type_id=PROFILE_IMAGE, file_name='circles_test.txt',
                                      local_file_path=filepath)
        self.assertGreater(id, 0)

    def test_download(self):
        cwd = os.getcwd()
        filepath = os.path.join(cwd, 'download_test.txt')
        self.circles_storage.download(
            entity_type_id=PROFILE_IMAGE, profile_id=PROFILE_ID, file_name='circles_test.txt', local_path=filepath)
        assert os.path.isfile(
            filepath)

    def test_download_storage_id(self):
        cwd=os.getcwd()
        filepath = os.path.join(cwd, 'download_test.txt')
        self.circles_storage.download_by_storage_id(self.db.getLastId())
        assert os.path.isfile(filepath)


    def test_save_image_in_storage_by_url(self):
        self.circles_storage.save_image_in_storage_by_url(
            URL, 'test_generic_profile_inesrt1.jpg', PROFILE_ID, PROFILE_IMAGE)

if __name__ == '__main__':
    unittest.main()
