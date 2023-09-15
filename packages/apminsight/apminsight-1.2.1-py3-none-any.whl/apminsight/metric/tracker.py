
from apminsight.constants import *
from apminsight.util import current_milli_time
from apminsight.metric.error import ErrorInfo
from apminsight.constants import max_exc_per_trace, CONTEXT, PARENT_CONTEXT
from apminsight.logger import agentlogger
from apminsight.util import is_ext_comp, remove_null_keys
from apminsight import constants
from apminsight import context
from apminsight.agentfactory import get_agent

class Tracker:

    def __init__(self, tracker_info={}):
        self._name = tracker_info.get('name', 'anonymous')
        self._actual_method = tracker_info.get('name', 'anonymous')
        self._component = tracker_info.get('component', '')
        self._start_time = current_milli_time()
        self._end_time = 0
        self._rt = 0
        self._child_overhead = 0
        self._info = {}
        self._child_trackers = []
        self._error = None
        self._is_error = False
        self._completed = False
        self._http_err = 0
        self._context = tracker_info.get(CONTEXT)
        self._parent_context = tracker_info.get(PARENT_CONTEXT, {})
        self._transaction = context.get_cur_txn()
        self._dt_trace = False

    def end_tracker(self, err=None):
        from apminsight.metric.dbtracker import DbTracker
        try:
            if err is not None:
                self.mark_error(err)
            self._end_time = current_milli_time()
            total_time = self._end_time - self._start_time
            self._rt =  total_time - self._child_overhead
            if isinstance(self, DbTracker) and not self.is_error() and self._rt>= self._transaction.get_sql_stacktrace_threshold():
                self._info[constants.STACKTRACE] = self.get_current_stacktrace()
            parent = self.get_parent()
            if parent is not None:
                parent.update_child_overhead(total_time)
                parent.add_child_tracker(self)
            if self.is_distributed_trace():
                context.get_cur_txn().increment_dt_count()

            self._completed = True
        except:
            agentlogger.exception('while ending the tracker, ', self._name)
        
    def get_current_stacktrace(self):
        stacktrace = []
        import traceback
        tracelist = traceback.extract_stack()
        for trace in tracelist:
            if not 'apminsight' in trace.filename:
                stacktrace.append(['', trace.filename, trace.name, trace.lineno])
        return stacktrace
    
    def get_parent(self):
        return self._transaction.get_tracker(self.get_parent_span_id())
    
    def get_parent_context(self):
        return self._parent_context
    
    def set_parent_context(self, context):
        self._parent_context = context
        
    def get_actual_method(self):
        return self._actual_method
        
    def set_tracker_name(self, name):
        if isinstance(name, str):
            self._name = name
        
    def get_end_time(self):
        return self._end_time
    
    def set_end_time(self, end_time):
        if isinstance(end_time, int):
            self._end_time = end_time
        
    def mark_error(self, err):
        if err is not None:
            self._is_error = True
            self._name+=' : '+ str(type(err).__name__ if hasattr(type(err), '__name__') else 'Error')
            if isinstance(err, Exception) and not hasattr(err, 'apminsight'):
                self._error = ErrorInfo(err)
                err.apminsight = True

    def get_child_overhead(self):
        return self._child_overhead
    
    def update_child_overhead(self, total_time):
        self._child_overhead += total_time

    def get_child_trackers(self):
        return self._child_trackers
    
    def add_child_tracker(self, child_trakcer):
        self._child_trackers.append(child_trakcer)

    def get_tracker_name(self):
        if OPERATION not in self._info:
            return self._name

        query_info = self._info[OPERATION]
        if constants.host_str in self._info and constants.port_str in self._info:
            query_info += ' - ' + self._info[constants.host_str] +':' + str(self._info[constants.port_str])

        return self._name + ' : ' + query_info

    def get_rt(self):
        return self._rt

    def set_rt(self, rt):
        if isinstance(rt, int):
            self._rt = rt
        
    def complete(self):
        self._completed = True
        
    def is_completed(self):
        return self._completed is True

    def get_component(self):
        return self._component

    def set_component(self, component):
        if isinstance(component, str):
            self._component = component
        
    def get_info(self, key=None):
        if key is None:
            return self._info
        if key and isinstance(key, str):
            return self._info.get(key)

    def set_info(self, info):
        self._info.update(info)
        
    def is_error(self):
        if self._is_error:
            return True
        
        return False

    def set_as_http_err(self):
        self._http_err = 1
        
    def is_http_err(self):
        return self._http_err

    def get_error_name(self):
        if self._error is not None:
            try:
                return self._error.get_type()
            except:
                agentlogger.exception("While extracting error information")

        return ''

    def get_exc_info(self):
        return self._error
    
    def get_span_id(self):
        return self._context.get(SPAN_ID_STR)
    
    def get_parent_span_id(self):
        return self._parent_context.get(SPAN_ID_STR)
    
    def get_context(self):
        return self._context

    def set_context(self, context):
        self._context = context
        
    def get_trace_id(self):
        return self._context.get(TRACE_ID_STR)

    def get_transaction(self):
        return self._transaction
    
    def set_transaction(self, txn):
        self._transaction = txn
    def is_distributed_trace(self):
        return self._dt_trace

    def set_dt_trace(self):
        self._dt_trace = True
        
    def check_and_add_loginfo(self, trace_info={}):
        if LOGINFO not in trace_info:
            trace_info[LOGINFO] = []

        if self.is_error() and len(trace_info[LOGINFO])<=max_exc_per_trace:
            log_info = {}
            excinfo = self.get_exc_info()
            log_info[TIME] = excinfo.get_time()
            log_info[constants.level_str] = excinfo.get_level()
            log_info[SH_STRING] = excinfo.get_message()
            log_info[SH_ERR_CLS] = excinfo.get_type()
            log_info[SH_STACK_TRACE] = excinfo.get_error_stack_frames()
            trace_info[LOGINFO].append(log_info)


    def get_tracker_info(self, trace_info={}):
        self.check_and_add_loginfo(trace_info)
        tracker_info = []
        tracker_info.append(self._start_time)
        tracker_info.append(self.get_tracker_name())
        tracker_info.append(self._component)
        tracker_info.append(self._rt + self._child_overhead) # total
        tracker_info.append(self._rt) # exclusive
        tracker_info.append(self.get_additional_info())
        tracker_info.append([])
        return tracker_info


    def get_additional_info(self):
        info = {}
        if self.is_error():
            info['exception_st'] = self._error.get_error_stack_frames()
        if self.is_distributed_trace():
            info['dtdata'] = self.get_info().get('dtdata')
        return info

    def get_tracker_data_for_trace(self, trace_info):
        cur_tracker_info = self.get_tracker_info(trace_info)

        for eachchild in self._child_trackers:
            child_tracker_data = eachchild.get_tracker_data_for_trace(trace_info)
            cur_tracker_info[6].append(child_tracker_data)
            
        return cur_tracker_info

    def add_tracker_data(self):
        method_data = {}
        method_data[SH_EXT_COMP] = int(is_ext_comp(self.get_component()))
        method_data[SH_IS_FAULT] = 0
        method_data[SH_IS_ERROR] = 1 if self.is_error() or self.is_http_err() else 0
        if self.get_component()==constants.http_comp:
            method_data[SH_HOST_NAME] = (self._info.get('url', ''))
        elif self._info.get(constants.host_str):
            method_data[SH_HOST_NAME] = self._info.get(constants.host_str, '')
        if self._info.get(constants.port_str):
            method_data[SH_PORT_NUMBER] = self._info.get(constants.port_str)
        method_data[SH_START_TIME] = self._start_time
        method_data[SH_END_TIME] = self._end_time
        method_data[SH_FUN_NAME] = self.get_tracker_name()
        method_data[SH_COMP_NAME] = self.get_component() or constants.python_str
        method_data[SH_SPAN_ID] = self.get_span_id()
        method_data[SH_PAR_SPAN_ID] = self.get_parent_span_id()
        method_data[SH_DIST_TRACE] = self.get_info().get('dtdata', {})
        if self._info.get(constants.query_str, ''):
            method_data[SH_QUERY_STR] = self._info.get(constants.query_str)
        if self._error:
            excinfo = self.get_exc_info()
            error_details = {}
            error_details[TIME] = excinfo.get_time()
            error_details[constants.level_str] = excinfo.get_level()
            error_details[SH_ERR_MSG] = excinfo.get_message()
            error_details[SH_ERR_CLS] = excinfo.get_type()
            method_data[SH_ERR_INFO] = [error_details]
            method_data[SH_ERR_STACK_TRACE] = self.get_exc_info().get_error_stack_frames()
        else:
            method_data['mst'] = self._info.get(STACKTRACE)
        remove_null_keys(method_data)
        return method_data
    