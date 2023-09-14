
import os
import requests
import apminsight
import socket
import platform
import json
import re
import apminsight.constants as constants
from apminsight.logger import agentlogger
from apminsight.util import is_empty_string, is_non_empty_string

class Configuration:
    __license_key = None
    __app_name = None
    __app_port =  None
    __app_port_set = None
    __collector_host = None
    __collector_host = None
    __proxy_server_host = None
    __proxy_server_port = None
    __proxy_username = None
    __proxy_password = None
    __agent_version = None
    __installed_path = None
    __cloud_instance_id = None
    __is_cloud_instance = None
    __cloud_type = None
    __exporter = None
    __exporter_status_port = None
    __exporter_data_port = None
    __exporter_host = None
    __host_type = None
    __is_docker = None
    __host_name = None
    __fqdn = None
    __conn_payload=None

    def __init__(self, info):
        self.__license_key = None#get_license_key(info)   Not reading from user config
        self.__app_name = get_app_name(info)
        self.__app_port = None
        self.__app_port_set = False
        self.__collector_host = get_collector_host(self.__license_key, info)
        self.__collector_port = get_collector_port(info)
        self.__proxy_server_host = get_proxy_server_host(info)
        self.__proxy_server_port = get_proxy_server_port(info)
        self.__proxy_username = get_proxy_auth_username(info)
        self.__proxy_password = get_proxy_auth_password(info)
        self.__agent_version = apminsight.version
        payload_config = os.getenv(constants.apm_print_payload, '')
        self.print_payload = False if is_empty_string(payload_config) else True
        self.__installed_path = apminsight.installed_path
        self.__is_cloud_instance, self.__cloud_type, self.__cloud_instance_id = get_cloud_details() if not using_exporter(info) else (None, None, None)
        self.__exporter = using_exporter(info)
        self.__exporter_status_port = get_exporter_status_port(info)
        self.__exporter_data_port = get_exporter_data_port(info)
        self.__exporter_host = get_exporter_host(info)
        self.__is_docker, self.__host_type, self.__host_name = get_docker_env_details()
        self.__fqdn = get_fqdn()
        self.__conn_payload = self.create_connection_payload()
        
    def is_configured_properly(self):
        if is_empty_string(self.__license_key):
            return False
       
        return True

    def update_collector_info(self, collector_info):
        if collector_info is None:
            return

        try:
            self.__collector_host = collector_info.get(constants.host_str, self.__collector_host)
            self.__collector_port = collector_info.get(constants.port_str, self.__collector_port)
        except Exception:
            agentlogger.exception('while updating collector info')
            
    def get_license_key(self):
        return self.__license_key

    def get_app_name(self):
        return self.__app_name

    def set_app_name(self, appname):
        self.__app_name = appname
        
    def get_app_port(self, for_exporter=True):
        if self.__app_port is not None:
            if not for_exporter or not self.__exporter:
                return self.__app_port
            return int(self.__app_port)
        
    def set_app_port(self, app_port):
        self.__app_port = app_port
        self.__conn_payload['connect_info']['agent_info']['port'] = int(app_port)
        self.__app_port_set = True
        
    def app_port_set(self):
        return self.__app_port_set
    
    def get_collector_host(self):
        return self.__collector_host

    def get_collector_port(self):
        return self.__collector_port

    def get_agent_version(self):
        return self.__agent_version

    def get_installed_dir(self):
        return self.__installed_path

    def is_payload_print_enabled(self):
        return self.print_payload
    
    def get_is_cloud_instance(self):
        return self.__is_cloud_instance

    def get_cloud_instance_id(self):
        return self.__cloud_instance_id

    def get_cloud_type(self):
        return self.__cloud_type

    def get_fqdn(self):
        return self.__fqdn
        
    def get_host_name(self, for_exporter=True):
        if self.__is_docker:
            return self.__host_name
        if not for_exporter or not self.__exporter and self.__cloud_instance_id:
            return self.__cloud_instance_id
        return platform.node()
        
    def get_host_type(self, for_exporter=True):
        if self.__is_docker:
            return self.__host_type
        if not for_exporter or not self.__exporter and self.__cloud_type:
            return self.__cloud_type
        return platform.system()

    def get_proxy_details(self):
        if not self.__proxy_server_host or not self.__proxy_server_port:
            return False
        if self.__proxy_username and self.__proxy_password :
            proxy_details = { 'http': 'http://' + self.__proxy_username + ':' + self.__proxy_password + '@' + self.__proxy_server_host + ':' + self.__proxy_server_port,
                    'https': 'http://' + self.__proxy_username + ':' + self.__proxy_password + '@' + self.__proxy_server_host + ':' + self.__proxy_server_port
                    }
        else:
            proxy_details = { 'http': 'http://' + self.__proxy_server_host + ':' + self.__proxy_server_port,
                    'https': 'http://' + self.__proxy_server_host + ':' + self.__proxy_server_port
                    }
        return proxy_details

    def is_using_exporter(self):
        return self.__exporter

    def get_exporter_status_port(self):
        return self.__exporter_status_port 
        
    def get_exporter_data_port(self):
        return self.__exporter_data_port

    def get_exporter_host(self):
        return self.__exporter_host

    def set_license_key(self, license_str):
        if is_non_empty_string(license_str):
            self.__license_key = license_str
    
    def get_user_setup_config(self):
        return {
                        constants.APP_NAME : self.get_app_name(),
                        constants.HOST_NAME : self.get_host_name(),
                        constants.APP_PORT : self.get_app_port(),
                        constants.EXP_HOST : self.get_exporter_host(),
                        constants.EXP_STATUS_PORT : self.get_exporter_status_port(),
                        constants.EXP_DATA_PORT : self.get_exporter_data_port(),
                        constants.PROXY_DETAILS : self.get_proxy_details(),
                        constants.AGENT_VERSION : self.get_agent_version()
            },
        
    def get_license_key_for_dt(self):
        if self.is_configured_properly():
            license_key = self.__license_key
            license_key_for_dt = license_key[-12:]
            return license_key_for_dt
        return None
    def create_connection_payload(self):
        conn_payload = {
                "agent_info" : { 
                "application.type": constants.python_str, 
                "agent.version": self.get_agent_version(), 
                "application.name": self.get_app_name(), 
                "port": self.get_app_port(), 
                "host.type": self.get_host_type(),
                "hostname": self.get_host_name(),
                "fqdn" : self.get_fqdn()
            }, "environment" : { 
                #"UserName": process.env.USER, 
                "OSVersion": platform.release(), 
                "MachineName": platform.node(), 
                'AgentInstallPath': self.get_installed_dir(), 
                "Python version": platform.python_version(), 
                "OSArch": platform.machine(), 
                "OS": platform.system(),
                "Python implementation" : platform.python_implementation()
            }
        }
        if self.is_using_exporter():
            conn_payload = { 
            "connect_info" : conn_payload,
            "misc_info" : {}
        }
        
        return conn_payload

    def get_conn_payload(self, wsgi_environ=None):
        conn_payload = self.__conn_payload
        if wsgi_environ is not None:
            txn_name = wsgi_environ.get(constants.path_info_str, '')
            conn_payload["misc_info"]["txn.name"] = txn_name
        if self.is_using_exporter():
            conn_payload = json.dumps(conn_payload)
            conn_payload+="\n"
        return conn_payload
    
