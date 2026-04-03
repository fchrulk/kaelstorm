"""Tests for MockexAdapter REST methods."""

import pytest
import json
from unittest.mock import AsyncMock, MagicMock

from exchange.mockex import MockexAdapter
from core.models import Order, Balance, Position, Trade


@pytest.fixture
def adapter():
    """Create adapter with a mocked session (simulates post-connect state)."""
    a = MockexAdapter(base_url="http://localhost:3000")
    a._session = MagicMock()  # simulate connected state
    return a


def _mock_response(data, status=200):
    """Create a mock aiohttp response."""
    resp = AsyncMock()
    resp.status = status
    resp.json = AsyncMock(return_value=data)
    resp.text = AsyncMock(return_value=json.dumps(data))
    resp.__aenter__ = AsyncMock(return_value=resp)
    resp.__aexit__ = AsyncMock(return_value=False)
    return resp


def _set_mock_session(adapter, response):
    """Configure the adapter's mock session to return the given response."""
    adapter._session.get = MagicMock(return_value=response)
    adapter._session.post = MagicMock(return_value=response)
    adapter._session.delete = MagicMock(return_value=response)


@pytest.mark.asyncio
async def test_get_balance(adapter):
    data = {"cash": "50000.00", "reserved": "5000.00", "equity": "100000.00", "position_value": "45000.00"}
    _set_mock_session(adapter, _mock_response(data))

    balance = await adapter.get_balance()

    assert isinstance(balance, Balance)
    assert balance.cash == 50000.0
    assert balance.reserved == 5000.0
    assert balance.position_value == 45000.0


@pytest.mark.asyncio
async def test_get_position_exists(adapter):
    data = {
        "symbol": "BTCUSDT", "side": "buy",
        "quantity": "0.01", "entry_price": "95000.00",
        "unrealized_pnl": "5.00", "current_price": "95500.00",
    }
    _set_mock_session(adapter, _mock_response(data))

    pos = await adapter.get_position()

    assert isinstance(pos, Position)
    assert pos.quantity == 0.01
    assert pos.entry_price == 95000.0


@pytest.mark.asyncio
async def test_get_position_none(adapter):
    _set_mock_session(adapter, _mock_response({}))

    pos = await adapter.get_position()

    assert pos is None


@pytest.mark.asyncio
async def test_place_order(adapter):
    data = {
        "id": "abc-123", "symbol": "BTCUSDT", "side": "buy",
        "order_type": "market", "quantity": "0.005", "status": "filled",
        "filled_qty": "0.005", "avg_fill_price": "95200.00", "fee": "4.76",
        "price": None, "stop_price": None,
        "created_at": "2026-04-03T00:00:00", "updated_at": "2026-04-03T00:00:00",
    }
    _set_mock_session(adapter, _mock_response(data, status=201))

    order = await adapter.place_order("buy", "market", 0.005)

    assert isinstance(order, Order)
    assert order.id == "abc-123"
    assert order.status == "filled"


@pytest.mark.asyncio
async def test_place_order_error(adapter):
    _set_mock_session(adapter, _mock_response({"error": "Insufficient balance"}, status=400))

    with pytest.raises(ValueError, match="Insufficient balance"):
        await adapter.place_order("buy", "market", 999)


@pytest.mark.asyncio
async def test_cancel_order(adapter):
    data = {
        "id": "abc-123", "symbol": "BTCUSDT", "side": "buy",
        "order_type": "limit", "quantity": "0.005", "status": "cancelled",
        "filled_qty": "0", "avg_fill_price": None, "fee": "0",
        "price": "94000.00", "stop_price": None,
        "created_at": "2026-04-03T00:00:00", "updated_at": "2026-04-03T00:00:01",
    }
    _set_mock_session(adapter, _mock_response(data))

    order = await adapter.cancel_order("abc-123")

    assert isinstance(order, Order)
    assert order.status == "cancelled"


@pytest.mark.asyncio
async def test_cancel_order_error(adapter):
    _set_mock_session(adapter, _mock_response({"error": "Order not found"}, status=404))

    with pytest.raises(ValueError, match="Order not found"):
        await adapter.cancel_order("nonexistent")


@pytest.mark.asyncio
async def test_get_open_orders(adapter):
    data = [
        {
            "id": "o-1", "symbol": "BTCUSDT", "side": "buy",
            "order_type": "limit", "quantity": "0.01", "status": "open",
            "filled_qty": "0", "avg_fill_price": None, "fee": "0",
            "price": "94000.00", "stop_price": None,
            "created_at": "2026-04-03T00:00:00", "updated_at": None,
        },
    ]
    _set_mock_session(adapter, _mock_response(data))

    orders = await adapter.get_open_orders()

    assert len(orders) == 1
    assert isinstance(orders[0], Order)
    assert orders[0].status == "open"


@pytest.mark.asyncio
async def test_get_trades(adapter):
    data = [
        {
            "id": "t-1", "order_id": "o-1", "symbol": "BTCUSDT",
            "side": "buy", "quantity": "0.005", "price": "95200.00",
            "fee": "4.76", "realized_pnl": "0", "executed_at": "2026-04-03T00:00:00",
        },
    ]
    _set_mock_session(adapter, _mock_response(data))

    trades = await adapter.get_trades()

    assert len(trades) == 1
    assert isinstance(trades[0], Trade)
    assert trades[0].price == 95200.0


@pytest.mark.asyncio
async def test_not_connected_raises():
    adapter = MockexAdapter(base_url="http://localhost:3000")
    # _session is None (not connected)
    with pytest.raises(RuntimeError, match="Not connected"):
        await adapter.get_balance()
