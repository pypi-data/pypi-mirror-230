from rest_framework.views import Response, exception_handler
from rest_framework import status
import json
import traceback
from django.conf import settings
from rest_framework.exceptions import ValidationError
from django.db import IntegrityError
from django.core.exceptions import ValidationError as CoreValidationError
from kfsd.apps.core.exceptions.api import KubefacetsAPIException


def KubefacetsAPIExceptionHandler(ex, context):
    response = exception_handler(ex, context)
    request = context["request"]
    errorData = {
        "status": "ERROR",
        "path": request.path,
        "method": request.method,
        "content_type": request.content_type,
        "query_params": request.query_params,
        "body": request.data,
        "cookies": request.COOKIES,
        "error": ex.__str__(),
    }
    try:
        errorJson = json.dumps(errorData, indent=4)
        print(errorJson)
    except Exception:
        print("Error: {}".format(errorData))

    # print error to console
    if settings.DEBUG:
        print("[[ STACKTRACE ]]")
        traceback.print_exc()

    if isinstance(ex, IntegrityError) and not response:
        response = Response(
            {"detail": ex.__str__(), "code": "bad_request"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    if isinstance(ex, TypeError) and not response:
        response = Response(
            {"detail": ex.__str__(), "code": "system_error"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    if isinstance(ex, ValidationError):
        response = Response(
            {"detail": ex.args[0], "code": "bad_request"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    if isinstance(ex, CoreValidationError):
        response = Response(
            {"detail": ex.args[0], "code": "bad_request"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    if isinstance(ex, KubefacetsAPIException):
        response = Response(
            {"detail": ex.detail, "code": ex.default_code}, status=ex.status_code
        )
    return response
