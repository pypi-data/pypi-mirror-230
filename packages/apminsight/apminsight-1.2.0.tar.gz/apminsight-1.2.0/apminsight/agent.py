
import copy
import random
import string
import json
from apminsight.collector.connhandler import init_connection
from apminsight.metric.txn import Transaction
from apminsight.metric.tracker import Tracker
from apminsight.metric.dbtracker import DbTracker
from apminsight.metric.metricstore import Metricstore
from apminsight.config.configuration import Configuration
from apminsight.collector.ins_info import Instanceinfo
from apminsight.config.threshold import Threshold
from apminsight import context
from apminsight import constants
from apminsight.logger import agentlogger
from apminsight.util import check_and_create_base_dir
from apminsight import agentfactory
from apminsight.context import get_cur_txn
from apminsight.collector.metric_dispatcher import MetricDispatcher
from apminsight.collector.rescodes import res_codes_info


def initalize(options={}):
    options['agentbasedir'] = check_and_create_base_dir()
    agentfactory.agent_instance = Agent(options)
    agent_instance = agentfactory.agent_instance
    if not agent_instance.get_config().is_using_exporter():
        if not agent_instance.get_config().is_configured_properly():
            raise RuntimeError('Configure license key properly')
        init_connection()
    return agent_instance

class Agent:
    def __init__(self, info):
        self.config = Configuration(info)
        self.ins_info = Instanceinfo(info)
        self.threshold = Threshold()
        self.metricstore = Metricstore() if not self.config.is_using_exporter() else None
        self.metric_queue = [] if not self.config.is_using_exporter() else None
        self.metric_dispatcher = MetricDispatcher(self.config) if self.config.is_using_exporter() else None
        self.txn_dict = {} if self.config.is_using_exporter() else None
        self.__instance_info = None
        
    def update_app_port(self, app_port):
        self.config.set_app_port(app_port)
        
    def get_txn(self, trace_id):
        return self.txn_dict.get(trace_id)
    
    def push_to_txn_dict(self, txn):
        self.txn_dict[txn.get_trace_id()] = txn
    
    def push_to_queue(self, txn):
        self.metric_queue.append(txn)

    def get_metric_queue_for_processing(self):
        txn_list = copy.copy(self.metric_queue)
        self.metric_queue = []
        return txn_list

    def is_data_collection_allowed(self, txn_config):
        if txn_config is None:
            return False
        cur_status = txn_config.get("instance.status")
        if cur_status in [constants.manage_agent, constants.agent_config_updated]:
            return True
        else:
            agentlogger.info('data collection stopped due to response code %s %s', str(self.get_ins_info().get_status()), res_codes_info.get(self.get_ins_info().get_status()).get('name'))

        return False

    def update_threshold_config(self, wsgi_environ=None):
        response = {}
        try:
            payload_to_exporter = self.config.get_conn_payload(wsgi_environ)
            response = self.metric_dispatcher.send_connect_data(payload_to_exporter)
            if response:
                response = json.loads(response.decode("utf-8"))
                instance_info = {key:val for key, val in response.items() if not 'transaction' in key}
                if instance_info != self.__instance_info:
                    self.get_ins_info().set_status(response.get("instance.status"))
                    self.get_ins_info().set_instanceid(response.get("instance.id"))
                    self.get_config().set_license_key(response.get('license.key', ''))    
                    self.get_ins_info().write_conf_info(self.get_info_for_conf_file(instance_info))
                    self.__instance_info = instance_info
                agentlogger.info("Recieved the instance and threshold info from S247DataExporter successfully")
            else:
                agentlogger.info("No response from S247DataExporter")
        except:
            agentlogger.exception("while getting instance and threshold info from S247DataExporter")
        return response
    
    def get_info_for_conf_file(self, response):
        if response:
            response.pop('license.key')
            info_for_conf_file = {
                constants.SETUP_CONFIG: self.get_config().get_user_setup_config(),
                constants.THRESHOLD_CONFIG : response
            }
            return info_for_conf_file
        return response
    
    def check_and_create_txn(self, wsgi_environ, root_tracker_info):
        try:
            txn_config=None
            if not self.get_config().app_port_set():
                if not wsgi_environ.get(constants.server_port_str).isnumeric():
                    agentlogger.info('Auto detection of port failed due to absense of SERVER PORT details in environ')
                    return
                self.update_app_port(wsgi_environ[constants.server_port_str])
                    
            if self.get_config().is_using_exporter():
                txn_config = self.update_threshold_config(wsgi_environ)
                if not txn_config:
                    return
                if not self.metric_dispatcher.started():
                    self.metric_dispatcher.start_dispatching()

            if not self.is_data_collection_allowed(txn_config):
                return

            if type(wsgi_environ) is not dict:
                return

            if type(root_tracker_info) is not dict:
                return

            context.clear_cur_context()
            root_tracker_info[constants.CONTEXT][constants.TRACE_ID_STR] = ''.join(random.choices(string.ascii_letters+string.digits, k=32))
            txn = Transaction(wsgi_environ, root_tracker_info, txn_config)
            txn.get_root_tracker().set_transaction(txn)
            context.set_cur_context(txn.get_trace_id(), txn.get_root_tracker().get_span_id())
            self.txn_dict[txn.get_trace_id()] = txn
            # handle cross app response
            return txn
        except Exception:
            agentlogger.exception("while creating txn obj")

    def check_and_create_tracker(self, tracker_info):
        track = None
        cur_txn = get_cur_txn()
        try:
            if type(tracker_info) is not dict:
                return None

            if context.is_txn_active() is not True:
                return None

            if constants.PARENT_TRACKER not in tracker_info:
                tracker_info[constants.PARENT_TRACKER] = context.get_cur_tracker()

            if constants.is_db_tracker_str in tracker_info:
                track = DbTracker(tracker_info)
            else:
                track = Tracker(tracker_info)
            cur_txn.add_tracker(track)
            cur_txn.increment_method_count(1)

            context.set_cur_tracker(track)
        except:
            agentlogger.exception("While creating Tracker")
        
        return track

    
    def end_txn(self, txn, res=None, err=None):
        try:
            if txn is None:
                return

            if isinstance(txn, Transaction):
                txn.end_txn(res, err)
        except Exception:
            agentlogger.exception("tracking end txn")


    def end_tracker(self, tracker, err=None):
        if isinstance(tracker, Tracker) is not True:
            return

        txn=context.get_cur_txn()
        if isinstance(txn, Transaction):
            tracker.end_tracker(err)
            cur_txn = context.get_cur_txn()
            cur_txn.handle_end_tracker(tracker)


    def get_config(self):
        return self.config

    def get_threshold(self):
        return self.threshold

    def get_ins_info(self):
        return self.ins_info

    def get_metric_store(self):
        for txn in self.get_metric_queue_for_processing():
            self.metricstore.add_web_txn(txn)
        return self.metricstore
    
    def get_metric_dispatcher(self, external=None):
        if external:
            self.metric_dispatcher.start_dispatching()
        return self.metric_dispatcher