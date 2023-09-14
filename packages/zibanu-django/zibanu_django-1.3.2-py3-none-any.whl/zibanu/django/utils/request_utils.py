# -*- coding: utf-8 -*-

# ****************************************************************
# IDE:          PyCharm
# Developed by: macercha
# Date:         16/03/23 10:42
# Project:      Zibanu Django Project
# Module Name:  request_utils
# Description:
# ****************************************************************
import hashlib
from typing import Any
def get_ip_address(request:Any) -> str:
    """
    Get ip Address from request
    """
    ip_address = None
    if request is not None:
        ip_address = request.META.get("REMOTE_ADDR", None)
    return ip_address

def get_http_origin(request: Any, md5: bool = False) -> str:
    http_origin = None
    if request is not None:
        http_origin = request.META.get("HTTP_ORIGIN", "undefined")
        if md5:
            http_origin = hashlib.md5(http_origin.encode("utf-8")).hexdigest()
    return http_origin