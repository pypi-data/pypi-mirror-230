from logger_local.LoggerComponentEnum import LoggerComponentEnum

USER_LOCAL_PYTHON_PACKAGE_COMPONENT_ID = 207
USER_LOCAL_PYTHON_PACKAGE_COMPONENT_NAME = "storage-local-python-package"


OBJECT_TO_INSERT_CODE = {
    'component_id': USER_LOCAL_PYTHON_PACKAGE_COMPONENT_ID,
    'component_name': USER_LOCAL_PYTHON_PACKAGE_COMPONENT_NAME,
    'component_category': LoggerComponentEnum.ComponentCategory.Code.value,
    'developer_email': 'tal.g@circ.zone'
}

OBJECT_TO_INSERT_TEST = {
    'component_id': USER_LOCAL_PYTHON_PACKAGE_COMPONENT_ID,
    'component_name': USER_LOCAL_PYTHON_PACKAGE_COMPONENT_NAME,
    'component_category': LoggerComponentEnum.ComponentCategory.Unit_Test.value,
    'testing_framework': LoggerComponentEnum.testingFramework.pytest.value,
    'developer_email': 'tal.g@circ.zone'
}


# File-Type according to storage.file_type_ml_table
# TODO: Add _FILE_TYPE_ID suffix to all those
PROFILE_IMAGE = 1
COVERAGE_IMAGE = 2
PERSONAL_INTODUCTION_VIDEO = 3
SCANNED_DRIVING_LICENSE = 4
SCANNED_PASSPORT = 5

# TODO Should we change this to TEST_STORAGE_FILE_TYPE_ID?
STORAGE_TYPE_ID = 1
FILE_TYPE_ID = 1

# TODO Add all values from storage.file_extension_table
# TODO Change this to TEST_EXTENSION_ID
EXTENSION_ID = 1
