from logger_local.LoggerComponentEnum import LoggerComponentEnum

PROFILE_REACTION_LOCAL_PYTHON_PACKAGE_COMPONENT_ID = 169
PROFILE_REACTION_LOCAL_PYTHON_PACKAGE_COMPONENT_NAME = 'profile_reaction_local_python_package'

OBJECT_TO_INSERT_CODE = {
    'component_id': PROFILE_REACTION_LOCAL_PYTHON_PACKAGE_COMPONENT_ID,
    'component_name': PROFILE_REACTION_LOCAL_PYTHON_PACKAGE_COMPONENT_NAME,
    'component_category': LoggerComponentEnum.ComponentCategory.Code.value,
    'developer_email': 'tal.g@circ.zone'
}

OBJECT_TO_INSERT_TESTS = {
    'component_id': PROFILE_REACTION_LOCAL_PYTHON_PACKAGE_COMPONENT_ID,
    'component_name': PROFILE_REACTION_LOCAL_PYTHON_PACKAGE_COMPONENT_NAME,
    'component_category': LoggerComponentEnum.ComponentCategory.Unit_Test.value,
    'testing_framework': LoggerComponentEnum.testingFramework.pytest.value,
    'developer_email': 'tal.g@circ.zone'
}

PROFILE_REACTION_DATABASE_NAME = "profile_reaction"
PROFILE_REACTION_TABLE_NAME = "profile_reaction_table"
PROFILE_REACTION_VIEW_NAME = "profile_reaction_view"
PROFILE_REACTION_ID_COLUMN_NAME = "profile_reaction_id"
PROFILE_ID_COLUMN_NAME = "profile_id"
REACTION_ID_COLUMN_NAME = "reaction_id"

PROFILE_REACTION_ID_COLUMN_NUMBER = 0
PROFILE_ID_COLUMN_NUMBER = 1
REACTION_ID_COLUMN_NUMBER = 2
