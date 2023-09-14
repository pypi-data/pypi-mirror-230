# -*- coding: utf-8 -*-

#  Developed by CQ Inversiones SAS. Copyright ©. 2019 - 2023. All rights reserved.
#  Desarrollado por CQ Inversiones SAS. Copyright ©. 2019 - 2023. Todos los derechos reservado

# ****************************************************************
# IDE:          PyCharm
# Developed by: macercha
# Date:         7/02/23 18:56
# Project:      Zibanu Django Project
# Module Name:  string_concat
# Description:
# ****************************************************************
from django import template

register = template.Library()


@register.simple_tag
def string_concat(first_string: str, *args):
    """
    Simple tag to concatenate one string with strings tuple.

    Parameters
    ----------
    first_string : Base string to concatenate
    args : Strings tuple

    Returns
    -------
    Concatenated string
    """
    return first_string % args

