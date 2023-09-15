import typing_extensions

from seaplane_framework.api.apis.tags import TagValues
from seaplane_framework.api.apis.tags.stream_api import StreamApi
from seaplane_framework.api.apis.tags.flow_api import FlowApi
from seaplane_framework.api.apis.tags.object_api import ObjectApi
from seaplane_framework.api.apis.tags.endpoint_api import EndpointApi
from seaplane_framework.api.apis.tags.key_value_api import KeyValueApi

TagToApi = typing_extensions.TypedDict(
    "TagToApi",
    {
        TagValues.STREAM: StreamApi,
        TagValues.FLOW: FlowApi,
        TagValues.OBJECT: ObjectApi,
        TagValues.ENDPOINT: EndpointApi,
        TagValues.KEYVALUE: KeyValueApi,
    },
)

tag_to_api = TagToApi(
    {
        TagValues.STREAM: StreamApi,
        TagValues.FLOW: FlowApi,
        TagValues.OBJECT: ObjectApi,
        TagValues.ENDPOINT: EndpointApi,
        TagValues.KEYVALUE: KeyValueApi,
    }
)
