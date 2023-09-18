import json
from datetime import datetime, timedelta
from typing import Any, Dict, List, Tuple, Union

import requests

from .base import BaseAPIClient


class Versions:
    V1 = 'v1'
    V2 = 'v2'


class URL:
    BASE_FORMAT = "https://api.catcher.es/"

    AUTH = "auth/{version}/authorize"
    PITCHER = "pitcher/{version}/order"


class CatcherClient(BaseAPIClient):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.api_key = ...
        self.api_secret = ...
        self.base_url = URL.BASE_FORMAT

    def set_api_credentials(self, **kwargs: str) -> None:
        self.api_key = kwargs.pop('api_key')
        self.api_secret = kwargs.pop('api_secret')

    def set_login_payload(self) -> None:
        self.login_payload = json.dumps(
            {
                "appId": str(self.api_key),
                "appSecret": str(self.api_secret),
                "grant_type": "client_secret",
            }
        )

    def authorize(self) -> None:
        if not self.handle_authorization():
            return

        self.set_login_payload()
        hasattr(self, 'api_key') and self.api_key is not Ellipsis
        hasattr(self, 'api_secret') and self.api_secret is not Ellipsis

        response = requests.request(
            'POST',
            f"{self.base_url}{URL.AUTH.format(version=Versions.V1)}",
            data=self.login_payload,
            headers=self.headers,
        )

        self.raise_for_status(response.json(), f"{self.base_url}{URL.AUTH.format(version=Versions.V1)}")

        self.access_token = response.json()['data']['token']
        self.expires_at = datetime.now() + timedelta(seconds=self.expires_in)
        self.headers.update({'Authorization': f'Bearer {self.access_token}'})

    def validate_address(
        self, data: dict
    ) -> Tuple[int, Union[List[Any], Dict[str, Any]]]:
        pass

    def create(self, data: dict) -> Tuple[int, Union[List[Any], Dict[str, Any]]]:
        return self.perform_request(
            'POST', f"{URL.PITCHER.format(version=Versions.V1)}", data=data
        )

    def get(
        self, _id: Union[str, int]
    ) -> Tuple[int, Union[List[Any], Dict[str, Any]]]:
        return self.perform_request(
            'GET', f"{URL.PITCHER.format(version=Versions.V1)}/{_id}", data={}
        )

    def get_order_status(
        self, _id: Union[str, int]
    ) -> Tuple[int, Union[List[Any], Dict[str, Any]]]:
        return self.perform_request(
            'GET', f"{URL.PITCHER.format(version=Versions.V1)}/status/{_id}", data={}
        )

    def cancel(
        self, _id: Union[str, int]
    ) -> Tuple[int, Union[List[Any], Dict[str, Any]]]:
        return self.perform_request(
            'PUT', f"{URL.PITCHER.format(version=Versions.V1)}/cancel/{_id}", data={}
        )

    def update(
        self, _id: Union[str, int], data: dict
    ) -> Tuple[int, Union[List[Any], Dict[str, Any]]]:
        pass

    def get_rider_data(
        self, _id: Union[str, int]
    ) -> Tuple[int, Union[List[Any], Dict[str, Any]]]:
        pass

    def get_rider_location(
        self, _id: Union[str, int]
    ) -> Tuple[int, Union[List[Any], Dict[str, Any]]]:
        return self.perform_request(
            'GET',
            f"{URL.PITCHER.format(version=Versions.V1)}/riderlocation/{_id}",
            data={},
        )


catcher_client = CatcherClient()
