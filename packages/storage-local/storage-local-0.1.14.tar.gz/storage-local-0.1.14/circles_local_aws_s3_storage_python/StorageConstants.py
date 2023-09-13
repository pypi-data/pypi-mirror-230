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


PROFILE_IMAGE = 1
COVERAGE_IMAGE = 2
PERSONAL_INTODUCTION_VIDEO = 3
SCANNED_DRIVING_LICENSE = 4
SCANNED_PASSPORT = 5
STORAGE_TYPE_ID = 1
FILE_TYPE_ID = 1
EXTENSION_ID = 1