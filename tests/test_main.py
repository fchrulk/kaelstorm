"""Tests for main entry point."""

from unittest.mock import patch

from exchange.factory import create_exchange
from exchange.mockex import MockexAdapter


def test_create_exchange_from_config():
    """Verify that config creates the right exchange adapter."""
    with patch("config.EXCHANGE", "mockex"), \
         patch("config.MOCKEX_URL", "http://localhost:3000"):
        import config
        ex = create_exchange(config.EXCHANGE, mockex_url=config.MOCKEX_URL)
        assert isinstance(ex, MockexAdapter)
