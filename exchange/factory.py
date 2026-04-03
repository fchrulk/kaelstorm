"""Factory for creating exchange adapters based on config."""

from exchange.base import BaseExchange
from exchange.mockex import MockexAdapter


def create_exchange(exchange_type: str, **kwargs) -> BaseExchange:
    """Create an exchange adapter based on type string.

    Args:
        exchange_type: One of 'mockex', 'binance_testnet', 'binance'.
        **kwargs: Adapter-specific config (mockex_url, binance_api_key, etc.)
    """
    if exchange_type == "mockex":
        return MockexAdapter(base_url=kwargs.get("mockex_url", "http://localhost:3000"))
    elif exchange_type in ("binance", "binance_testnet"):
        raise NotImplementedError("Binance adapter not yet implemented (Phase 5)")
    else:
        raise ValueError(f"Unknown exchange: {exchange_type}")
