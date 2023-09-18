from typing import Dict
try:
    # When running from this package
    from location_local_constants import LocationLocalConstants
except Exception:
    # When importing this module from another package
    from location_local.location_local_constants import LocationLocalConstants
from dotenv import load_dotenv
load_dotenv()
from circles_local_database_python.generic_crud import GenericCRUD  # noqa: E402
from circles_local_database_python.connector import Connector   # noqa: E402
from logger_local.Logger import Logger  # noqa: E402
from language_local.lang_code import LangCode  # noqa: E402


logger = Logger.create_logger(object=LocationLocalConstants.OBJECT_FOR_LOGGER_CODE)


class State(GenericCRUD):
    def __init__(self):
        logger.start()

        self.connector = Connector.connect("location")
        self.cursor = self.connector.cursor()

        logger.end()

    def insert_state(
            self, coordinate: Dict[str, float],
            state: str, lang_code: LangCode = 'en', state_name_approved: bool = False):
        logger.start(object={'coordinate': coordinate, 'state': state,
                     'lang_code': lang_code, 'state_name_approved': state_name_approved})
        query_insert = "INSERT IGNORE INTO state_table (coordinate) VALUES (POINT(%s, %s))"
        self.cursor.execute(
            query_insert, (coordinate["latitude"], coordinate["longitude"]))
        state_id = self.cursor.lastrowid()
        query_insert_ml = "INSERT IGNORE INTO state_ml_table (state_id, lang_code, state_name," \
            " state_name_approved) VALUES (%s, %s, %s, %s)"
        self.cursor.execute(
            query_insert_ml, (state_id, lang_code, state, state_name_approved))
        self.connector.commit()
        logger.end(object={'state_id': state_id})
        return state_id

    def get_state_id(self, state_name):
        logger.start(object={'state_name': state_name})

        query_get = "SELECT state_id FROM state_ml_view WHERE state_name = %s"
        self.cursor.execute(query_get, (state_name,))
        state_id = self.cursor.fetchall()
        if state_id is not []:
            state_id = state_id[0][0]
        else:
            logger.end(object={'state_id': state_id})
            return None

        logger.end(object={'state_id': state_id})
        return state_id
