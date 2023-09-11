# -*- coding: utf-8 -*-
"""
jf-ext.RequestExt.py
~~~~~~~~~~~~~~~~~~~~

:copyright: (c) 2018-2022 by the Ji Fu, see AUTHORS for more details.
:license: MIT, see LICENSE for more details.
"""


def get_ip(request):
    """
    >>> 获取客户端IP地址

    @params {} request: flask request
    @returns {String}: request customer IP
    """
    headers_list = request.headers.getlist("X-Forwarded-For")
    ip = headers_list[0] if headers_list else request.remote_addr
    return ip


def get_request_data(request):
    """
    >>> 获取请求数据

    @params {} request: flask request
    @returns {json}: 请求数据
    """
    element = None
    if 'GET' == request.method:
        element = request.args
    if 'POST' == request.method:
        # 判断content_type
        content_type = request.headers.get('Content-Type', '')
        if "application/json" in content_type.lower():
            element = request.json
        else:
            element = request.form
    return element


def get_request_value(key):
    """
    >>> 获取请求参数

    @params {String} value:
    @return {String}:
    """
    none_strs = [
        'none',
        "undefined",
        'null',
    ]
    data = get_request_data()
    if isinstance(data, dict):
        value = data.get(key, None)
        if value and isinstance(value, str):
            if value.lower in none_strs:
                return None
        return value
    else:
        return None
