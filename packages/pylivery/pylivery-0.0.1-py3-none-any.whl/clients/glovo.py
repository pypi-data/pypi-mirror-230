import http.client
import json
from datetime import datetime, timedelta
from typing import Any, Dict, List, Tuple, Union

from .base import BaseAPIClient


class Stage:
    PRODUCTION = "production"
    STAGING = "staging"


class Versions:
    V1 = 'v1'
    V2 = 'v2'


class URL:
    PREFIX = {
        Stage.PRODUCTION: "api",
        Stage.STAGING: "stageapi",
    }
    BASE_FORMAT = "https://{prefix}.glovoapp.com/"

    AUTH = 'oauth/token'
    PARCEL = "laas/parcels/"


class GlovoV2Client(BaseAPIClient):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.client_id = ...
        self.client_secret = ...
        self.stage = ...
        self.base_url = URL.BASE_FORMAT

    def set_api_credentials(self, **kwargs: str) -> None:
        self.client_id = kwargs.pop('client_id')
        self.client_secret = kwargs.pop('client_secret')
        self.stage = kwargs.pop('stage')
        self.base_url = self.base_url.format(prefix=URL.PREFIX[self.stage])

    def set_login_payload(self) -> None:
        self.login_payload = json.dumps(
            {
                "clientId": str(self.client_id),
                "clientSecret": str(self.client_secret),
                "grantType": "client_credentials",
            }
        )

    def authorize(self) -> None:
        if not self.handle_authorization():
            return

        self.set_login_payload()
        hasattr(self, 'client_id') and self.client_id is not Ellipsis
        hasattr(self, 'client_secret') and self.client_secret is not Ellipsis
        hasattr(self, 'stage') and self.stage is not Ellipsis

        conn = http.client.HTTPSConnection(f"{self.base_url.split('//')[1][:-1]}")
        conn.request("POST", f"{URL.AUTH}", self.login_payload, self.headers)

        raw_response = conn.getresponse()

        response = json.loads(raw_response.read().decode('utf-8'))

        self.raise_for_status(response, f"{self.base_url}{URL.AUTH}")

        self.access_token = response["accessToken"]
        self.expires_in = response["expiresIn"]
        self.expires_at = datetime.now() + timedelta(seconds=self.expires_in)
        self.headers.update({'Authorization': f'Bearer {self.access_token}'})

    def validate_address(
        self, data: dict
    ) -> Tuple[int, Union[List[Any], Dict[str, Any]]]:
        return self.perform_request('POST', f"{URL.PARCEL}validation", data=data)

    def create(self, data: dict) -> Tuple[int, Union[List[Any], Dict[str, Any]]]:
        return self.perform_request('POST', URL.PARCEL, data=data)

    def get(
        self, _id: Union[str, int]
    ) -> Tuple[int, Union[List[Any], Dict[str, Any]]]:
        return self.perform_request('GET', f"{URL.PARCEL}{_id}", data={})

    def get_order_status(
        self, _id: Union[str, int]
    ) -> Tuple[int, Union[List[Any], Dict[str, Any]]]:
        return self.perform_request(
            'GET', f"/{Versions.V2}/{URL.PARCEL}{_id}/status", data={}
        )

    def cancel(
        self, _id: Union[str, int]
    ) -> Tuple[int, Union[List[Any], Dict[str, Any]]]:
        return self.perform_request('PUT', f"{URL.PARCEL}{_id}/cancel", data={})

    def update(
        self, _id: Union[str, int], data: dict
    ) -> Tuple[int, Union[List[Any], Dict[str, Any]]]:
        pass

    def get_rider_data(
        self, _id: Union[str, int]
    ) -> Tuple[int, Union[List[Any], Dict[str, Any]]]:
        return self.perform_request(
            'GET', f"{URL.PARCEL}{_id}/courier-contact", data={}
        )

    def get_rider_location(
        self, _id: Union[str, int]
    ) -> Tuple[int, Union[List[Any], Dict[str, Any]]]:
        return self.perform_request(
            'GET', f"{URL.PARCEL}{_id}/courier-position", data={}
        )


glovo_v2_client = GlovoV2Client()
