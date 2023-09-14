# -*- coding: utf-8 -*-

#  Developed by CQ Inversiones SAS. Copyright ©. 2019 - 2023. All rights reserved.
#  Desarrollado por CQ Inversiones SAS. Copyright ©. 2019 - 2023. Todos los derechos reservado

# ****************************************************************
# IDE:          PyCharm
# Developed by: macercha
# Date:         28/01/23 15:33
# Project:      Zibanu Django Project
# Module Name:  static_uri
# Description:
# ****************************************************************
from django import template
from django.conf import settings
from django.utils.translation import gettext_lazy as _

register = template.Library()


class StaticNodeUri(template.Node):
    """
    Inherited class from django.template.Node to allow the use of template tag "static_uri" in django templates.
    """
    def __init__(self, uri_string: str):
        """
        Constructor method.

        Parameters
        ----------
        uri_string : URI string received from template
        """
        self._static_uri = uri_string

    def render(self, context):
        """
        Override method to render the tag in template.

        Parameters
        ----------
        context : Context dictionary object from template

        Returns
        -------
        uri: String to render in template
        """
        if hasattr(context, "request"):
            request = context.get("request")
            if hasattr(settings, "STATIC_URL"):
                uri = request.build_absolute_uri(settings.STATIC_URL)
                uri = uri + self._static_uri
            else:
                raise template.TemplateSyntaxError(_("'STATIC_URL' setting is not defined."))
        else:
            raise template.TemplateSyntaxError(_("Tag 'static_uri' requires 'request' var in context."))
        return uri


@register.tag("static_uri")
def static_uri(parse, token):
    """
    Function to register tag in template

    Parameters
    ----------
    parse : Parse object from template
    token : Token object from template

    Returns
    -------
    StaticNodeUri class to be called from template and render it.
    """
    try:
        tag_name, uri_string = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError("")

    return StaticNodeUri(uri_string[1:-1])



