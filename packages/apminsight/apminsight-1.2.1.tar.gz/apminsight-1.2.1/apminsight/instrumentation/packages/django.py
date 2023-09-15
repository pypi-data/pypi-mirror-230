
from apminsight import constants
from apminsight.instrumentation.wrapper import wsgi_wrapper, handle_dt_headers
from apminsight.context import is_no_active_txn, get_cur_txn
from apminsight.agentfactory import get_agent
from apminsight.logger import agentlogger

def wrap_get_response(original, module, method_info):
    def wrapper(*args, **kwargs):
        if is_no_active_txn():
            return original(*args, **kwargs)
        try:
            response = original(*args, **kwargs)
        except Exception as exc:
            raise exc
        try:
            request = args[1]
            license_key_from_req = request.headers.get(constants.LICENSE_KEY_FOR_DT_REQUEST)
            dtdata = handle_dt_headers(license_key_from_req)
            if dtdata is not None:
                response.headers[constants.DTDATA] = dtdata
        except:
            agentlogger.exception('while processing distributed trace headers')
        return response

    # special handling for flask route decorator
    wrapper.__name__ = original.__name__
    return wrapper

def wrap_get_wsgi_application(original, module, method_info):
    def wrapper(*args, **kwargs):
        from apminsight.instrumentation import instrument_django_middlewares
        instrument_django_middlewares()
        return original(*args, **kwargs)
    return wrapper

module_info = {
    'django.core.handlers.wsgi' : [
        {
            constants.class_str : 'WSGIHandler',
            constants.method_str : '__call__',
            constants.wrapper_str : wsgi_wrapper,
            constants.component_str : constants.django_comp
        }
    ],
    'django.core.handlers.base' : [
        {
            constants.class_str : 'BaseHandler',
            constants.method_str : 'get_response',
            constants.wrapper_str : wrap_get_response,
            constants.component_str : constants.django_comp
        }
    ],
    'django.conf.urls' : [
        {
            constants.method_str : 'url',
            constants.wrap_args_str : 1,
            constants.component_str : constants.django_comp
        }
    ],
    'django.urls' : [
        {
            constants.method_str : 'path',
            constants.wrap_args_str : 1,
            constants.component_str : constants.django_comp
        }
    ],
    'django.template' : [
        {
            constants.class_str : 'Template',
            constants.method_str : 'render',
            constants.component_str : constants.template
        }
    ],
    'django.core.wsgi' : [
        {
            constants.method_str : 'get_wsgi_application',
            constants.wrapper_str : wrap_get_wsgi_application,
            constants.component_str : constants.django_comp
        }
    ],
}