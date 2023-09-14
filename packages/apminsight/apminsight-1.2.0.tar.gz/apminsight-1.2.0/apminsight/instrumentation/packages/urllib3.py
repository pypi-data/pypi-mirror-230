
from apminsight import constants
from apminsight.logger import agentlogger

def get_request_url(conn,args, kwargs):
    from urllib3.connectionpool import HTTPSConnection
    if isinstance(conn, HTTPSConnection):
        return 'https://' + conn.host + kwargs.get(constants.URL)
    else:
        return 'http://' + conn.host + kwargs.get(constants.URL)


def get_conn_object(args):
    if len(args) :
        return args[0]
    return None

def get_conn_host_port( conn):
    if conn:
        return conn.host, conn.port
    return None, None
    
def extract_urllib3_request(tracker, args=(), kwargs={}, return_value=None, error=None):
    try:
        conn = get_conn_object(args)
        host, port = get_conn_host_port(conn) 
        method = ""
        url = ""
        
        if conn and len(args)==1:
            method = 'REQUESTS' + ' - ' + kwargs.get('method')
            url  = get_request_url(conn, args, kwargs)   
        elif len(args)==3:
            method = args[1]
            url = kwargs.get(constants.REQUEST_URL)

        if conn:
            status = str(return_value.status) if return_value is not None else None
            if status:
                tracker.set_tracker_name( tracker.get_tracker_name() + " : " + method + ' - ' + status + ' - ' + url)
                tracker.set_as_http_err() if int(status) >= 400 else 0
            else:
                tracker.set_tracker_name( tracker.get_tracker_name() + " : " + method + ' - ' + url)
            tracker.set_info({constants.HTTP_METHOD: method, constants.HOST: host, constants.PORT: port, constants.URL: url, constants.STATUS: status})

    except:
        agentlogger.exception("while extracting URLLIB3 request")

module_info = {

    'urllib3.connectionpool' : [
        {   constants.class_str : 'HTTPConnectionPool',
            constants.method_str : 'urlopen',
            constants.component_str : constants.http_comp,
            constants.extract_info_str : extract_urllib3_request
        }
    ],
}
