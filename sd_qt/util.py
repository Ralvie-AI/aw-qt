import os
import json
import logging


import requests
from cachetools import LRUCache

from sd_core.cache import credentials
from sd_core.const import SETTINGS_CACHE_KEY, LOCAL_HOST, CERT
from sd_core.util import stop_process_by_exe, start_exe

os.environ.pop('HTTP_PROXY', None)
os.environ.pop('HTTPS_PROXY', None)


logger = logging.getLogger(__name__)

cache = LRUCache(maxsize=100)
events_cache = LRUCache(maxsize=2000)


# Functions to interact with settings

def add_settings(key, value):
    headers = {'Content-Type': 'application/json',
               'Accept': 'application/json'}
    data = json.dumps({"code": key, "value": value})
    settings = requests.post(LOCAL_HOST + "/0/settings", data=data, headers=headers,
                             verify=str(CERT),)
    sundail_token = ""
    creds = credentials()
    if creds:
        sundail_token = creds["token"] if creds['token'] else None

        sett = requests.get(LOCAL_HOST + "/0/getallsettings",
                                    headers={"Authorization": sundail_token},
                                    verify=str(CERT),)
        cache[SETTINGS_CACHE_KEY] = sett.json()

        # Clear the events cache to make effect on enabling or disabling on "Enable idle time detection" 
        events_cache.clear()
    else:
        cache[SETTINGS_CACHE_KEY] = settings.json()

def retrieve_settings():
    creds = credentials()
    sundail_token = ""
    cached_settings = cache.get(SETTINGS_CACHE_KEY)
    # import pdb; pdb.set_trace()
    if cached_settings:
        return cached_settings
    else:
        if creds:
            sundail_token = creds["token"] if creds['token'] else None
        try:
            sett = requests.get(LOCAL_HOST + "/0/getallsettings",
                                headers={"Authorization": sundail_token},
                                verify=str(CERT),)
            settings = sett.json()
            cache[SETTINGS_CACHE_KEY] = settings

            # Clear the events cache to make effect on enabling or disabling on "Enable idle time detection" 
            events_cache.clear()
        except:
            settings = {}
        return settings
    
def check_server_status():
    try:
        response = requests.get(
            LOCAL_HOST + "/0/server_status",
            verify=str(CERT),
            timeout=5,
        )

        logger.debug("Server returned HTTP %s", response.status_code)

        return response.status_code == 200

    except requests.exceptions.SSLError as e:
        logger.exception("TLS/SSL verification failed: %s", e)
        stop_process_by_exe("sd-server.exe")
        start_exe("sd-server.exe")
        
        return False

    except requests.exceptions.ConnectionError as e:
        logger.exception("Unable to connect to server: %s", e)
        return False

    except requests.exceptions.Timeout as e:
        logger.exception("Connection timed out: %s", e)
        return False

    except requests.RequestException as e:
        logger.exception("Request failed: %s", e)
        return False

def clear_cache():
    """
    Clears both the general cache and the events cache.
    """
    try:
        cache.clear()
        events_cache.clear()
    except Exception as e:
        logger.exception(f"An error occurred while clearing the cache: {e}")
