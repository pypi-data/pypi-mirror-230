from enums import ClientsEnum
from clients.glovo import glovo_v2_client
from clients.ubereats import uber_eats_client
from clients.catcher import catcher_client
from functions import get_delivery_client


def test_get_delivery_client_returns_glovo():
    assert get_delivery_client(ClientsEnum.GLOVO.value) == glovo_v2_client


def test_get_delivery_client_returns_catcher():
    assert get_delivery_client(ClientsEnum.CATCHER.value) == catcher_client


def test_get_delivery_client_returns_uber():
    assert get_delivery_client(ClientsEnum.UBER.value) == uber_eats_client
