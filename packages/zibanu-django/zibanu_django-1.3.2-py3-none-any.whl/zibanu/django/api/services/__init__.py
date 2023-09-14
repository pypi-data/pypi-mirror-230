# -*- coding: utf-8 -*-

# ****************************************************************
# IDE:          PyCharm
# Developed by: macercha
# Date:         7/07/23 7:31
# Project:      Zibanu - Django
# Module Name:  __init__.py
# Description:
# ****************************************************************
from .timezone import TimeZoneViewSet
from .language import LanguageViewSet

__all__ = [
    "LanguageViewSet",
    "TimeZoneViewSet"
]