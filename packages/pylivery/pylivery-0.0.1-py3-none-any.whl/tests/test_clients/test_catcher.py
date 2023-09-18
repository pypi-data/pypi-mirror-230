import datetime
from unittest.mock import Mock

from clients.catcher import catcher_client

catcher_client.set_api_credentials(api_key='api_key', api_secret='api_secret')


def test_authorization_sets_tokens(mocker):
    response = Mock()
    response.status_code = 200
    response.json.return_value = {
        "data": {
            "token": "<SOME_TOKEN>"
        }
    }

    mocker.patch('clients.base.BaseAPIClient.raise_for_status', return_value=None)
    mock_response = mocker.patch('requests.request', return_value=response)

    catcher_client.authorize()

    mock_response.assert_called_once()

    assert 'Authorization' in catcher_client.headers
    assert catcher_client.access_token is not None


def test_access_token_is_refreshed(mocker):
    assert catcher_client.expires_at is not Ellipsis
    catcher_client.expires_at = datetime.datetime.now() - datetime.timedelta(seconds=3600)
    assert catcher_client.handle_authorization() is True

    response = Mock()
    response.status_code = 200
    response.json.return_value = {
        "data": {
            "token": "<SOME_OTHER_TOKEN>"
        }
    }

    mocker.patch('clients.base.BaseAPIClient.raise_for_status', return_value=None)
    mock_response = mocker.patch('requests.request', return_value=response)

    catcher_client.authorize()

    mock_response.assert_called_once()

    assert catcher_client.access_token == '<SOME_OTHER_TOKEN>'
