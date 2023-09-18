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


class County(GenericCRUD):
    def __init__(self):
        logger.start()

        self.connector = Connector.connect("location")
        self.cursor = self.connector.cursor()

        logger.end()

    def insert_county(
            self, coordinate: Dict[str, float],
            county: str, lang_code: LangCode = 'en', title_approved: bool = False):
        logger.start(object={'coordinate': coordinate, 'county': county,
                     'lang_code': lang_code, 'title_approved': title_approved})
        query_insert = "INSERT IGNORE INTO county_table (coordinate) VALUES (POINT(%s, %s))"
        self.cursor.execute(
            query_insert, (coordinate["latitude"], coordinate["longitude"]))
        county_id = self.cursor.lastrowid()
        query_insert_ml = "INSERT IGNORE INTO county_ml_table (county_id, lang_code," \
            " title, title_approved) VALUES (%s, %s, %s, %s)"
        self.cursor.execute(query_insert_ml, (county_id,
                            lang_code, county, title_approved))
        self.connector.commit()
        logger.end(object={'county_id': county_id})
        return county_id

    def get_county_id(self, title):
        logger.start(object={'title': title})

        query_get = "SELECT county_id FROM county_ml_view WHERE title = %s"
        self.cursor.execute(query_get, (title,))
        county_id = self.cursor.fetchall()
        if county_id is not []:
            county_id = county_id[0][0]
        else:
            logger.end(object={'county_id': county_id})
            return None

        logger.end(object={'county_id': county_id})
        return county_id
