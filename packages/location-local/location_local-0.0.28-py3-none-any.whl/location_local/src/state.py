from typing import Dict
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

class State(GenericCRUD):
    def __init__(self):
        INIT_METHOD_NAME = '__init__'
        logger.start(INIT_METHOD_NAME)

        self.connector = Connector.connect("location")
        self.cursor = self.connector.cursor()

        logger.end(INIT_METHOD_NAME)

    def insert_state(
            self, coordinate: Dict[str, float],
            state: str, lang_code: str = 'en', state_name_approved: int = True):
        INSERT_STATE_METHOD_NAME = 'insert_state'
        logger.start(INSERT_STATE_METHOD_NAME)
        query_insert = "INSERT IGNORE INTO state_table (coordinate) VALUES (POINT(%s, %s))"
        self.cursor.execute(
            query_insert, (coordinate["latitude"], coordinate["longitude"]))
        state_id = self.cursor.lastrowid()
        query_insert_ml = "INSERT IGNORE INTO state_ml_table (state_id, lang_code, state_name," \
            " state_name_approved) VALUES (%s, %s, %s, %s)"
        self.cursor.execute(
            query_insert_ml, (state_id, lang_code, state, state_name_approved))
        self.connector.commit()
        logger.end(INSERT_STATE_METHOD_NAME)
        return state_id

    def get_state_id(self, state_name):
        GET_STATE_ID_METHOD_NAME = 'get_state_id'
        logger.start(GET_STATE_ID_METHOD_NAME, object = {'state_name': state_name})

        query_get = "SELECT state_id from state_ml_table WHERE state_name = %s"
        self.cursor.execute(query_get, (state_name,))
        state_id = self.cursor.fetchone()
        if state_id is not None:
            state_id = state_id[0]

        logger.end(GET_STATE_ID_METHOD_NAME, object = {'state_id': state_id})
        return state_id