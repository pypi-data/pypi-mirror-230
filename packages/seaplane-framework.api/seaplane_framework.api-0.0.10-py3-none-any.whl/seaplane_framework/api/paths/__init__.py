# do not import all endpoints into this module because that uses a lot of memory and stack frames
# if you need the ability to import all endpoints from this module, import them with
# from seaplane_framework.api.apis.path_to_api import path_to_api

import enum


class PathValues(str, enum.Enum):
    STREAM = "/stream"
    STREAM_STREAM_NAME = "/stream/{stream_name}"
    FLOW = "/flow"
    FLOW_FLOW_NAME = "/flow/{flow_name}"
    FLOW_FLOW_NAME_EVENTS = "/flow/{flow_name}/events"
    FLOW_FLOW_NAME_SECRETS = "/flow/{flow_name}/secrets"
    FLOW_FLOW_NAME_SECRETS_SECRET_NAME = "/flow/{flow_name}/secrets/{secret_name}"
    OBJECT = "/object"
    OBJECT_BUCKET_NAME = "/object/{bucket_name}"
    OBJECT_BUCKET_NAME_LIST = "/object/{bucket_name}/list"
    OBJECT_BUCKET_NAME_STORE = "/object/{bucket_name}/store"
    ENDPOINTS_ENDPOINT_REQUEST = "/endpoints/{endpoint}/request"
    ENDPOINTS_ENDPOINT_RESPONSE_REQUEST_ID = (
        "/endpoints/{endpoint}/response/{request_id}"
    )
    KV = "/kv"
    KV_KV_STORE = "/kv/{kv_store}"
    KV_KV_STORE_KEY = "/kv/{kv_store}/key"
    KV_KV_STORE_KEY_KEY = "/kv/{kv_store}/key/{key}"
