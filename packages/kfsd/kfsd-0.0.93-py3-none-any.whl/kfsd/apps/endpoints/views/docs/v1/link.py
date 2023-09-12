from drf_spectacular.utils import OpenApiExample, OpenApiTypes, OpenApiParameter


class LinkV1Doc:
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
                "Link - List All",
                value=[
                    {
                        "identifier": "TYPE=Social,PLATFORM=Facebook,LINK_ID=abcde",
                        "link": "https://www.facebook.com/nathangokul/",
                        "platform": "TYPE=Social,PLATFORM=Facebook",
                        "link_id": "abcde",
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
                        "Link - Get",
                        summary="Link Identifier",
                        description="Link - Get",
                        value="TYPE=Social,PLATFORM=Facebook,LINK_ID=abcde",
                    )
                ],
            )
        ]

    @staticmethod
    def modelviewset_get_examples():
        return [
            OpenApiExample(
                "Link - Get",
                value={
                    "identifier": "TYPE=Social,PLATFORM=Facebook,LINK_ID=abcde",
                    "link": "https://www.facebook.com/nathangokul/",
                    "platform": "TYPE=Social,PLATFORM=Facebook",
                    "link_id": "abcde",
                },
                request_only=False,
                response_only=True,
            )
        ]

    @staticmethod
    def modelviewset_create_examples():
        return [
            OpenApiExample(
                "Link - Create (with platform)",
                value={
                    "link": "https://www.facebook.com/nathangokul/",
                    "platform": "TYPE=Social,PLATFORM=Facebook",
                },
                request_only=True,
                response_only=False,
            ),
            OpenApiExample(
                "Link - Create (no platform)",
                value={"link": "https://www.facebook.com/nathangokul/"},
                request_only=True,
                response_only=False,
            ),
            OpenApiExample(
                "Link - Create (with platform)",
                value={
                    "identifier": "TYPE=Social,PLATFORM=Facebook,LINK_ID=abcde",
                    "link": "https://www.facebook.com/nathangokul/",
                    "platform": "TYPE=Social,PLATFORM=Facebook",
                    "link_id": "abcde",
                },
                request_only=False,
                response_only=True,
            ),
            OpenApiExample(
                "Link - Create (no platform)",
                value={
                    "identifier": "LINK_ID=abcde",
                    "link": "https://www.facebook.com/nathangokul/",
                    "platform": "",
                    "link_id": "abcde",
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
                        "Link - Delete",
                        summary="Link Identifier",
                        description="Link - Delete",
                        value="TYPE=Social,PLATFORM=Facebook,LINK_ID=abcde",
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
                        "Link - Patch",
                        summary="Link Identifier",
                        description="Link - Patch",
                        value="TYPE=Social,PLATFORM=Facebook,LINK_ID=abcde",
                    )
                ],
            )
        ]

    @staticmethod
    def modelviewset_patch_examples():
        return [
            OpenApiExample(
                "Link - Patch",
                value={
                    "link": "https://www.facebook.com/nathangokul/",
                },
                request_only=True,
                response_only=False,
            ),
            OpenApiExample(
                "Link - Patch",
                value={
                    "identifier": "TYPE=Social,PLATFORM=Facebook,LINK_ID=abcde",
                    "link": "https://www.facebook.com/nathangokul/",
                    "platform": "TYPE=Social,PLATFORM=Facebook",
                    "link_id": "abcde",
                },
                request_only=False,
                response_only=True,
            ),
        ]
