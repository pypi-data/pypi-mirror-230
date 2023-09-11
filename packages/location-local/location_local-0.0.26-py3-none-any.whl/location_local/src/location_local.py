from typing import Dict
from logger_local.LoggerComponentEnum import LoggerComponentEnum
from dotenv import load_dotenv
load_dotenv()
from circles_local_database_python.generic_crud import GenericCRUD   # noqa: E402
from circles_local_database_python.connector import Connector   # noqa: E402
from logger_local.Logger import Logger  # noqa: E402

LOCATION_LOCAL_PYTHON_PACKAGE_COMPONENT_ID = 113
LOCATION_LOCAL_PYTHON_PACKAGE_COMPONENT_NAME = 'location/src/location.py'


object_to_insert = {
    'component_id': LOCATION_LOCAL_PYTHON_PACKAGE_COMPONENT_ID,
    'component_name': LOCATION_LOCAL_PYTHON_PACKAGE_COMPONENT_NAME,
    'component_category': LoggerComponentEnum.ComponentCategory.Code.value,
    'developer_email': 'tal.g@circ.zone'
}

logger = Logger.create_logger(object=object_to_insert)


class LocationLocal(GenericCRUD):
    def __init__(self):
        INIT_METHOD_NAME = '__init__'
        logger.start(INIT_METHOD_NAME)

        self.connector = Connector.connect("location")
        self.cursor = self.connector.cursor()

        logger.end(INIT_METHOD_NAME)

    def get_location_table_ids(
            self, neighborhood: str, county: str, region: str, state: str, country: str) -> tuple(
            [int, int, int, int, int]):
        GET_LOCATION_TABLE_IDS_METHOD_NAME = 'get_location_table_ids'
        logger.start(GET_LOCATION_TABLE_IDS_METHOD_NAME)
        neighborhood_id, county_id, region_id, state_id, country_id = None, None, None, None, None
        self.cursor.execute(
            "SELECT neighborhood_id from neighborhood_ml_table WHERE title = '{}'".format(neighborhood))
        result = self.cursor.fetchone()
        if result is not None:
            neighborhood_id, = result
        self.cursor.execute(
            "SELECT county_id from county_ml_table WHERE title = '{}'".format(county))
        result = self.cursor.fetchone()
        if result is not None:
            county_id, = result
        self.cursor.execute(
            "SELECT region_id from region_ml_table WHERE title = '{}'".format(region))
        result = self.cursor.fetchone()
        if result is not None:
            region_id, = result
        self.cursor.execute(
            "SELECT state_id from state_ml_table WHERE state_name = '{}'".format(state))
        result = self.cursor.fetchone()
        if result is not None:
            state_id, = result
        self.cursor.execute(
            "SELECT id from country_table WHERE `name` = '{}'".format(country))
        result = self.cursor.fetchone()
        if result is not None:
            country_id, = result

        logger.end(
            GET_LOCATION_TABLE_IDS_METHOD_NAME,
            object={"neighborhood_id": neighborhood_id, "county_id": county_id, "region_id": region_id,
                    "state_id": state_id, "country_id": country_id})
        return (neighborhood_id, county_id, region_id, state_id, country_id)

    def insert_location(self, data: Dict[str, any], lang_code="en", is_approved=True):
        INSERT_LOCATION_METHOD_NAME = 'insert_location'
        logger.start(INSERT_LOCATION_METHOD_NAME)
        (neighborhood_id, county_id, region_id, state_id, country_id) = self._check_location_details_insert_if_not_exist(
            data["coordinate"], (data["neighborhood"], data["county"], data["region"], data["state"], data["country"]), lang_code)

        query_insert = "INSERT INTO location_table (coordinate, address_local_language, address_english," \
            " neighborhood_id, county_id, region_id, state_id, country_id, postal_code, plus_code, is_approved)" \
            " VALUES (POINT(%s, %s), %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
        self.cursor.execute(
            query_insert,
            (data["coordinate"]["latitude"],
             data["coordinate"]["longitude"],
             data["address_local_language"],
             data["address_english"],
             neighborhood_id, county_id, region_id, state_id, country_id, data["postal_code"],
             data["plus_code"],
             is_approved))
        self.connector.commit()

        location_id = self.cursor.lastrowid()

        logger.end(INSERT_LOCATION_METHOD_NAME)
        return location_id

    def update_location(self, location_id: int, data: Dict[str, any], lang_code: str = "en", is_approved: int = True):
        UPDATE_LOCATION_METHOD_NAME = 'update_location'
        logger.start(UPDATE_LOCATION_METHOD_NAME)
        (neighborhood_id, county_id, region_id, state_id, country_id) = self._check_location_details_insert_if_not_exist(
            data["coordinate"], (data["neighborhood"], data["county"], data["region"], data["state"], data["country"]), lang_code)

        query_update = "UPDATE location_table SET coordinate = POINT(%s, %s), address_local_language = %s, " \
            "address_english = %s, neighborhood_id = %s, county_id = %s, region_id = %s, state_id = %s," \
            " country_id = %s, postal_code = %s, plus_code = %s WHERE location_id = %s"
        self.cursor.execute(
            query_update,
            (data["coordinate"]["latitude"],
             data["coordinate"]["longitude"],
             data["address_local_language"],
             data["address_english"],
             neighborhood_id, county_id, region_id, state_id, country_id, data["postal_code"],
             data["plus_code"],
             location_id))
        self.connector.commit()
        logger.end(UPDATE_LOCATION_METHOD_NAME)

    def read_location(self, location_id: int) -> tuple([Dict[str, float], str, str, str, str, str, str, str, str, str]):
        READ_LOCATION_METHOD_NAME = 'read_location'
        logger.start(READ_LOCATION_METHOD_NAME)

        query_get = '''SELECT ST_X(l.coordinate), ST_Y(l.coordinate), l.address_local_language, l.address_english, n.title, c.title, 
                            r.title, s.state_name, co.name, l.postal_code, l.plus_code 
                            FROM location_view l 
                            JOIN neighborhood_ml_table n ON n.neighborhood_id = l.neighborhood_id
                            JOIN county_ml_table c ON c.county_id = l.county_id
                            JOIN region_ml_table r ON r.region_id = l.region_id
                            JOIN state_ml_table s ON s.state_id = l.state_id 
                            JOIN country_table co ON co.id = l.country_id 
                            WHERE l.location_id = %s'''
        self.cursor.execute(query_get, (location_id,))
        result = None
        coordinate = None
        result = self.cursor.fetchone()
        if result is None:
            logger.end(READ_LOCATION_METHOD_NAME, object={"result": result})
            return None

        (latitude, longitude, address_local_language, address_english, neighborhood,
         county, region, state, country, postal_code, plus_code) = result
        coordinate = {"latitude": latitude, "longitude": longitude}

        logger.end(
            READ_LOCATION_METHOD_NAME,
            object={"address_local_language": address_local_language, "address_english": address_english,
                    "neighborhood": neighborhood, "county": county, "region": region, "state": state,
                    "country": country, "postal_code": postal_code, "plus_code": plus_code})
        return (coordinate, address_local_language, address_english, neighborhood, county, region,
                state, country, postal_code, plus_code)

    def delete_location(self, location_id: int):
        DELETE_LOCATION_METHOD_NAME = 'delete_location'
        logger.start(DELETE_LOCATION_METHOD_NAME)

        query_update = "UPDATE location_table SET end_timestamp = NOW() WHERE location_id = %s"
        self.cursor.execute(query_update, (location_id,))

        self.connector.commit()
        logger.end(DELETE_LOCATION_METHOD_NAME)

    def insert_neighborhood(
            self, coordinate: Dict[str, float],
            neighborhood: str, lang_code: str = 'en', title_approved: int = True):
        INSERT_NEIGHBORHOOD_METHOD_NAME = 'insert_neighborhood'
        logger.start(INSERT_NEIGHBORHOOD_METHOD_NAME)
        query_insert = "INSERT IGNORE INTO neighborhood_table (coordinate) VALUES (POINT(%s, %s))"
        self.cursor.execute(
            query_insert, (coordinate["latitude"], coordinate["longitude"]))
        neighborhood_id = self.cursor.lastrowid()
        query_insert_ml = "INSERT IGNORE INTO neighborhood_ml_table (neighborhood_id, lang_code," \
            " title, title_approved) VALUES (%s, %s, %s, %s)"
        self.cursor.execute(query_insert_ml, (neighborhood_id,
                            lang_code, neighborhood, title_approved))
        self.connector.commit()
        logger.end(INSERT_NEIGHBORHOOD_METHOD_NAME)
        return neighborhood_id

    def insert_county(
            self, coordinate: Dict[str, float],
            county: str, lang_code: str = 'en', title_approved: int = True):
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

    def insert_region(
            self, coordinate: Dict[str, float],
            region: str, lang_code: str = 'en', title_approved: int = True):
        INSERT_REGION_METHOD_NAME = 'insert_region'
        logger.start(INSERT_REGION_METHOD_NAME)
        query_insert = "INSERT IGNORE INTO region_table (coordinate) VALUES (POINT(%s, %s))"
        self.cursor.execute(
            query_insert, (coordinate["latitude"], coordinate["longitude"]))
        region_id = self.cursor.lastrowid()
        query_insert_ml = "INSERT IGNORE INTO region_ml_table (region_id, lang_code, title, title_approved)" \
            " VALUES (%s, %s, %s, %s)"
        self.cursor.execute(query_insert_ml, (region_id,
                            lang_code, region, title_approved))
        self.connector.commit()
        logger.end(INSERT_REGION_METHOD_NAME)
        return region_id

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

    def _check_location_details_insert_if_not_exist(
            self, coordinate: Dict[str, float],
            location_details: tuple([str, str, str, str, str]),
            lang_code: str = 'en') -> tuple(
            [int, int, int, int, int]):
        CHECK_LOCATION_DETAILS_INSERT_IF_NOT_EXIST_METHOD_NAME = '_check_location_details_insert_if_not_exist'
        logger.start(CHECK_LOCATION_DETAILS_INSERT_IF_NOT_EXIST_METHOD_NAME)
        (neighborhood, county, region, state, country) = location_details
        ids = self.get_location_table_ids(
            neighborhood, county, region, state, country)
        if ids is None:
            return None
        (neighborhood_id, county_id, region_id, state_id, country_id) = ids
        if neighborhood_id is None:
            neighborhood_id = self.insert_neighborhood(
                coordinate, neighborhood, lang_code)
        if county_id is None:
            county_id = self.insert_county(coordinate, county, lang_code)
        if region_id is None:
            region_id = self.insert_region(coordinate, region, lang_code)
        if state_id is None:
            state_id = self.insert_state(coordinate, state, lang_code)
        if country_id is None:
            country_id = self.insert_country(coordinate, country, lang_code)
        logger.end(CHECK_LOCATION_DETAILS_INSERT_IF_NOT_EXIST_METHOD_NAME)
        return (neighborhood_id, county_id, region_id, state_id, country_id)
