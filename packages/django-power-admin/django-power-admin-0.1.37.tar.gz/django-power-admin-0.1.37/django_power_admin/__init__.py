#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, generators, nested_scopes, print_function, unicode_literals, with_statement

default_app_config = "django_power_admin.apps.DjangoPowerAdminConfig"

app_requires = [
    "mptt",
    "django_static_fontawesome",
    "django_static_jquery_ui",
    "django_middleware_global_request",
    "django_simple_tags",
]

app_middleware_requires = [
    "django_middleware_global_request.middleware.GlobalRequestMiddleware",
]
