from logger_local.LoggerComponentEnum import LoggerComponentEnum


class LocationLocalConstants:
    LOCATION_LOCAL_PYTHON_PACKAGE_COMPONENT_ID = 113
    LOCATION_LOCAL_PYTHON_PACKAGE_COMPONENT_NAME = 'location local python package'
    OBJECT_FOR_LOGGER_CODE = {
        'component_id': LOCATION_LOCAL_PYTHON_PACKAGE_COMPONENT_ID,
        'component_name': LOCATION_LOCAL_PYTHON_PACKAGE_COMPONENT_NAME,
        'component_category': LoggerComponentEnum.ComponentCategory.Code.value,
        'developer_email': 'tal.g@circ.zone'
    }

    OBJECT_FOR_LOGGER_TEST = {
        'component_id': LOCATION_LOCAL_PYTHON_PACKAGE_COMPONENT_ID,
        'component_name': LOCATION_LOCAL_PYTHON_PACKAGE_COMPONENT_NAME,
        'component_category': LoggerComponentEnum.ComponentCategory.Unit_Test.value,
        'developer_email': 'tal.g@circ.zone'
    }

    UNKNOWN_LOCATION_ID = 37522
