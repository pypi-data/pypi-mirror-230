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


class Neighborhood(GenericCRUD):
    def __init__(self):
        logger.start()

        self.connector = Connector.connect("location")
        self.cursor = self.connector.cursor()

        logger.end()

    def insert_neighborhood(
            self, coordinate: Dict[str, float],
            neighborhood: str, lang_code: LangCode = 'en', title_approved: bool = False):
        logger.start(object={'coordinate': coordinate, 'neighborhood': neighborhood,
                     'lang_code': lang_code, 'title_approved': title_approved})
        query_insert = "INSERT IGNORE INTO neighborhood_table (coordinate) VALUES (POINT(%s, %s))"
        self.cursor.execute(
            query_insert, (coordinate["latitude"], coordinate["longitude"]))
        neighborhood_id = self.cursor.lastrowid()
        query_insert_ml = "INSERT IGNORE INTO neighborhood_ml_table (neighborhood_id, lang_code," \
            " title, title_approved) VALUES (%s, %s, %s, %s)"
        self.cursor.execute(query_insert_ml, (neighborhood_id,
                            lang_code, neighborhood, title_approved))
        self.connector.commit()
        logger.end(object={'neighborhood_id': neighborhood_id})
        return neighborhood_id

    def get_neighborhood_id(self, title):
        logger.start(object={'title': title})

        query_get = "SELECT neighborhood_id FROM neighborhood_ml_view WHERE title = %s"
        self.cursor.execute(query_get, (title,))
        neighborhood_id = self.cursor.fetchall()
        if neighborhood_id is not []:
            neighborhood_id = neighborhood_id[0][0]
        else:
            logger.end(object={'neighborhood_id': neighborhood_id})
            return None

        logger.end(object={'neighborhood_id': neighborhood_id})
        return neighborhood_id
