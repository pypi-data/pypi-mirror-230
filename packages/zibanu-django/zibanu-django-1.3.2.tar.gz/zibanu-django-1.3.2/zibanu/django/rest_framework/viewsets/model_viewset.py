# -*- coding: utf-8 -*-

#  Developed by CQ Inversiones SAS. Copyright ©. 2019 - 2022. All rights reserved.
#  Desarrollado por CQ Inversiones SAS. Copyright ©. 2019 - 2022. Todos los derechos reservado

# ****************************************************************
# IDE:          PyCharm
# Developed by: macercha
# Date:         19/12/22 3:18 PM
# Project:      Zibanu Django Project
# Module Name:  model_viewset
# Description:
# ****************************************************************
import logging
import traceback
from django.db import DatabaseError
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import authentication
from rest_framework import permissions
from rest_framework import status
from rest_framework.generics import QuerySet
from rest_framework.viewsets import ModelViewSet as RestModelViewSet
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTTokenUserAuthentication
from zibanu.django.rest_framework.exceptions import APIException
from zibanu.django.rest_framework.exceptions import ValidationError
from zibanu.django.utils import ErrorMessages
from typing import Any


class ModelViewSet(RestModelViewSet):
    """
    Inherited class from rest_framework.viewsets.ModelViewSet to override
    """
    logger = logging.getLogger(__name__)
    model = None
    http_method_names = ["post"]
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [JWTTokenUserAuthentication]

    if settings.DEBUG:
        authentication_classes.append(authentication.TokenAuthentication)

    @staticmethod
    def _get_pk(request) -> Any:
        """
        Get PK value from received request data dictionary.

        Parameters
        ----------
        request: Request object from HTTP

        Returns
        -------
        pk_value: Value obtained from request.data
        """
        if request.data is not None:
            if "pk" in request.data.keys():
                pk_value = request.data.get("pk", None)
            elif "id" in request.data.keys():
                pk_value = request.data.get("id", None)
            else:
                raise APIException(ErrorMessages.DATA_REQUIRED, "get_pk", status.HTTP_406_NOT_ACCEPTABLE)
        else:
            raise APIException(ErrorMessages.DATA_REQUIRED, "get_pk", status.HTTP_406_NOT_ACCEPTABLE)
        return pk_value

    def get_queryset(self, **kwargs) -> QuerySet:
        """
        Get a queryset from model from **kwargs parameters. If you want queryset pk based on, send "pk" key in kwargs.
        Parameters
        ----------
        **kwargs: Dictionary with key, value parameters.

        Returns
        -------
        qs: Queryset object from model
        """
        pk = kwargs.get("pk", None)
        qs = self.model.objects.get_queryset()
        if pk is not None:
            qs = qs.filter(pk=pk)
        elif len(kwargs) > 0:
            qs = qs.filter(**kwargs)
        else:
            qs = qs.all()

        return qs

    def list(self, request, *args, **kwargs) -> Response:
        """
        REST service to get a list of records from class defined model.

        Parameters
        ----------
        request: Request object from HTTP
        *args: Tuple of parameters
        **kwargs: Dictionary of key, value parameters.

        Returns
        -------
        response: Response object with status and dataset list.
            status -> 200 if data exists
            status -> 204 if empty data
        """
        try:
            # Get Order by
            order_by = None
            if "order_by" in kwargs.keys():
                order_by = kwargs.pop("order_by")

            qs = self.get_queryset(**kwargs)

            # Set Order by
            if order_by is not None:
                qs = qs.order_by(order_by)

            serializer = self.get_serializer(instance=qs, many=True)
            data_return = serializer.data
            status_return = status.HTTP_200_OK if len(data_return) > 0 else status.HTTP_204_NO_CONTENT
            data_return = data_return
        except APIException as exc:
            raise APIException(msg=exc.detail.get("message"), error=exc.detail.get("detail"),
                               http_status=exc.status_code) from exc
        except Exception as exc:
            logging.error(str(exc))
            logging.debug(traceback.format_exc())
            raise APIException(error=str(exc), http_status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response(data=data_return, status=status_return)

    def retrieve(self, request, *args, **kwargs) -> Response:
        """
        REST service to get a record filtered by pk.

        Parameters
        ----------
        request: Request object from HTTP
        *args: Tuple of parameters values
        **kwargs: Dictionary with key, value parameter

        Returns
        -------
        response: Response object with status 200 if record exists and data record. If record does not exist, an exception is launched.
        """
        try:
            pk = self._get_pk(request)
            data_record = self.get_queryset(pk=pk).get()
            data_return = self.get_serializer(data_record).data
            status_return = status.HTTP_200_OK
        except ObjectDoesNotExist as exc:
            raise APIException(ErrorMessages.NOT_FOUND, str(exc), http_status=status.HTTP_404_NOT_FOUND) from exc
        except APIException as exc:
            raise APIException(exc.detail.get("message"), exc.detail.get("detail"), exc.status_code) from exc
        except Exception as exc:
            logging.error(str(exc))
            logging.debug(traceback.format_exc())
            raise APIException(error=str(exc), http_status=status.HTTP_500_INTERNAL_SERVER_ERROR) from exc
        else:
            return Response(status=status_return, data=data_return)

    def create(self, request, *args, **kwargs) -> Response:
        """
        REST service for create a model record.

        Parameters
        ----------
        request: Request object from HTTP
        *args: Tuple of parameters values
        **kwargs: Dictionary with key, value parameter

        Returns
        -------
        response: Response object with status 201 if successfully and record created from model object.
        """
        try:
            data_return = []
            status_return = status.HTTP_400_BAD_REQUEST
            request_data = request.data
            if len(request_data) > 0:
                serializer = self.get_serializer(data=request_data)
                if serializer.is_valid(raise_exception=True):
                    created_record = serializer.create(validated_data=serializer.validated_data)
                    if created_record is not None:
                        data_return = self.get_serializer(created_record).data
                        status_return = status.HTTP_201_CREATED
                    else:
                        raise ValidationError(ErrorMessages.CREATE_ERROR, "create_object")
            else:
                raise APIException(ErrorMessages.DATA_REQUIRED, "data_required")
        except DatabaseError as exc:
            raise APIException(ErrorMessages.DATABASE_ERROR, str(exc)) from exc
        except ValidationError as exc:
            raise APIException(error=str(exc.detail[0]), http_status=status.HTTP_406_NOT_ACCEPTABLE) from exc
        except APIException as exc:
            raise APIException(exc.detail.get("message"), exc.detail.get("detail"), exc.status_code) from exc
        except Exception as exc:
            logging.error(str(exc))
            logging.debug(traceback.format_exc())
            raise APIException(error=str(exc), http_status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response(status=status_return, data=data_return)

    def update(self, request, *args, **kwargs) -> Response:
        """
        REST service to update an existent record from model.

        Parameters
        ----------
        request: Request object from HTTP
        *args: Tuple of parameters values
        **kwargs: Dictionary with key, value parameter

        Returns
        -------
        response: Response object with status 200 if successfully and record updated from model object.
        """
        try:
            pk = self._get_pk(request)
            data_record = self.get_queryset(pk=pk).get()
            serializer = self.get_serializer(data_record, data=request.data)
            if serializer.instance and serializer.is_valid(raise_exception=True):
                updated = serializer.update(instance=serializer.instance, validated_data=serializer.validated_data)
                if updated is not None:
                    data_return = self.get_serializer(updated).data
                    status_return = status.HTTP_200_OK
                else:
                    raise APIException(ErrorMessages.UPDATE_ERROR, "update", status.HTTP_418_IM_A_TEAPOT)
            else:
                raise APIException(ErrorMessages.NOT_FOUND, "update", status.HTTP_404_NOT_FOUND)
        except ObjectDoesNotExist as exc:
            raise APIException(ErrorMessages.NOT_FOUND, "update", status.HTTP_404_NOT_FOUND) from exc
        except DatabaseError as exc:
            raise APIException(ErrorMessages.UPDATE_ERROR, str(exc)) from exc
        except ValidationError as exc:
            raise APIException(error=str(exc.detail), http_status=status.HTTP_406_NOT_ACCEPTABLE) from exc
        except APIException as exc:
            raise APIException(exc.detail.get("message"), exc.detail.get("detail"), exc.status_code) from exc
        except Exception as exc:
            logging.error(str(exc))
            logging.debug(traceback.format_exc())
            raise APIException(error=str(exc), http_status=status.HTTP_500_INTERNAL_SERVER_ERROR) from exc
        else:
            return Response(data=data_return, status=status_return)

    def destroy(self, request, *args, **kwargs) -> Response:
        """
        REST service to delete a record from model.

        Parameters
        ----------
        request: Request object from HTTP
        *args: Tuple of parameters values
        **kwargs: Dictionary with key, value parameter

        Returns
        -------
        response: Response object with status 200 if successfully.
        """
        try:
            pk = self._get_pk(request)
            data_record = self.get_queryset(pk=pk)
            if data_record:
                data_record.delete()
                status_return = status.HTTP_200_OK
            else:
                raise APIException(ErrorMessages.DELETE_ERROR, "delete", status.HTTP_404_NOT_FOUND)
        except DatabaseError as exc:
            raise APIException(ErrorMessages.UPDATE_ERROR, str(exc)) from exc
        except ValidationError as exc:
            raise APIException(error=str(exc.detail), http_status=status.HTTP_406_NOT_ACCEPTABLE) from exc
        except APIException as exc:
            raise APIException(exc.detail.get("message"), exc.detail.get("detail"), exc.status_code) from exc
        except Exception as exc:
            logging.error(str(exc))
            logging.debug(traceback.format_exc())
            raise APIException(error=str(exc), http_status=status.HTTP_500_INTERNAL_SERVER_ERROR) from exc
        else:
            return Response(status=status_return)
