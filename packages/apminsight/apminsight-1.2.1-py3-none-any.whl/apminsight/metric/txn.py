
import os
from urllib import parse
from apminsight.util import current_milli_time,is_empty_string
import random
import string
import asyncio
from apminsight import constants
from apminsight.util import current_milli_time,is_empty_string, remove_null_keys
from apminsight.metric.tracker import Tracker
from apminsight.metric.dbtracker import DbTracker
from apminsight.agentfactory import get_agent
from apminsight.metric.component import Component
from apminsight.constants import webtxn_prefix
from apminsight import constants
from apminsight.agentfactory import get_agent

class Transaction:

    def __init__(self, wsgi_environ={}, root_tracker_info={}, txn_config = None):
        self._url = wsgi_environ.get(constants.path_info_str, str())
        self._query = wsgi_environ.get(constants.query_string_str, str())
        self._http_input_params = self.get_request_params()
        self._request_method = wsgi_environ.get(constants.request_method_str, str())
        self._root_trakcer = Tracker(root_tracker_info)
        self._start_time = current_milli_time()
        self._end_time = None
        self._rt = 0
        self._completed = False
        self._status_code = 200
        self._exceptions_info = {}
        self._exceptions_count = 0
        self._external_comps = {}
        self._internal_comps = {}
        self._extcall_count = 0
        self._db_calls = []
        self._method_count = 1
        self._trace_id = root_tracker_info.get(constants.CONTEXT).get(constants.TRACE_ID_STR)
        self._custom_params = None
        self._cpu_start_time = int(round(os.times()[0] * 1000))
        self._cpu_end_time = None
        self._trackers = {self._root_trakcer.get_span_id():self._root_trakcer}
        self._dt_response_headers = None
        self._dt_count = 0
        self._txn_config = TxnConfig(txn_config)

    def get_trackers(self):
        return self._trackers
    
    def get_tracker(self, span_id):
        return self._trackers.get(span_id)
    
    def add_tracker(self, tracker):
        self._trackers[tracker.get_span_id()] = tracker
        
    def end_txn(self, res=None, err=None):
        agent = get_agent()
        self._root_trakcer.end_tracker(err)
        self._end_time = current_milli_time()
        if res is not None and hasattr(res, constants.status_code_str):
            self._status_code = res.status_code
        if err is not None:
            self._status_code = 500 
        self._rt = self._end_time-self._start_time
        self._completed = True
        self._cpu_end_time = int(round(os.times()[0] * 1000))
        if agent.get_config().is_using_exporter():
            asyncio.run(agent.metric_dispatcher.construct_payload(self.create_txn_payload))
        else:
            agent.push_to_queue(self)

    def create_txn_payload(self):
        transaction_info = {}
        from apminsight import get_agent
        config = get_agent().get_config()
        transaction_info[constants.exporter_param_key_http_host] = config.get_host_name()
        transaction_info[constants.exporter_param_key_request_url] = self.get_url()
        transaction_info[constants.exporter_param_key_query_string] = self.get_query_string()	
        transaction_info[constants.exporter_param_key_http_input_params] = self.get_http_input_params()
        transaction_info[constants.exporter_param_key_transaction_duration] = self.get_rt()
        transaction_info[constants.exporter_param_key_request_method] = self.get_method()
        transaction_info[constants.exporter_param_key_bytes_in] = None
        transaction_info[constants.exporter_param_key_bytes_out] = None
        transaction_info[constants.exporter_param_key_transaction_type] = 1      #1 for WEB self/ 0 for BG self
        transaction_info[constants.exporter_param_key_distributed_count] = self.get_dt_count()
        transaction_info[constants.exporter_param_key_thread_id] = None
        transaction_info[constants.exporter_param_key_response_code] = self.get_status_code()
        transaction_info[constants.exporter_param_key_collection_time] = self.get_start_time()
        transaction_info[constants.exporter_param_key_collection_end_time] = self.get_end_time()
        transaction_info[constants.exporter_param_key_cpu_time] = self.get_cpu_time()
        transaction_info[constants.exporter_param_key_memory_usage] = None
        transaction_info[constants.exporter_param_key_trace_id] = ''.join(random.choices(string.ascii_letters, k=7)) #sending a random string for now
        transaction_info[constants.exporter_param_key_custom_params] = None
        transaction_info[constants.exporter_param_key_trace_id] = self.get_trace_id()
        remove_null_keys(transaction_info)
        method_info =  self.add_trackers()
        txn_payload = {
                            "apm" : {constants.data_str : True,
                                    "application_info": {	
                                                        constants.exporter_param_key_application_type : constants.python_comp,
                                                        constants.exporter_param_key_application_name : get_agent().get_config().get_app_name(),
                                                        constants.exporter_param_key_instance_id : get_agent().get_ins_info().get_instance_id(),
                                                        },
                                    constants.transaction_info_str : transaction_info,
                                    constants.method_info_str : {"span_info": method_info}
                                    }
                            }
        return txn_payload
    
    def handle_end_tracker(self, tracker):
        self.aggregate_component(tracker)
        self.check_and_add_db_call(tracker)
        self.check_and_add_error(tracker)


    def aggregate_component(self, tracker):
        if is_empty_string(tracker.get_component()):
            return

        component = Component(tracker)
        if component.is_ext():
            component.aggregate_to_global(self._external_comps)
            self._extcall_count += component.get_count() + component.get_error_count()
        else:
            component.aggregate_to_global(self._internal_comps)
         

    def check_and_add_db_call(self, db_tracker):
        if isinstance(db_tracker, DbTracker):
            self._db_calls.append(db_tracker)


    def check_and_add_error(self, tracker):
        if not tracker.is_error():
            return

        err_name = tracker.get_error_name()
        if is_empty_string(err_name):
            return

        err_count = self._exceptions_info.get(err_name, 0)
        self._exceptions_info[err_name] = err_count+1
        self._exceptions_count += 1 


    @staticmethod
    def comp_details_for_trace(allcompinfo):
        comp_details = {'success' : {}, 'fail' : {}}
        for eachcomp in allcompinfo.keys():
            compinfo = allcompinfo[eachcomp]
            if compinfo.get_name() in comp_details['success'].keys():
                comp_details['success'][compinfo.get_name()] += compinfo.get_count()
                comp_details['fail'][compinfo.get_name()] += compinfo.get_error_count()
            else:
                comp_details['success'][compinfo.get_name()] = compinfo.get_count()
                comp_details['fail'][compinfo.get_name()] = compinfo.get_error_count()


        return comp_details
        
    def add_trackers(self):
        method_info = []
        for tracker in self._trackers.values():
            method_info.append(tracker.add_tracker_data())
        return method_info

    def get_trace_info(self):
        trace_info = {}
        trace_info['t_name'] = webtxn_prefix + self.get_url()
        trace_info['http_method_name'] = self.get_method()
        trace_info['s_time'] = self.get_start_time()
        trace_info['r_time'] = self.get_rt()
        trace_info['http_query_str'] = self.get_query_string()
        trace_info['http_input_params'] = self.get_http_input_params()
        trace_info['trace_reason'] = 4
        trace_info['db_opn'] = []
        trace_info['loginfo'] = []
        trace_info['method_count'] = self.get_method_count()
        trace_info['dt_count'] = self._dt_count
        trace_info['ext_components'] = Transaction.comp_details_for_trace(self._external_comps)
        trace_info['int_components'] = Transaction.comp_details_for_trace(self._internal_comps)
        if self.get_status_code() is not None:
            trace_info['httpcode'] = self.get_status_code()

        return trace_info

    def get_trace_data(self):
        trace_info = self.get_trace_info()
        trace_data = self._root_trakcer.get_tracker_data_for_trace(trace_info)
        return [trace_info, trace_data]

    def get_status_code(self):
        return self._status_code

    def set_status_code(self, code):
        if isinstance(code, int):
            self._status_code = code
            
    def get_method_count(self):
        return self._method_count

    def increment_method_count(self, count):
        if isinstance(count, int):
            self._method_count+=count
            
    def get_root_tracker(self):
        return self._root_trakcer

    def get_url(self):
        return self._url

    def get_method(self):
        return self._request_method

    def get_rt(self):
        return self._rt
    
    def set_rt(self, rt):
        if isinstance(rt, int):
            self._rt = rt

    def get_start_time(self):
        return self._start_time

    def get_end_time(self):
        return self._end_time
    
    def get_query_string(self):
        return self._query

    def get_http_input_params(self):
        return self._http_input_params
    
    def get_exceptions_info(self):
        return self._exceptions_info

    def get_exceptions_count(self):
        return self._exceptions_count

    def set_exceptions_count(self, count):
        if isinstance(count, int):
            self._exceptions_count = count
            
    def get_status_code(self):
        return self._status_code

    def clear_db_calls(self):
        self._db_calls = []

    def get_db_calls(self):
        return self._db_calls
    
    def update_db_calls(self, db_calls):
        if isinstance(db_calls, list):
            self._db_calls+=db_calls

    def get_internal_comps(self):
        return self._internal_comps

    def get_external_comps(self):
        return self._external_comps

    def get_ext_call_count(self):
        return self._extcall_count

    def is_completed(self):
        return self._completed

    def get_trace_id(self):
        return self._trace_id
    
    def get_cpu_time(self):
        if self._cpu_end_time:
            return self._cpu_end_time - self._cpu_start_time
        else :
            return None
    
    def is_error_txn(self):
        if isinstance(self._status_code, int) and self._status_code >= 400:
            return True
        
        return self._root_trakcer.is_error()

    def set_custom_params(self, key, value):
        
        if self._custom_params is None:
            self._custom_params = {key:[value]}
        elif len(self._custom_params)>10:
            return
        elif self._custom_params.get(key):
            if len(self._custom_params[key])<10:
                self._custom_params[key].append(value)
        else:
            self._custom_params[key] = [value]
      
    def get_custom_params(self):
        return self._custom_params
    
    def get_dt_count(self):
        return self._dt_count
    
    def increment_dt_count(self):
        self._dt_count+=1
        
    def get_dt_response_headers(self):
        return self._dt_response_headers
    
    def set_dt_response_headers(self, resp_headers):
        self._dt_response_headers = resp_headers
        
    def get_txn_config(self):
        return self._txn_config
    
    def aggregate_trackers(self, tracker):
        for child_tracker in tracker.get_child_trackers():
            self.aggregate_trackers(child_tracker)
        self.handle_end_tracker(tracker)

    def get_request_params(self):
        params = {}
        if self._query:
            parsed = parse.parse_qs(parse.urlparse(self._query).query)
            params.update({key, value[0]} for key, value in parsed.items())
        return params
    
    def get_sql_stacktrace_threshold(self):
        return self._txn_config.sql_stacktrace_threshold
    
    def get_rum_appkey(self):
        return self._txn_config.rum_appkey

    def get_webtxn_naming_use_requesturl(self):
        return self._txn_config.txn_naming_use_requesturl

class TxnConfig:
    def __init__(self, txn_config):
        self.sql_stacktrace_threshold = txn_config.get(constants.sql_stacktrace, 3)
        self.rum_appkey = txn_config.get(constants.web_rum_appkey, '')
        self.txn_naming_use_requesturl = txn_config.get(constants.webtxn_naming_use_requesturl, '')