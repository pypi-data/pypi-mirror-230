from unittest.mock import Mock

from clients.glovo import glovo_v2_client, URL


glovo_v2_client.set_api_credentials(client_id='client_id', client_secret='client_secret', stage='production')


def unset_credentials():
    glovo_v2_client.client_id, glovo_v2_client.client_secret, glovo_v2_client.stage, glovo_v2_client.base_url = ..., ..., ..., URL.BASE_FORMAT


def test_glovo_v2_client_stage_is_production_and_url_returns_api():
    prefix = URL.PREFIX[glovo_v2_client.stage]
    assert prefix == 'api'
    assert glovo_v2_client.base_url == URL.BASE_FORMAT.format(prefix=prefix)


def test_glovo_v2_client_stage_is_staging_and_url_returns_stageapi():
    unset_credentials()
    glovo_v2_client.set_api_credentials(client_id='client_id', client_secret='client_secret', stage='staging')
    prefix = URL.PREFIX[glovo_v2_client.stage]
    assert prefix == 'stageapi'
    assert glovo_v2_client.base_url == URL.BASE_FORMAT.format(prefix=prefix)
