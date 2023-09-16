#!/usr/bin/env python
# -*- coding: utf8 -*-
from __future__ import absolute_import, division, generators, nested_scopes, print_function, unicode_literals, with_statement

import logging
from django.conf import settings
from .middlewares import get_request_id

DJANGO_REQUEST_ID_LOG_ID = getattr(settings, "DJANGO_REQUEST_ID_LOG_ID", "request_id")

class RequestIdLogFilter(logging.Filterer):
    def filter(self, record):
        setattr(record, DJANGO_REQUEST_ID_LOG_ID, get_request_id())
        return True

def add_request_id_log_filter(globals):
    """Fix LOGGING in pro/settings.py.
    """
    LOGGING = globals.get("LOGGING", {})
    if LOGGING:
        filters = LOGGING.get("filters", None)
        if filters is None:
            LOGGING["filters"] = {}
            filters = LOGGING["filters"]
        if not DJANGO_REQUEST_ID_LOG_ID in filters:
            filters[DJANGO_REQUEST_ID_LOG_ID] = {
                "()": "django_middleware_request_id.log_filters.RequestIdLogFilter",
            }
        handlers = LOGGING.get("handlers", None)
        if handlers is None:
            LOGGING["handlers"] = {}
            handlers = LOGGING["handlers"]
        for _, handler_config in handlers.items():
            if not "filters" in handler_config:
                handler_config["filters"] = []
            if not DJANGO_REQUEST_ID_LOG_ID in handler_config["filters"]:
                handler_config["filters"].append(DJANGO_REQUEST_ID_LOG_ID)
