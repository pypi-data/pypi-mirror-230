#!/usr/bin/env python
# -*- coding: utf8 -*-
from __future__ import absolute_import, division, generators, nested_scopes, print_function, unicode_literals, with_statement
from .middlewares import get_request_id

app_requires = [
    "django_middleware_global_request",
]

app_middleware_requires = [
    "django_middleware_global_request.middleware.GlobalRequestMiddleware",
    "django_middleware_request_id.middlewares.DjangoMiddlewareRequestId",
]

app_setting_callbacks = [
    "django_middleware_request_id.log_filters.add_request_id_log_filter",
]
