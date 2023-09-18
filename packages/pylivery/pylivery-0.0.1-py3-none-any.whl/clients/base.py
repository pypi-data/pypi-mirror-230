import abc
from datetime import datetime, timedelta
from typing import Any, Dict, List, Tuple, Union

import requests
from requests import HTTPError


class APIInterface(metaclass=abc.ABCMeta):
    @classmethod
    def __subclasshook__(cls, subclass):
        return (
            hasattr(subclass, 'set_api_credentials')
            and callable(subclass.set_api_credentials)
            and hasattr(subclass, 'set_login_payload')
            and callable(subclass.set_login_payload)
            and hasattr(subclass, 'authorize')
            and callable(subclass.authorize)
            and hasattr(subclass, 'validate_address')
            and callable(subclass.validate_address)
            and hasattr(subclass, 'create')
            and callable(subclass.create)
            and hasattr(subclass, 'get')
            and callable(subclass.get)
            and hasattr(subclass, 'get_order_status')
            and callable(subclass.get_order_status)
            and hasattr(subclass, 'cancel')
            and callable(subclass.cancel)
            and hasattr(subclass, 'update')
            and callable(subclass.update)
            and hasattr(subclass, 'get_rider_data')
            and callable(subclass.get_rider_data)
            and hasattr(subclass, 'get_rider_location')
            and callable(subclass.get_rider_location)
            or NotImplemented
        )

    @abc.abstractmethod
    def set_api_credentials(self, **kwargs: str) -> None:
        """Handles setting the required keys for each API"""
        raise NotImplementedError

    @abc.abstractmethod
    def set_login_payload(self) -> None:
        """Handles creating a JSON to send as payload to the auth endpoint"""
        raise NotImplementedError

    @abc.abstractmethod
    def authorize(self) -> None:
        """Handles authorization and token management"""
        raise NotImplementedError

    @abc.abstractmethod
    def validate_address(
        self, data: dict
    ) -> Tuple[int, Union[List[Any], Dict[str, Any]]]:
        """Checks if the company makes deliveries in that working area"""
        raise NotImplementedError

    @abc.abstractmethod
    def create(self, data: dict) -> Tuple[int, Union[List[Any], Dict[str, Any]]]:
        """Creates an order"""
        raise NotImplementedError

    @abc.abstractmethod
    def get(
        self, _id: Union[str, int]
    ) -> Tuple[int, Union[List[Any], Dict[str, Any]]]:
        """Gets an order"""
        raise NotImplementedError

    @abc.abstractmethod
    def get_order_status(
        self, _id: Union[str, int]
    ) -> Tuple[int, Union[List[Any], Dict[str, Any]]]:
        """Gets order's status"""
        raise NotImplementedError

    @abc.abstractmethod
    def cancel(
        self, _id: Union[str, int]
    ) -> Tuple[int, Union[List[Any], Dict[str, Any]]]:
        """Cancels an order"""
        raise NotImplementedError

    @abc.abstractmethod
    def update(
        self, _id: Union[str, int], data: dict
    ) -> Tuple[int, Union[List[Any], Dict[str, Any]]]:
        """Updates an order"""
        raise NotImplementedError

    @abc.abstractmethod
    def get_rider_data(
        self, _id: Union[str, int]
    ) -> Tuple[int, Union[List[Any], Dict[str, Any]]]:
        """Gets the rider's information"""
        raise NotImplementedError

    @abc.abstractmethod
    def get_rider_location(
        self, _id: Union[str, int]
    ) -> Tuple[int, Union[List[Any], Dict[str, Any]]]:
        """Gets the rider's location (coordinates)"""
        raise NotImplementedError


class BaseAPIClient(APIInterface):
    def __init__(self, *args, **kwargs: str) -> None:
        self.base_url = ...
        self.access_token = ...
        self.expires_in = 3600  # 1 hour
        self.expires_at = ...
        self.headers = {'Content-type': 'application/json'}
        self.login_payload = ...

    @property
    def base_url(self) -> str:
        return self._base_url

    @base_url.setter
    def base_url(self, value: str) -> None:
        self._base_url = value

    @property
    def access_token(self) -> Dict[str, Any]:
        return self._access_token

    @access_token.setter
    def access_token(self, value: Dict[str, Any]) -> None:
        self._access_token = value

    @property
    def expires_in(self) -> int:
        return self._expires_in

    @expires_in.setter
    def expires_in(self, value: int) -> None:
        self._expires_in = value

    @property
    def expires_at(self) -> datetime:
        return self._expires_at

    @expires_at.setter
    def expires_at(self, value: datetime) -> None:
        self._expires_at = value

    def raise_for_status(self, data: dict, url: str) -> None:
        """Custom exception raiser that throws 'Unauthorized' when the authorization response returns an error with
         status_code 20X (Catcher) or when 'requests' is not used to perform the authorization request (Glovo)"""
        response_has_token = data.get('accessToken') or data.get('data').get('token')  # 'Glovo' or 'Catcher'

        if not response_has_token:
            http_error_msg = (
                f"401 Client Error: 'Unauthorized' for url: {url}"
            )
            raise HTTPError(http_error_msg, response=self)

    def handle_authorization(self) -> bool:
        """Handles authorization headers
        :returns: True if token must be refreshed else False
        """
        ask_for_token = True
        if 'Authorization' in self.headers:
            if hasattr(self, 'expires_at'):
                if self.expires_at <= datetime.now() + timedelta(seconds=120):
                    del self.headers['Authorization']
                else:
                    ask_for_token = False

        return ask_for_token

    def perform_request(
        self,
        http_verb: str,
        endpoint: str,
        *,
        data: Union[str, Dict[str, Any]] = ...,
        params: Dict[str, str] = ...,
        headers: Dict[str, Any] = ...,
    ) -> Tuple[int, Dict[str, Any]]:
        if data is None or data is Ellipsis:
            data = {}
        if params is None or params is Ellipsis:
            params = {}
        if headers is None or headers is Ellipsis:
            headers = self.headers

        self.authorize()
        try:
            url = f"{self.base_url}{endpoint}"
            response = requests.request(
                http_verb, url, data=data, params=params, headers=headers
            )
            response.raise_for_status()
        except requests.RequestException:
            raise
        except requests.ConnectTimeout:
            raise
        except Exception:
            raise

        return response.status_code, response.json()
