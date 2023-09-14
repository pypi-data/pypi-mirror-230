from typing import List, Optional
from openapi_client.configuration import Configuration
from openapi_client.api_client import ApiClient
from openapi_client.models import EventInput
from openapi_client.apis.tags import events_api
from openapi_client.model.refresh_token_input import RefreshTokenInput

class WeftClient:
    def __init__(self, host: str):
        self.api = self.__build_api(host)

    def __build_api(self, host: str):
        configuration = Configuration(host=host)
        client = ApiClient(configuration)
        
        return events_api.EventsApi(client)


    def login(self, access_key_id: str):
        """
        Get new access token from refresh token (access token expires after 1 hour)

        Args:
            refresh_token (str): refresh token
        
        Returns:
        str: access token
        """
        

        refresh_token_input =  RefreshTokenInput(refreshToken=access_key_id)

        refresh_response = self.api.refresh_user(body=refresh_token_input)

        access_token = refresh_response.body.get('token')

        self.api.api_client.configuration.access_token = access_token
    
    def send_events(self, events: List[EventInput]):
        """
        Send events to Weft

        Args:
            events ([EventInput]): events to send
        """        

        return self.api.send_events(body=events)
