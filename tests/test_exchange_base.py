"""Tests for base exchange interface."""

import pytest
from exchange.base import BaseExchange


def test_cannot_instantiate_base_exchange():
    """BaseExchange is abstract — cannot be instantiated directly."""
    with pytest.raises(TypeError):
        BaseExchange()


def test_subclass_must_implement_all_methods():
    """A subclass that doesn't implement all methods cannot be instantiated."""
    class IncompleteExchange(BaseExchange):
        async def connect(self): ...

    with pytest.raises(TypeError):
        IncompleteExchange()


def test_subclass_with_all_methods_can_instantiate():
    """A subclass implementing all methods can be instantiated."""
    class FakeExchange(BaseExchange):
        async def connect(self): pass
        async def disconnect(self): pass
        async def place_order(self, side, order_type, quantity, price=None, stop_price=None): pass
        async def cancel_order(self, order_id): pass
        async def get_balance(self): pass
        async def get_position(self): pass
        async def get_open_orders(self): pass
        async def get_trades(self): pass
        async def subscribe_market_data(self, callback): pass

    ex = FakeExchange()
    assert ex is not None
