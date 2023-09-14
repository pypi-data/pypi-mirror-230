# -*- coding: utf-8 -*-

#  Developed by CQ Inversiones SAS. Copyright ©. 2019 - 2023. All rights reserved.
#  Desarrollado por CQ Inversiones SAS. Copyright ©. 2019 - 2023. Todos los derechos reservado

# ****************************************************************
# IDE:          PyCharm
# Developed by: macercha
# Date:         16/02/23 9:03
# Project:      Zibanu Django Project
# Module Name:  subtotal_dict
# Description:
# ****************************************************************
from django import template
from django.utils.translation import gettext_lazy as _


register = template.Library()


@register.simple_tag
def subtotal_dict(source_list: list, key_control: str, *args) -> list:
    """
    Template tag to get a subtotal from a list of dictionary records.

    Parameters
    ----------
    source_list : List with all data dictionary.
    key_control : Key use to index and make the breaks for subtotals.
    args : Tuple with list of key names to get the subtotals.

    Returns
    -------
    return_list: List with a data dictionary with the keys "control", "totals" and data", which contains the subtotals like this:
        control -> Value from source_list for key_control key.
        totals -> Total for key_control
        data -> list with data from source_list with a key different from key_control param value.
    """
    if args is not None:
        key_value = None
        return_list = []
        item_dict = {
            "control": None,
            "totals": dict(),
            "data": []
        }

        for record in source_list:
            data_dict = dict()
            if key_value is None or key_value != record[key_control]:
                # Add Control var and dict
                if key_value is not None:
                    return_list.append(item_dict)
                key_value = record[key_control]
                # Init vars on change key_value
                item_dict = {
                    "control": record[key_control],
                    "totals": dict(),
                    "data": []
                }
                for param in args:
                    item_dict["totals"][param] = 0

            for key_item in record.keys():
                if key_item != key_control:
                    data_dict[key_item] = record.get(key_item)

                if key_item in item_dict.get("totals").keys():
                    item_dict["totals"][key_item] += record[key_item]

            item_dict["data"].append(data_dict)
        return_list.append(item_dict)
    else:
        raise template.TemplateSyntaxError(_("The keys for subtotals are required."))

    return return_list



