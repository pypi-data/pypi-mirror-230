# -*- coding: utf-8 -*-

#  Developed by CQ Inversiones SAS. Copyright ©. 2019 - 2023. All rights reserved.
#  Desarrollado por CQ Inversiones SAS. Copyright ©. 2019 - 2023. Todos los derechos reservado

# ****************************************************************
# IDE:          PyCharm
# Developed by: macercha
# Date:         28/01/23 15:37
# Project:      Zibanu Django Project
# Module Name:  site
# Description:
# ****************************************************************
def site(request):
    """
    Context preprocessor to get absolute uri of site for use in django templates.

    Parameters
    ----------
    request : Request object from HTTP

    Returns
    -------
    site_uri: Dictionary with site key/value.
    """
    return {
        "site": request.build_absolute_uri("/")
    }
