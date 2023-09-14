# -*- coding: utf-8 -*-

#  Developed by CQ Inversiones SAS. Copyright ©. 2019 - 2023. All rights reserved.
#  Desarrollado por CQ Inversiones SAS. Copyright ©. 2019 - 2023. Todos los derechos reservado

# ****************************************************************
# IDE:          PyCharm
# Developed by: macercha
# Date:         10/01/23 1:47 PM
# Project:      Zibanu Django Project
# Module Name:  code_generator
# Description:
# ****************************************************************
import logging
import os
import string
import secrets
import traceback
from django.utils.translation import gettext_lazy as _
from uuid import SafeUUID, UUID


class CodeGenerator:
    """
    Class to generate different types of codes randomly.
    """
    def __init__(self, action: str, is_safe: bool = True, code_length: int = 6):
        """
        Constructor method

        Parameters
        ----------
        action : Code of action to reference it at cache if needed.
        is_safe : Flag to indicate if it uses UUID safe mode.
        code_length : Length of generated code
        """
        self.__action = action
        self._uuid_safe = SafeUUID.safe if is_safe else SafeUUID.unsafe
        self.__code_length = code_length
        self.__code = None
        self.__uuid = None

    @property
    def is_safe(self):
        """
        Property getter for _uuid_safe value

        Returns
        -------
        Boolean value: True if UUID uses safe mode, otherwise False
        """
        return self._uuid_safe == SafeUUID.safe

    @is_safe.setter
    def is_safe(self, value: bool):
        """
        Property setter for _uuid_safe value

        Parameters
        ----------
        value : Boolean parameter to set SafeUUID.safe if True, else set SafeUUID.unsafe
        """
        self._uuid_safe = SafeUUID.safe if value else SafeUUID.unsafe

    @property
    def code(self) -> str:
        """
        Property getter for __code value

        Returns
        -------
        String value with generated code
        """
        return self.__code

    @property
    def action(self) -> str:
        """
        Property getter for __action value

        Returns
        -------
        String value with action description
        """
        return self.__action

    def get_numeric_code(self, length: int = None) -> str:
        """
        Get a numeric code with the length defined in the constructor or received in the parameter "length" of this method.

        Parameters
        ----------
        length : Length of generated code. Override length defined in the class.

        Returns
        -------
        String with numeric code
        """
        if length is not None:
            self.__code_length = length
        self.__code = "".join(secrets.choice(string.digits) for i in range(self.__code_length))
        return self.code

    def get_alpha_numeric_code(self, length: int = None) -> str:
        """
        Get an alphanumeric code with the length defined in the constructor or received in the parameter "length" of this method.

        Parameters
        ----------
        length : Length of generated code. This parameter override length defined in the class.

        Returns
        -------
        String with numeric code
        """
        if length is not None:
            self.__code_length = length
        self.__code = "".join(secrets.choice(string.digits + string.ascii_letters) for i in range(self.__code_length))
        return self.code

    def get_secure_code(self, length: int = None) -> str:
        """
        Get a secure code with the length defined in the constructor or received in the parameter "length" of this method.

        Parameters
        ----------
        length : Length of generated code. This parameter override length defined in the class.

        Returns
        -------
        String with numeric code
        """
        if length is not None:
            self.__code_length = length
        self.__code = "".join(secrets.choice(string.digits + string.ascii_letters + string.punctuation) for i in range(self.__code_length))
        return self.code

    def generate_uuid(self) -> bool:
        """
        Method to generate a UUID in safe mode, depending on the parameter set in the constructor

        Returns
        -------
        True if successfully, otherwise False.
        """
        try:
            self.__uuid = UUID(bytes=os.urandom(16), version=4, is_safe=self._uuid_safe)
        except Exception as exc:
            logging.warning(str(exc))
            logging.debug(traceback.format_exc())
            return False
        else:
            return True

    def generate_dict(self, is_numeric: bool = True) -> dict:
        """
        Method to generate a dictionary with uuid, code and action.

        Parameters
        ----------
        is_numeric : Flag to indicate if generated code is numeric or alphanumeric.

        Returns
        -------
        Dictionary with uuid, code and action keys.
        """
        if is_numeric:
            self.get_numeric_code()
        else:
            self.get_alpha_numeric_code()

        if self.generate_uuid():
            return {"uuid": self.__uuid, "code": self.code, "action": self.action}
        else:
            raise ValueError(_("The generated values are invalid."))
