
agent_instance = None

def get_agent(config={}, external=None):
    global agent_instance
    if external:
        return agent_instance
    if agent_instance is None:
        try:
            from apminsight.agent import initalize
            agent_instance = initalize(options=config)
            print('APM INISGHT Agent initialized sucessfully')
        except Exception as e:
            print("[ERROR] APM INISHGT PYTHON Initilizaiton failed %s" %str(e))
    
    return agent_instance

def initialize_agent(config={}):
    from .logger import create_agentlogger
    create_agentlogger(config)
    from .instrumentation import init_instrumentation
    init_instrumentation()
    get_agent(config)
