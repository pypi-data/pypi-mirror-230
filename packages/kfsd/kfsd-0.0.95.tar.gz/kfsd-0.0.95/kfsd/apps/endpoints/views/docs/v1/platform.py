from drf_spectacular.utils import OpenApiExample, OpenApiTypes, OpenApiParameter


class PlatformV1Doc:
    @staticmethod
    def modelviewset_list_path_examples():
        return [
            OpenApiParameter(
                location=OpenApiParameter.QUERY,
                name="page",
                required=False,
                type=OpenApiTypes.INT,
                examples=[
                    OpenApiExample("Example 1", summary="Pagination", value=1),
                    OpenApiExample("Example 2", summary="Pagination", value=2),
                ],
            )
        ]

    @staticmethod
    def modelviewset_list_examples():
        return [
            OpenApiExample(
                "Platform - List All",
                value=[
                    {
                        "identifier": "TYPE=Social,PLATFORM=Facebook",
                        "type": "Social",
                        "slug": "social",
                    }
                ],
                request_only=False,
                response_only=True,
            )
        ]

    @staticmethod
    def modelviewset_get_path_examples():
        return [
            OpenApiParameter(
                location=OpenApiParameter.PATH,
                name="identifier",
                required=True,
                type=OpenApiTypes.STR,
                examples=[
                    OpenApiExample(
                        "Platform - Get",
                        summary="Platform Identifier",
                        description="Platform - Get",
                        value="TYPE=Social,PLATFORM=Facebook",
                    )
                ],
            )
        ]

    @staticmethod
    def modelviewset_get_examples():
        return [
            OpenApiExample(
                "Platform - Get",
                value={
                    "identifier": "TYPE=Social,PLATFORM=Facebook",
                    "type": "Social",
                    "slug": "social",
                },
                request_only=False,
                response_only=True,
            )
        ]

    @staticmethod
    def modelviewset_create_examples():
        return [
            OpenApiExample(
                "Platform - Create",
                value={
                    "identifier": "TYPE=Social,PLATFORM=Facebook",
                    "type": "Social",
                    "slug": "social",
                },
                request_only=True,
                response_only=False,
            ),
            OpenApiExample(
                "Platform - Create",
                value={
                    "identifier": "TYPE=Social,PLATFORM=Facebook",
                    "type": "Social",
                    "slug": "social",
                },
                request_only=False,
                response_only=True,
            ),
        ]

    @staticmethod
    def modelviewset_delete_path_examples():
        return [
            OpenApiParameter(
                location=OpenApiParameter.PATH,
                name="identifier",
                required=True,
                type=OpenApiTypes.STR,
                examples=[
                    OpenApiExample(
                        "Platform - Delete",
                        summary="Platform Identifier",
                        description="Platform - Delete",
                        value="TYPE=Social,PLATFORM=Facebook",
                    )
                ],
            )
        ]

    @staticmethod
    def modelviewset_patch_path_examples():
        return [
            OpenApiParameter(
                location=OpenApiParameter.PATH,
                name="identifier",
                required=True,
                type=OpenApiTypes.STR,
                examples=[
                    OpenApiExample(
                        "Platform - Patch",
                        summary="Platform Identifier",
                        description="Platform - Patch",
                        value="TYPE=Social,PLATFORM=Facebook",
                    )
                ],
            )
        ]

    @staticmethod
    def modelviewset_patch_examples():
        return [
            OpenApiExample(
                "Platform - Patch",
                value={
                    "slug": "social",
                },
                request_only=True,
                response_only=False,
            ),
            OpenApiExample(
                "Platform - Patch",
                value={
                    "identifier": "TYPE=Social,PLATFORM=Facebook",
                    "type": "Social",
                    "slug": "social",
                },
                request_only=False,
                response_only=True,
            ),
        ]
