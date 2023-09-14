# -*- coding: utf-8 -*-

#  Developed by CQ Inversiones SAS. Copyright ©. 2019 - 2022. All rights reserved.
#  Desarrollado por CQ Inversiones SAS. Copyright ©. 2019 - 2022. Todos los derechos reservado

# ****************************************************************
# IDE:          PyCharm
# Developed by: macercha
# Date:         13/12/22 10:14 AM
# Project:      Zibanu Django Project
# Module Name:  base_model
# Description:
# ****************************************************************
from django.db import models


class Model(models.Model):
    """
    Inherited abstract class from models.Model to add the "use_db" attribute.
    """
    # Protected attribute
    use_db = "default"

    def set(self, fields: dict):
        """
        Method to save a set of fields from a dictionary.

        Parameters
        ----------
        fields: Dictionary with fields keys and values.

        Returns
        -------
        None
        """
        for key, value in fields.items():
            if hasattr(self, key):
                setattr(self, key, value)
            self.save(force_update=True)

    class Meta:
        """
        Metaclass for Model class.
        """
        abstract = True


