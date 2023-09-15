
from apminsight import constants
from apminsight.instrumentation.wrapper import default_wrapper
from apminsight.util import is_non_empty_string
from apminsight.agentfactory import get_agent
from apminsight.logger import agentlogger
from apminsight.instrumentation.proxy import WrapperObject
from apminsight.constants import db_opn_regex
import re


def track_dbapi_query_opn(tracker, args =(), kwargs ={}):
    if is_non_empty_string(args[0]):
        query = args[0]
    elif isinstance(args[0], (bytes, bytearray)):
        query = args[0].decode("utf-8")
    if query:
        tracker.set_info({ constants.query_str : query})  
        opn_name = query.split(' ')[0]
        if opn_name.lower() in db_opn_regex:
            regex = db_opn_regex[opn_name.lower()]
            matchobj = re.match(regex, query, re.IGNORECASE)
            if matchobj is not None:
                tracker.set_info({ 'opn' : matchobj.group(1).lower(), 'obj' : matchobj.group(2)})

class CursorProxy(WrapperObject):

    def __init__(self, cursor, conn):
        super(CursorProxy, self).__init__(cursor)
        self._apm_wrap_conn = conn

    def execute(self, *args, **kwargs):
        if hasattr(self.__original__, 'execute'):
            wrapper = None
            try:
                actual = self.__original__.execute
                method_info = {
                    constants.method_str : 'execute',
                    constants.component_str : self._apm_wrap_conn._apm_comp_name,
                    constants.extract_info_str : self._apm_extract_query,
                    constants.is_db_tracker_str : True
                }
                wrapper = default_wrapper(actual, self.get_complete_class_name(), method_info)
            except:
                agentlogger.exception('while instrumenting execute function')
            if wrapper is not None:
                try:
                    return wrapper(*args, **kwargs)
                except Exception as exc:
                    raise exc
        return self.__original__.execute(*args, **kwargs)

    def executemany(self, *args, **kwargs):
        
        if hasattr(self.__original__, 'executemany'):
            wrapper = None
            try:
                actual = self.__original__.executemany
                method_info = {
                    constants.method_str : 'executemany',
                    constants.component_str : self._apm_wrap_conn._apm_comp_name,
                    constants.extract_info_str : self._apm_extract_query,
                    constants.is_db_tracker_str : True
                }
                wrapper = default_wrapper(actual, self.get_complete_class_name(), method_info)
            except:
                agentlogger.exception('while instrumenting executemany function')
            if wrapper is not None: 
                try:
                    return wrapper(*args, **kwargs)
                except Exception as exc:
                    raise exc
        return self.__original__.executemany(*args, **kwargs)

    def _apm_extract_query(self, tracker, args=(), kwargs={}, return_value=None, error=None):
        try:
            tracker.set_info(self._apm_wrap_conn._apm_host_info)
            if isinstance(args, (list, tuple)) and len(args)>0:
                track_dbapi_query_opn(tracker, args, kwargs)
        except:
            agentlogger.exception('while extracting query')


    def get_complete_class_name(self):
        class_name = str()
        try:
            class_name = self.__original__.__class__.__module__+'.'+ self.__original__.__class__.__name__
            return class_name
        except:
            agentlogger.exception('while extracting class name for cursor')
            
        return 'Cursor'

class ConnectionProxy(WrapperObject):

    def __init__(self, conn, comp, host_info):
        super(ConnectionProxy, self).__init__(conn)
        self._apm_comp_name = comp
        self._apm_host_info = host_info
        

    def cursor(self, *args, **kwargs):
        real_cursor = self.__original__.cursor(*args, **kwargs)
        try:
            cur = CursorProxy(real_cursor, self)
            return cur
        except:
            agentlogger.exception("While creating CursorProxy object")
            return real_cursor
    
    @staticmethod
    def get_host_info(method_info, conn_kwargs):
        host_info = {}
        try:
            if constants.host_str in conn_kwargs:
                host_info[constants.host_str] = conn_kwargs[constants.host_str]
            elif constants.default_host_str in method_info:
                host_info[constants.host_str] = method_info[constants.default_host_str]

            if constants.port_str in conn_kwargs:
                host_info[constants.port_str] = int(conn_kwargs[constants.port_str])
            elif constants.default_port_str in method_info:
                host_info[constants.port_str] = method_info[constants.default_port_str]
        except:
            agentlogger.exception("While extracting host_info")
        return host_info

    @staticmethod
    def instrument_conn(original, module, method_info):
        def conn_wrapper(*args, **kwargs):
            try:
                conn = original(*args, **kwargs)
            except Exception as exc:
                raise exc
            if conn is not None:
                try:
                    comp = method_info.get(constants.component_str, '')
                    proxy_class = method_info.get(constants.proxy_class_str, ConnectionProxy)
                    host_info = proxy_class.get_host_info(method_info, kwargs)
                    new_conn = proxy_class(conn, comp, host_info)
                    return new_conn
                except:
                    agentlogger.exception('while creating Proxy object')

            return conn

        return conn_wrapper

class ConnectionProxySqlite(ConnectionProxy):

    def __init__(self, conn, comp, host_info):
        super(ConnectionProxySqlite, self).__init__(conn, comp, host_info)

    def execute(self, *args, **kwargs):
        
        if hasattr(self.__original__ , 'execute'):
            wrapper = None
            try:
                actual = getattr(self.__original__, 'execute')
                method_info = {
                    constants.method_str : 'execute',
                    constants.component_str : self._apm_comp_name,
                    constants.extract_info_str : self._apm_extract_query,
                    constants.is_db_tracker_str : True
                }
                wrapper = default_wrapper(actual, self.get_complete_class_name(), method_info)
            except:
                agentlogger.exception('while instrumenting execute function')
            if wrapper is not None:
                try:
                    return wrapper(*args, **kwargs)
                except Exception as exc:
                    raise exc
        return self.__original__.execute(*args, **kwargs)

    def executemany(self, *args, **kwargs):
        
        if hasattr(self.__original__, 'executemany'):
            wrapper = None
            try:
                actual = getattr(self.__original__, 'executemany')
                method_info = {
                    constants.method_str : 'executemany',
                    constants.component_str : self._apm_comp_name,
                    constants.extract_info_str : self._apm_extract_query,
                    constants.is_db_tracker_str : True
                }
                wrapper = default_wrapper(actual, self.get_complete_class_name(), method_info)
            except:
                agentlogger.exception('while instrumenting executemany function')
            if wrapper is not None:
                try:
                    return wrapper(*args, **kwargs)
                except Exception as exc:
                    raise exc
        return self.__original__.executemany(*args, **kwargs)

    def _apm_extract_query(self, tracker, args=(), kwargs={}, return_value=None, error=None):
        try:
            tracker.set_info(self._apm_host_info)
            if isinstance(args, (list, tuple)) and len(args)>0:
                track_dbapi_query_opn(tracker, args, kwargs)

        except:
            agentlogger.exception('while extracting query')
    
    def get_complete_class_name(self):
        class_name = str()
        try:
            class_name = self.__original__.__class__.__module__+'.'+self.__original__.__class__.__name__
            return class_name
        except:
            agentlogger.exception('while extracting class name for cursor')
            
        return 'sqlite3.Connection'