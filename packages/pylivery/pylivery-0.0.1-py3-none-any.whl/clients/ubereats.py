from datetime import datetime, timedelta
from typing import Any, Dict, List, Tuple, Union

import requests

from .base import BaseAPIClient


class Versions:
    V1 = 'v1'
    V2 = 'v2'


class URL:
    BASE_FORMAT = "https://api.uber.com/{version}/"

    AUTH = "https://login.uber.com/oauth/{version}/token"
    DELIVERIES = "customers/{customer_id}/deliveries"
    QUOTE = "customers/{customer_id}/delivery_quotes"


class UberEatsClient(BaseAPIClient):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.client_id = ...
        self.client_secret = ...
        self.customer_id = ...
        self.base_url = URL.BASE_FORMAT.format(version=Versions.V1)

    def set_api_credentials(self, **kwargs: str) -> None:
        self.client_id = kwargs.pop('client_id')
        self.client_secret = kwargs.pop('client_secret')
        self.customer_id = kwargs.pop('customer_id')

    def set_login_payload(self) -> None:
        self.login_payload = (
            'client_id={client_id}&client_secret={client_secret}&grant_type=client_credentials&'
            'scope=eats.deliveries%20direct.organizations'.format(
                client_id=self.client_id, client_secret=self.client_secret
            )
        )

    def authorize(self) -> None:
        if not self.handle_authorization():
            return

        self.set_login_payload()
        hasattr(self, 'client_id') and self.client_id is not Ellipsis
        hasattr(self, 'client_secret') and self.client_secret is not Ellipsis
        hasattr(self, 'customer_id') and self.customer_id is not Ellipsis

        self.headers.update({'Content-Type': 'application/x-www-form-urlencoded'})

        response = requests.post(
            f"{URL.AUTH.format(version=Versions.V2)}",
            data=self.login_payload,
            headers=self.headers,
        )
        response.raise_for_status()

        self.access_token = response.json()['access_token']
        self.expires_in = response.json()['expires_in']
        self.expires_at = datetime.now() + timedelta(seconds=self.expires_in)
        self.headers.update({'Authorization': f'Bearer {self.access_token}'})
        # We do not need urlencoded anymore
        self.headers.update({'Content-Type': 'application/json'})

    def validate_address(
        self, data: dict
    ) -> Tuple[int, Union[List[Any], Dict[str, Any]]]:
        return self.perform_request(
            'POST', f'{URL.QUOTE.format(customer_id=self.customer_id)}', data=data
        )

    def create(self, data: dict) -> Tuple[int, Union[List[Any], Dict[str, Any]]]:
        return self.perform_request(
            'POST', f"{URL.DELIVERIES.format(customer_id=self.customer_id)}", data=data
        )

    def get(
        self, _id: Union[str, int]
    ) -> Tuple[int, Union[List[Any], Dict[str, Any]]]:
        return self.perform_request(
            'GET',
            f"{URL.DELIVERIES.format(customer_id=self.customer_id)}/{_id}",
            data={},
        )

    def get_order_status(
        self, _id: Union[str, int]
    ) -> Tuple[int, Union[List[Any], Dict[str, Any]]]:
        response = self.get(_id)
        return response[0], response[1]['status']

    def cancel(
        self, _id: Union[str, int]
    ) -> Tuple[int, Union[List[Any], Dict[str, Any]]]:
        # if not self.headers.get('Authorization'):
        #    self.authorize()
        # self.headers = {'Authorization': self.headers['Authorization']}
        return self.perform_request(
            'POST',
            f"{URL.DELIVERIES.format(customer_id=self.customer_id)}/{_id}/cancel",
            data="",
            # headers=self.headers,
        )

    def update(
        self, _id: Union[str, int], data: dict
    ) -> Tuple[int, Union[List[Any], Dict[str, Any]]]:
        pass

    def get_rider_data(
        self, _id: Union[str, int]
    ) -> Tuple[int, Union[List[Any], Dict[str, Any]]]:
        response = self.get(_id)
        return response[0], response[1]['courier']

    def get_rider_location(
        self, _id: Union[str, int]
    ) -> Tuple[int, Union[List[Any], Dict[str, Any]]]:
        response = self.get(_id)
        return response[0], response[1]['courier']['location']


uber_eats_client = UberEatsClient()