def get_collector_host(license_key, info):

    host = os.getenv(constants.apm_collector_host, '')
    if is_non_empty_string(host):
        return host

    if 'apm_collector_host' in info and is_non_empty_string(info['apm_collector_host']):
        return info['apm_collector_host']

    if is_non_empty_string(license_key):
        if license_key.startswith('eu_'):
            return constants.eu_collector_host

        if license_key.startswith('cn_'):
            return constants.cn_collector_host

        if license_key.startswith('in_'):
            return constants.ind_collector_host

        if license_key.startswith('au_'):
            return constants.aus_collector_host
        
        if license_key.startswith('jp_'):
            return constants.jp_collector_host

        return constants.us_collector_host

    return ''


def get_license_key(info):
    license_key = os.getenv(constants.license_key_env)
    if is_non_empty_string(license_key):
        return license_key
    if 'license_key' in info and is_non_empty_string(info['license_key']):
        return info['license_key']
    return ''

def get_app_name(info):

    app_name = os.getenv(constants.apm_app_name)
    if is_non_empty_string(app_name) and re.fullmatch('^[A-Za-z0-9]+[-:@_/()|\\ A-Za-z0-9]*',app_name):
        return app_name
    if 'appname' in info and is_non_empty_string(info['appname']) and re.fullmatch('^[A-Za-z0-9]+[-:@_/()|\\ A-Za-z0-9]*',info['appname']):
        return info['appname']

    return 'Python-Application'


def get_app_port(info):
    app_port = os.getenv(constants.apm_app_port)
    if is_non_empty_string(app_port) :
        return app_port
    if 'app_port' in info and is_non_empty_string(info['app_port']):
        return info['app_port']

    return '80'

def get_collector_port(info):
    collector_port = os.getenv(constants.apm_collector_port)
    if is_non_empty_string(collector_port):
        return collector_port
    if 'apm_collector_port' in info and is_non_empty_string(info['apm_collector_port']):
        return info['apm_collector_port']

    return constants.ssl_port

