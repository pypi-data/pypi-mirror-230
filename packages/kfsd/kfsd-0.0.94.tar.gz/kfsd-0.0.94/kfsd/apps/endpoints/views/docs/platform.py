from drf_spectacular.utils import extend_schema

from kfsd.apps.endpoints.views.docs.v1.platform import PlatformV1Doc
from kfsd.apps.endpoints.serializers.common.platform import PlatformViewModelSerializer
from kfsd.apps.endpoints.serializers.base import (
    NotFoundSerializer,
    ErrorSerializer,
)


class PlatformDoc:
    @staticmethod
    def modelviewset():
        return {
            "list": extend_schema(**PlatformDoc.modelviewset_list()),
            "retrieve": extend_schema(**PlatformDoc.modelviewset_get()),
            "destroy": extend_schema(**PlatformDoc.modelviewset_delete()),
            "partial_update": extend_schema(**PlatformDoc.modelviewset_patch()),
            "create": extend_schema(**PlatformDoc.modelviewset_create()),
        }

    @staticmethod
    def modelviewset_patch():
        return {
            "summary": "Platform - Patch",
            "description": "Platform Patch",
            "tags": ["PLATFORM"],
            "responses": {
                200: PlatformViewModelSerializer,
                404: NotFoundSerializer,
                500: ErrorSerializer,
            },
            "parameters": PlatformV1Doc.modelviewset_patch_path_examples(),
            "examples": PlatformV1Doc.modelviewset_patch_examples(),
        }

    @staticmethod
    def modelviewset_list():
        return {
            "summary": "Platform - List",
            "description": "Platform - All",
            "tags": ["PLATFORM"],
            "responses": {
                200: PlatformViewModelSerializer,
                404: NotFoundSerializer,
                500: ErrorSerializer,
            },
            "parameters": PlatformV1Doc.modelviewset_list_path_examples(),
            "examples": PlatformV1Doc.modelviewset_list_examples(),
        }

    @staticmethod
    def modelviewset_get():
        return {
            "summary": "Platform - Get",
            "description": "Platform Detail",
            "tags": ["PLATFORM"],
            "responses": {
                200: PlatformViewModelSerializer,
                404: NotFoundSerializer,
                500: ErrorSerializer,
            },
            "parameters": PlatformV1Doc.modelviewset_get_path_examples(),
            "examples": PlatformV1Doc.modelviewset_get_examples(),
        }

    @staticmethod
    def modelviewset_create():
        return {
            "summary": "Platform - Create",
            "description": "Platform - Create",
            "tags": ["PLATFORM"],
            "responses": {
                200: PlatformViewModelSerializer,
                400: ErrorSerializer,
                404: ErrorSerializer,
                500: ErrorSerializer,
            },
            "examples": PlatformV1Doc.modelviewset_create_examples(),
        }

    @staticmethod
    def modelviewset_delete():
        return {
            "summary": "Platform - Delete",
            "description": "Platform Delete",
            "tags": ["PLATFORM"],
            "responses": {204: None, 404: NotFoundSerializer, 500: ErrorSerializer},
            "parameters": PlatformV1Doc.modelviewset_delete_path_examples(),
        }
