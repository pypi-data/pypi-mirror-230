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
from language_local_python_package.src.language_enum_class import LanguageCode  # noqa: E402


logger = Logger.create_logger(object=LocationLocalConstants.OBJECT_FOR_LOGGER_CODE)


class County(GenericCRUD):
    def __init__(self):
        INIT_METHOD_NAME = '__init__'
        logger.start(INIT_METHOD_NAME)

        self.connector = Connector.connect("location")
        self.cursor = self.connector.cursor()

        logger.end(INIT_METHOD_NAME)

    def insert_county(
            self, coordinate: Dict[str, float],
            county: str, lang_code: LanguageCode = 'en', title_approved: bool = False):
        INSERT_COUNTY_METHOD_NAME = 'insert_county'
        logger.start(INSERT_COUNTY_METHOD_NAME)
        query_insert = "INSERT IGNORE INTO county_table (coordinate) VALUES (POINT(%s, %s))"
        self.cursor.execute(
            query_insert, (coordinate["latitude"], coordinate["longitude"]))
        county_id = self.cursor.lastrowid()
        query_insert_ml = "INSERT IGNORE INTO county_ml_table (county_id, lang_code," \
            " title, title_approved) VALUES (%s, %s, %s, %s)"
        self.cursor.execute(query_insert_ml, (county_id,
                            lang_code, county, title_approved))
        self.connector.commit()
        logger.end(INSERT_COUNTY_METHOD_NAME)
        return county_id

    def get_county_id(self, title):
        GET_COUNTY_ID_METHOD_NAME = 'get_county_id'
        logger.start(GET_COUNTY_ID_METHOD_NAME, object={'title': title})

        query_get = "SELECT county_id FROM county_ml_view WHERE title = %s"
        self.cursor.execute(query_get, (title,))
        county_id = self.cursor.fetchone()
        if county_id is not None:
            county_id = county_id[0]

        logger.end(GET_COUNTY_ID_METHOD_NAME, object={'county_id': county_id})
        return county_id
