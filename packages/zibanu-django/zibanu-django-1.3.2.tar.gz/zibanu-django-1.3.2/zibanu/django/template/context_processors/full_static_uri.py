# -*- coding: utf-8 -*-

#  Developed by CQ Inversiones SAS. Copyright ©. 2019 - 2023. All rights reserved.
#  Desarrollado por CQ Inversiones SAS. Copyright ©. 2019 - 2023. Todos los derechos reservado

# ****************************************************************
# IDE:          PyCharm
# Developed by: macercha
# Date:         28/01/23 15:36
# Project:      Zibanu Django Project
# Module Name:  full_static_uri
# Description:
# ****************************************************************
from django.conf import settings


def full_static_uri(request):
    """
    Context preprocessor to get "full_static_uri", including hostname and static uri for template usage.

    Parameters
    ----------
    request : Request object from HTTP

    Returns
    -------
    full_uri: Dictionary with "full_static_uri" key/value.
    """

    if hasattr(settings, "STATIC_URL"):
        uri = request.build_absolute_uri(settings.STATIC_URL)
    else:
        uri = request.build_absolute_uri("/")
    return {
        "full_static_uri": uri
    }

