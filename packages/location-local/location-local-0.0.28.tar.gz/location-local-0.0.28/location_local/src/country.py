import os
from typing import Dict
from opencage.geocoder import OpenCageGeocode
from logger_local.LoggerComponentEnum import LoggerComponentEnum
from circles_local_database_python.generic_crud import GenericCRUD
from circles_local_database_python.connector import Connector
from dotenv import load_dotenv
load_dotenv()
from logger_local.Logger import Logger  # noqa: E402
api_key = os.getenv("OPENCAGE_KEY")

LOCATION_LOCAL_PYTHON_PACKAGE_COMPONENT_ID = 113
LOCATION_LOCAL_PYTHON_PACKAGE_COMPONENT_NAME = 'location/src/location.py'

object_to_insert = {
    'component_id': LOCATION_LOCAL_PYTHON_PACKAGE_COMPONENT_ID,
    'component_name': LOCATION_LOCAL_PYTHON_PACKAGE_COMPONENT_NAME,
    'component_category': LoggerComponentEnum.ComponentCategory.Code.value,
    'developer_email': 'tal.g@circ.zone'
}

logger = Logger.create_logger(object=object_to_insert)

class Country(GenericCRUD):
    def __init__(self):
        INIT_METHOD_NAME = '__init__'
        logger.start(INIT_METHOD_NAME)

        self.connector = Connector.connect("location")
        self.cursor = self.connector.cursor()

        logger.end(INIT_METHOD_NAME)

    def insert_country(
            self, coordinate: Dict[str, float],
            country: str, lang_code: str = 'en', title_approved: int = True):
        INSERT_COUNTRY_METHOD_NAME = 'insert_country'
        logger.start(INSERT_COUNTRY_METHOD_NAME)
        query_insert = "INSERT IGNORE INTO country_table (coordinate) VALUES (POINT(%s, %s))"
        self.cursor.execute(
            query_insert, (coordinate["latitude"], coordinate["longitude"]))
        country_id = self.cursor.lastrowid()
        query_insert_ml = "INSERT IGNORE INTO country_ml_table (country_id, lang_code, name," \
            " title_approved) VALUES (%s, %s, %s, %s)"
        self.cursor.execute(query_insert_ml, (country_id,
                            lang_code, country, title_approved))
        self.connector.commit()
        logger.end(INSERT_COUNTRY_METHOD_NAME)
        return country_id
    
    def get_country_id(self, name):
        GET_COUNTRY_ID_METHOD_NAME = 'get_country_id'
        logger.start(GET_COUNTRY_ID_METHOD_NAME, object = {'name': name})

        query_get = "SELECT id from country_table WHERE `name` = %s"
        self.cursor.execute(query_get, (name,))
        country_id = self.cursor.fetchone()
        if country_id is not None:
            country_id = country_id[0]

        logger.end(GET_COUNTRY_ID_METHOD_NAME, object = {'country_id': country_id})
        return country_id

    @staticmethod
    def get_country_name(location):
        GET_COUNTRY_NAME_METHOD_NAME = 'get_country_name'
        # Create a geocoder instance
        logger.start(GET_COUNTRY_NAME_METHOD_NAME, object={'location': location})

        # Define the city or state
        geocoder = OpenCageGeocode(api_key)

        # Use geocoding to get the location details
        results = geocoder.geocode(location)

        if results and len(results) > 0:
            first_result = results[0]
            components = first_result['components']

            # Extract the country from components
            country_name = components.get('country', '')
            if not country_name:
                # If country is not found, check for country_code as an alternative
                country_name = components.get('country_code', '')
        else:
            country_name = None
            logger.error("country didnt  found for %s." % location)
        logger.end(GET_COUNTRY_NAME_METHOD_NAME, object={'country_name': country_name})
        return country_name


if __name__ == "__main__":
    pass
