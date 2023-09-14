
import time
import os
import json
import base64
import re
from apminsight import constants
from apminsight.logger import agentlogger

try:
    from collections.abc import Callable  # noqa
except ImportError:
    from collections import Callable  # noqa

def current_milli_time():
    return int(round(time.time() * 1000))

def is_non_empty_string(string):
    if not isinstance(string, str) or string == '':
        return False
    return True

def is_empty_string(string):
    if not isinstance(string, str) or string == '':
        return True

    return False

def is_digit(char):
    if char >= '0' and char <= '9':
        return True

    return False

def is_callable(fn):
    return isinstance(fn, Callable)

def is_ext_comp(component_name):
    return component_name in constants.ext_components

def check_and_create_base_dir():
    try:
        base_path = os.path.join(os.getcwd(), constants.base_dir)
        if not os.path.exists(base_path):
            os.makedirs(base_path)
        
    except Exception:
        print('Error while creating agent base dir in '+ os.getcwd())
    
    return base_path

def get_masked_query(sql):
    if is_empty_string(sql):
        return ''
    masked_string_arguments = re.sub(r'[\'"](.*?)[\'"]', '?', sql)
    final_masked_query = re.sub(r'\d+\.\d+|\d+', '?', masked_string_arguments)
    return final_masked_query

def convert_tobase64(string):
    try:
        base64_bytes = string.encode('ascii')
        base64_value = base64.b64encode(base64_bytes)
        return base64_value.decode('ascii')
    except:
        agentlogger.exception('while base64 encoding the data')
    return ''
    
def read_config_file():
    config = {}
    try:
        current_directory = os.getcwd()
        apminsight_info_file_path = os.path.join(current_directory, constants.AGENT_CONFIG_INFO_FILE_NAME)
        if os.path.exists(apminsight_info_file_path):
            with open(apminsight_info_file_path,'r') as fh:
                config=json.load(fh)
        config = {config_key.lower(): config_value for config_key,config_value in config.items()}
    except:
        agentlogger.exception('while reading config file')
    return config

def remove_null_keys(dict):
    keys = [key for key, value in dict.items() if value is None]
    for key in keys:
        del dict[key]
        
