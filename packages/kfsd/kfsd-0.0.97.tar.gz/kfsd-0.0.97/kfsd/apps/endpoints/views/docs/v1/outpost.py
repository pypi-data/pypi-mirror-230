from drf_spectacular.utils import OpenApiExample, OpenApiTypes, OpenApiParameter


class OutpostV1Doc:
    @staticmethod
    def send_all_view_examples():
        return [
            OpenApiExample(
                "Outpost - Send All",
                value={"detail": "ok"},
                request_only=False,
                response_only=True,
            ),
        ]

    @staticmethod
    def modelviewset_list_path_examples():
        return []

    @staticmethod
    def modelviewset_list_examples():
        return [
            OpenApiExample(
                "Outpost - List All",
                value=[
                    {
                        "identifier": "9fe1f2f2221c6b6a0f28dde862d55299",
                        "msg_queue_info": {
                            "exchange": "kubefacets.exchange",
                            "routing_key": "producer.actions.remind.create_reminder",
                            "properties": {"delivery_mode": 2},
                        },
                        "msg": {
                            "action": "CREATE_REMINDER",
                            "data": {
                                "identifier": "ORG=Kubefacets,APP=Certs,PRJ=Auth,COLL=Login,CSR=kubefacets Root CA",
                                "type": "ONETIME",
                                "remind_by_in_mins": 10,
                                "to_msg_queue": {
                                    "exchange": "kubefacets.exchange",
                                    "routing_key": "producer.actions.certs.reorder_cert",
                                    "properties": {"delivery_mode": 2},
                                },
                                "msg": {
                                    "action": "REORDER_CERT",
                                    "data": {
                                        "identifier": "ORG=Kubefacets,APP=Certs,PRJ=Auth,COLL=Login,CSR=kubefacets Root CA",
                                    },
                                },
                            },
                        },
                        "status": "IN-PROGRESS",
                        "attempts": 0,
                        "debug_info": {},
                    },
                    {
                        "identifier": "7b7ffebd901976a771f0a51cd7e4aedc",
                        "msg_queue_info": {
                            "exchange_name": "remind.exchange",
                            "queue_name": "remind.queue",
                            "routing_key": "remind.queue.route.key",
                        },
                        "msg": {
                            "action": "CREATE_REMINDER",
                            "data": {
                                "identifier": "ORG=Kubefacets,APP=Certs,PRJ=Auth,COLL=Login,CSR=kubefacets Root CA",
                                "type": "ONETIME",
                                "remind_by_in_mins": 10,
                                "to_msg_queue": {
                                    "exchange_name": "certs.exchange",
                                    "queue_name": "certs.queue",
                                    "routing_key": "certs.queue.route.key",
                                },
                                "msg": {
                                    "action": "REORDER_CERT",
                                    "data": {
                                        "identifier": "ORG=Kubefacets,APP=Certs,PRJ=Auth,COLL=Login,CSR=kubefacets Root CA",
                                    },
                                },
                            },
                        },
                        "status": "IN-PROGRESS",
                        "attempts": 0,
                        "debug_info": {},
                    },
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
                        "Outpost - Get",
                        summary="Outpost Identifier",
                        description="Outpost - Get",
                        value="9fe1f2f2221c6b6a0f28dde862d55299",
                    )
                ],
            )
        ]

    @staticmethod
    def modelviewset_get_examples():
        return [
            OpenApiExample(
                "Outpost - Get",
                value={
                    "identifier": "9fe1f2f2221c6b6a0f28dde862d55299",
                    "msg_queue_info": {
                        "exchange_name": "remind.exchange",
                        "queue_name": "remind.queue",
                        "routing_key": "remind.queue.route.key",
                    },
                    "msg": {
                        "action": "CREATE_REMINDER",
                        "data": {
                            "identifier": "ORG=Kubefacets,APP=Certs,PRJ=Auth,COLL=Login,CSR=kubefacets Root CA",
                            "type": "ONETIME",
                            "remind_by_in_mins": 10,
                            "to_msg_queue": {
                                "exchange_name": "certs.exchange",
                                "queue_name": "certs.queue",
                                "routing_key": "certs.queue.route.key",
                            },
                            "msg": {
                                "action": "REORDER_CERT",
                                "data": {
                                    "identifier": "ORG=Kubefacets,APP=Certs,PRJ=Auth,COLL=Login,CSR=kubefacets Root CA",
                                },
                            },
                        },
                    },
                    "status": "IN-PROGRESS",
                    "attempts": 0,
                    "debug_info": {},
                },
                request_only=False,
                response_only=True,
            )
        ]

    @staticmethod
    def modelviewset_create_examples():
        return [
            OpenApiExample(
                "Outpost - Create",
                value={
                    "msg_queue_info": {
                        "exchange_name": "remind.exchange",
                        "queue_name": "remind.queue",
                        "routing_key": "remind.queue.route.key",
                    },
                    "msg": {
                        "action": "CREATE_REMINDER",
                        "data": {
                            "identifier": "ORG=Kubefacets,APP=Certs,PRJ=Auth,COLL=Login,CSR=kubefacets Root CA",
                            "type": "ONETIME",
                            "remind_by_in_mins": 10,
                            "to_msg_queue": {
                                "exchange_name": "certs.exchange",
                                "queue_name": "certs.queue",
                                "routing_key": "certs.queue.route.key",
                            },
                            "msg": {
                                "action": "REORDER_CERT",
                                "data": {
                                    "identifier": "ORG=Kubefacets,APP=Certs,PRJ=Auth,COLL=Login,CSR=kubefacets Root CA",
                                },
                            },
                        },
                    },
                },
                request_only=True,
                response_only=False,
            ),
            OpenApiExample(
                "Outpost - Create",
                value={
                    "identifier": "9fe1f2f2221c6b6a0f28dde862d55299",
                    "msg_queue_info": {
                        "exchange_name": "remind.exchange",
                        "queue_name": "remind.queue",
                        "routing_key": "remind.queue.route.key",
                    },
                    "msg": {
                        "action": "CREATE_REMINDER",
                        "data": {
                            "identifier": "ORG=Kubefacets,APP=Certs,PRJ=Auth,COLL=Login,CSR=kubefacets Root CA",
                            "type": "ONETIME",
                            "remind_by_in_mins": 10,
                            "to_msg_queue": {
                                "exchange_name": "certs.exchange",
                                "queue_name": "certs.queue",
                                "routing_key": "certs.queue.route.key",
                            },
                            "msg": {
                                "action": "REORDER_CERT",
                                "data": {
                                    "identifier": "ORG=Kubefacets,APP=Certs,PRJ=Auth,COLL=Login,CSR=kubefacets Root CA",
                                },
                            },
                        },
                    },
                    "status": "IN-PROGRESS",
                    "attempts": 0,
                    "debug_info": {},
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
                        "Outpost - Delete",
                        summary="Outpost Identifier",
                        description="Outpost - Delete",
                        value="9fe1f2f2221c6b6a0f28dde862d55299",
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
                        "Outpost - Delete",
                        summary="Outpost Identifier",
                        description="Outpost - Delete",
                        value="9fe1f2f2221c6b6a0f28dde862d55299",
                    )
                ],
            )
        ]

    @staticmethod
    def modelviewset_patch_examples():
        return [
            OpenApiExample(
                "Outpost - Patch",
                value={
                    "msg_queue_info": {
                        "exchange_name": "remind.exchange1",
                        "queue_name": "remind.queue",
                        "routing_key": "remind.queue.route.key",
                    },
                },
                request_only=True,
                response_only=False,
            ),
            OpenApiExample(
                "Outpost - Patch",
                value={
                    "identifier": "9fe1f2f2221c6b6a0f28dde862d55299",
                    "msg_queue_info": {
                        "exchange_name": "remind.exchange1",
                        "queue_name": "remind.queue",
                        "routing_key": "remind.queue.route.key",
                    },
                    "msg": {
                        "action": "CREATE_REMINDER",
                        "data": {
                            "identifier": "ORG=Kubefacets,APP=Certs,PRJ=Auth,COLL=Login,CSR=kubefacets Root CA",
                            "type": "ONETIME",
                            "remind_by_in_mins": 10,
                            "to_msg_queue": {
                                "exchange_name": "certs.exchange",
                                "queue_name": "certs.queue",
                                "routing_key": "certs.queue.route.key",
                            },
                            "msg": {
                                "action": "REORDER_CERT",
                                "data": {
                                    "identifier": "ORG=Kubefacets,APP=Certs,PRJ=Auth,COLL=Login,CSR=kubefacets Root CA",
                                },
                            },
                        },
                    },
                    "status": "IN-PROGRESS",
                    "attempts": 0,
                    "debug_info": {},
                },
                request_only=False,
                response_only=True,
            ),
        ]