def get_proxy_server_host(info):
    proxy_server_host = os.getenv('PROXY_SERVER_HOST')
    if is_non_empty_string(proxy_server_host):
        return proxy_server_host
    if 'proxy_server_host' in info and is_non_empty_string(info['proxy_server_host']):
        return info['proxy_server_host']
    return None

def get_proxy_server_port(info):
    proxy_server_port = os.getenv('PROXY_SERVER_PORT')
    if is_non_empty_string(proxy_server_port):
        return proxy_server_port
    if 'proxy_server_port' in info and is_non_empty_string(info['proxy_server_port']):
        return info['proxy_server_port']
    return None

def get_proxy_auth_username(info):
    proxy_auth_username = os.getenv('PROXY_AUTH_USERNAME')
    if is_non_empty_string(proxy_auth_username):
        return proxy_auth_username
    if 'proxy_auth_username' in info and is_non_empty_string(info['proxy_auth_username']):
        return info['proxy_auth_username']
    return None

def get_proxy_auth_password(info):
    proxy_auth_password = os.getenv('PROXY_AUTH_PASSWORD')
    if is_non_empty_string(proxy_auth_password):
        return proxy_auth_password
    if 'proxy_auth_password' in info and is_non_empty_string(info['proxy_auth_password']):
        return info['proxy_auth_password']
    return None

def get_fqdn():
    try:
        return socket.getfqdn()
    except Exception:
        agentlogger.info("while fetching fqdn")
    return ''
        
def is_aws():
    try: 
        response = requests.get(constants.aws_url, timeout=0.005)
        if(response.status_code == 200 and  is_non_empty_string(response.text)):
            cloud_instance_id = response.text
            cloud_type = "AWS"
            return (True, cloud_type, cloud_instance_id)
    except Exception:
        agentlogger.info('AWS instance checking Failed')

    return False

def is_azure(): 
    try:
        headers = {'content-type': 'application/json'}
        response = requests.get(constants.azure_url, headers=headers, timeout=0.005)
        if(response.status_code == 200 and is_non_empty_string(response.json().get('ID'))):
            cloud_instance_id = response.json().get('ID')
            cloud_type = "AZURE"
            return (True, cloud_type, cloud_instance_id)
    except Exception:
        agentlogger.info('Azure instance checking Failed')

    return False

def get_docker_env_details():
    host_name = None
    host_type = None
    try:
        with open('/proc/self/cgroup','r') as cgroup:
            cgroup_info = cgroup.read()
            if(isinstance(cgroup_info,str) and is_non_empty_string(cgroup_info)):
                line_with_id = [ info for info in cgroup_info.split('\n') if "docker/" in info]
                if (line_with_id) :
                    id = line_with_id[0].split('docker/').pop()
                    host_name = id
                    host_type = 'DOCKER'
                    return (True, host_type, host_name) 
                else :
                    agentlogger.info("Not a docker environment.") 
            else:
                with open('/proc/self/cpuset','r') as cpuset:
                    cpuset_info = cpuset.read()
                    if(isinstance(cpuset_info,str) and is_non_empty_string(cpuset_info)):
                        id = cgroup_info.replace("/docker/","")
                        host_name = id
                        host_type = 'DOCKER'
                        return (True, host_type, host_name)
                    else :
                        agentlogger.info("Not a docker environment.") 
    except Exception:
        agentlogger.info('Exception checking docker environment')
    return (False, host_type, host_name)

def get_cloud_details():
    aws =  is_aws()
    azure = is_azure()
    if aws:
        return aws 
    elif azure:
        return azure
    return (False, None, None)

def using_exporter(info):
    using_exporter = info.get('exporter', True)
    if using_exporter:
        return True
    return False

def get_exporter_status_port(info):
    exporter_status_port = os.getenv(constants.APM_EXP_STATUS_PORT)
    if is_non_empty_string(exporter_status_port):
        return exporter_status_port
    if 'exporter_status_port' in info and is_non_empty_string(info['exporter_status_port']):
        return info['exporter_status_port']
    return '20021'

def get_exporter_data_port(info):
    exporter_data_port = os.getenv(constants.APM_EXP_DATA_PORT)
    if is_non_empty_string(exporter_data_port):
        return exporter_data_port
    if 'exporter_data_port' in info and is_non_empty_string(info['exporter_data_port']):
        return info['exporter_data_port']
    return '20022'
 
def get_exporter_host(info):
    exporter_host = os.getenv(constants.APM_EXP_HOST)
    if is_non_empty_string(exporter_host):
        return exporter_host
    if 'exporter_host' in info and is_non_empty_string(info['exporter_host']):
        return info['exporter_host']
    return constants.localhost_str