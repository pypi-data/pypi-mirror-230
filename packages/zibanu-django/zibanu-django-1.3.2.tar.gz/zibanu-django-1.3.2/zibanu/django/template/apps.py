# -*- coding: utf-8 -*-

#  Developed by CQ Inversiones SAS. Copyright ©. 2019 - 2023. All rights reserved.
#  Desarrollado por CQ Inversiones SAS. Copyright ©. 2019 - 2023. Todos los derechos reservado

# ****************************************************************
# IDE:          PyCharm
# Developed by: macercha
# Date:         28/01/23 15:31
# Project:      Zibanu Django Project
# Module Name:  apps
# Description:
# ****************************************************************
from django.apps import AppConfig


class ZbDjangoTemplate(AppConfig):
    """
    Inherited class from django.apps.AppConfig to define configuration for zibanu.django.template
    """
    #TODO: Delete this app and move to zibanu.django
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'zibanu.django.template'
