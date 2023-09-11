from logger_local.LoggerComponentEnum import LoggerComponentEnum
from dotenv import load_dotenv
load_dotenv()
from circles_local_database_python.generic_crud import GenericCRUD  # noqa: E402
from circles_local_database_python.connector import Connector   # noqa: E402
from logger_local.Logger import Logger  # noqa: E402

LOCATION_LOCAL_PYTHON_PACKAGE_COMPONENT_ID = 113
LOCATION_LOCAL_PYTHON_PACKAGE_COMPONENT_NAME = 'location/src/state.py'

object_to_insert = {
    'component_id': LOCATION_LOCAL_PYTHON_PACKAGE_COMPONENT_ID,
    'component_name': LOCATION_LOCAL_PYTHON_PACKAGE_COMPONENT_NAME,
    'component_category': LoggerComponentEnum.ComponentCategory.Code.value,
    'developer_email': 'tal.g@circ.zone'
}

logger = Logger.create_logger(object=object_to_insert)

class state(GenericCRUD):
    def __init__(self):
        INIT_METHOD_NAME = '__init__'
        logger.start(INIT_METHOD_NAME)

        self.connector = Connector.connect("location")
        self.cursor = self.connector.cursor()

        logger.end(INIT_METHOD_NAME)


    def get_state_id(self, title):
        GET_STATE_ID_METHOD_NAME = 'get_state_id'
        logger.start(GET_STATE_ID_METHOD_NAME, object = {'title': title})

        query_get = "SELECT state_id from state_ml_table WHERE title = %s"
        self.cursor.execute(query_get, (title,))
        state_id = self.cursor.fetchone()
        if state_id is not None:
            state_id = state_id[0]

        logger.end(GET_STATE_ID_METHOD_NAME, object = {'state_id': state_id})
        return state_id