import os
from opencage.geocoder import OpenCageGeocode
from logger_local.LoggerComponentEnum import LoggerComponentEnum
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

class Country:

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
