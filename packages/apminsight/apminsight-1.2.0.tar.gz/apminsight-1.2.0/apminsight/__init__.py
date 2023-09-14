
import os
from .agentfactory import initialize_agent, get_agent

name = "apminsight"

version = "1.2.0"

installed_path = os.path.dirname(__file__)

__all__ =[
    'name',
    'version',
    'installed_path',
    'get_agent',
    'initialize_agent',
]
