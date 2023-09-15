from uuid import uuid4
from . import FormatterRule
from flask import request, Request
from flask.ctx import has_request_context

TRACE_LOAD_HEADER_KEY = None
TRACE_LOAD_CALLBACK = None


def set_trace_id_from_header(key):
    global TRACE_LOAD_HEADER_KEY
    TRACE_LOAD_HEADER_KEY = key


def set_load_trace_id_callback(func):
    if callable(func):
        global TRACE_LOAD_CALLBACK
        TRACE_LOAD_CALLBACK = func
        return True
    else:
        return False


def request_field_extend(self):
    request_id = getattr(self, "__trace_id__", None)
    if not request_id:
        val = None
        if TRACE_LOAD_HEADER_KEY:
            val = request.headers.get(TRACE_LOAD_HEADER_KEY)
        else:
            if callable(TRACE_LOAD_CALLBACK):
                val = TRACE_LOAD_CALLBACK()

        request_id = val or uuid4().hex
        setattr(self, "__trace_id__", request_id)
    return request_id


Request.trace_id = property(request_field_extend)


def get_trace_id():
    if has_request_context():
        return request.trace_id
    else:
        return uuid4().hex


class TraceFormatterRule(FormatterRule):
    CB_TAG_MAP = {"trace_id": get_trace_id}
