"""Tests for exchange factory."""

import pytest
from exchange.factory import create_exchange
from exchange.mockex import MockexAdapter


def test_create_mockex_exchange():
    ex = create_exchange("mockex", mockex_url="http://localhost:3000")
    assert isinstance(ex, MockexAdapter)


def test_create_unknown_exchange():
    with pytest.raises(ValueError, match="Unknown exchange"):
        create_exchange("unknown_exchange")


def test_create_binance_not_yet_implemented():
    with pytest.raises(NotImplementedError, match="Binance adapter"):
        create_exchange("binance", binance_api_key="key", binance_api_secret="secret")


def test_create_binance_testnet_not_yet_implemented():
    with pytest.raises(NotImplementedError, match="Binance adapter"):
        create_exchange("binance_testnet", binance_api_key="key", binance_api_secret="secret")
