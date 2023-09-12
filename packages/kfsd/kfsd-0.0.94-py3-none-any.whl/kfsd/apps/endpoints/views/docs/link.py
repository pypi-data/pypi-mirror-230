from drf_spectacular.utils import extend_schema

from kfsd.apps.endpoints.views.docs.v1.link import LinkV1Doc
from kfsd.apps.endpoints.serializers.common.link import LinkViewModelSerializer
from kfsd.apps.endpoints.serializers.base import (
    NotFoundSerializer,
    ErrorSerializer,
)


class LinkDoc:
    @staticmethod
    def modelviewset():
        return {
            "list": extend_schema(**LinkDoc.modelviewset_list()),
            "retrieve": extend_schema(**LinkDoc.modelviewset_get()),
            "destroy": extend_schema(**LinkDoc.modelviewset_delete()),
            "partial_update": extend_schema(**LinkDoc.modelviewset_patch()),
            "create": extend_schema(**LinkDoc.modelviewset_create()),
        }

    @staticmethod
    def modelviewset_patch():
        return {
            "summary": "Link - Patch",
            "description": "Link Patch",
            "tags": ["LINK"],
            "responses": {
                200: LinkViewModelSerializer,
                404: NotFoundSerializer,
                500: ErrorSerializer,
            },
            "parameters": LinkV1Doc.modelviewset_patch_path_examples(),
            "examples": LinkV1Doc.modelviewset_patch_examples(),
        }

    @staticmethod
    def modelviewset_list():
        return {
            "summary": "Link - List",
            "description": "Link - All",
            "tags": ["LINK"],
            "responses": {
                200: LinkViewModelSerializer,
                404: NotFoundSerializer,
                500: ErrorSerializer,
            },
            "parameters": LinkV1Doc.modelviewset_list_path_examples(),
            "examples": LinkV1Doc.modelviewset_list_examples(),
        }

    @staticmethod
    def modelviewset_get():
        return {
            "summary": "Link - Get",
            "description": "Link Detail",
            "tags": ["LINK"],
            "responses": {
                200: LinkViewModelSerializer,
                404: NotFoundSerializer,
                500: ErrorSerializer,
            },
            "parameters": LinkV1Doc.modelviewset_get_path_examples(),
            "examples": LinkV1Doc.modelviewset_get_examples(),
        }

    @staticmethod
    def modelviewset_create():
        return {
            "summary": "Link - Create",
            "description": "Link - Create",
            "tags": ["LINK"],
            "responses": {
                200: LinkViewModelSerializer,
                400: ErrorSerializer,
                404: ErrorSerializer,
                500: ErrorSerializer,
            },
            "examples": LinkV1Doc.modelviewset_create_examples(),
        }

    @staticmethod
    def modelviewset_delete():
        return {
            "summary": "Link - Delete",
            "description": "Link Delete",
            "tags": ["LINK"],
            "responses": {204: None, 404: NotFoundSerializer, 500: ErrorSerializer},
            "parameters": LinkV1Doc.modelviewset_delete_path_examples(),
        }
