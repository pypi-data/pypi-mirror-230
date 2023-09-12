import json
import logging

from semantha_sdk.rest.rest_client import RestClient
from semantha_sdk.api.semantha_api import SemanthaAPI


__PLATFORM_SERVER_API_VERSION = "v3"


def login(server_url: str, key: str = None, key_file: str = None) -> SemanthaAPI:
    """ Access the Semantha API.

    Args:
        server_url (str): URL to the Semantha server
        key (str): A valid bearer token for accessing the given url.
        key_file (str): Path to a json file providing a valid `API_Key` value for the given url.

    Returns:
        SemanthaAPI: Entry point to the Semantha API.
    """
    if(not server_url.endswith("/tt-platform-server")):
        server_url += "/tt-platform-server"
    if key:
        pass
    elif key_file:
        with open(key_file, "r") as key_file:
            key = json.load(key_file)['API_Key']
    else:
        raise ValueError("You need to supply an API key to login, either directly or via a file.")
    
    __api = SemanthaAPI(RestClient(server_url, key), f"/api/{__PLATFORM_SERVER_API_VERSION}", "/api")

    # check whether API key is valid or not
    info = __api.info.get()
    logger = logging.getLogger()
    logger.info(f"Semantha API version: {info.version}")
    return __api
