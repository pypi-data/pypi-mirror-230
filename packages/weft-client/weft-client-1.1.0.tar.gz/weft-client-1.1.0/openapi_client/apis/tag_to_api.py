import typing_extensions

from openapi_client.apis.tags import TagValues
from openapi_client.apis.tags.auth_api import AuthApi
from openapi_client.apis.tags.events_api import EventsApi

TagToApi = typing_extensions.TypedDict(
    'TagToApi',
    {
        TagValues.AUTH: AuthApi,
        TagValues.EVENTS: EventsApi,
    }
)

tag_to_api = TagToApi(
    {
        TagValues.AUTH: AuthApi,
        TagValues.EVENTS: EventsApi,
    }
)
