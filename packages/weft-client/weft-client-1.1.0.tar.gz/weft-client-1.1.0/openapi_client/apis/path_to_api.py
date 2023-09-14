import typing_extensions

from openapi_client.paths import PathValues
from openapi_client.apis.paths.refresh_token import RefreshToken
from openapi_client.apis.paths.events import Events

PathToApi = typing_extensions.TypedDict(
    'PathToApi',
    {
        PathValues.REFRESH_TOKEN: RefreshToken,
        PathValues.EVENTS: Events,
    }
)

path_to_api = PathToApi(
    {
        PathValues.REFRESH_TOKEN: RefreshToken,
        PathValues.EVENTS: Events,
    }
)
