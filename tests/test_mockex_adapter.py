"""Tests for MockexAdapter REST methods."""

import pytest
import json
from unittest.mock import AsyncMock, patch, MagicMock

from exchange.mockex import MockexAdapter
from core.models import Order, Balance, Position, Trade


@pytest.fixture
def adapter():
    return MockexAdapter(base_url="http://localhost:3000")


def _mock_response(data, status=200):
    """Create a mock aiohttp response."""
    resp = AsyncMock()
    resp.status = status
    resp.json = AsyncMock(return_value=data)
    resp.text = AsyncMock(return_value=json.dumps(data))
    resp.__aenter__ = AsyncMock(return_value=resp)
    resp.__aexit__ = AsyncMock(return_value=False)
    return resp


def _mock_session(response):
    """Create a mock aiohttp ClientSession."""
    session = MagicMock()
    session.get = MagicMock(return_value=response)
    session.post = MagicMock(return_value=response)
    session.delete = MagicMock(return_value=response)
    session.__aenter__ = AsyncMock(return_value=session)
    session.__aexit__ = AsyncMock(return_value=False)
    return session


@pytest.mark.asyncio
async def test_get_balance(adapter):
    data = {"cash": "50000.00", "reserved": "5000.00", "equity": "100000.00", "position_value": "45000.00"}
    resp = _mock_response(data)
    session = _mock_session(resp)

    with patch("aiohttp.ClientSession", return_value=session):
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
    resp = _mock_response(data)
    session = _mock_session(resp)

    with patch("aiohttp.ClientSession", return_value=session):
        pos = await adapter.get_position()

    assert isinstance(pos, Position)
    assert pos.quantity == 0.01
    assert pos.entry_price == 95000.0


@pytest.mark.asyncio
async def test_get_position_none(adapter):
    resp = _mock_response({})
    session = _mock_session(resp)

    with patch("aiohttp.ClientSession", return_value=session):
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
    resp = _mock_response(data, status=201)
    session = _mock_session(resp)

    with patch("aiohttp.ClientSession", return_value=session):
        order = await adapter.place_order("buy", "market", 0.005)

    assert isinstance(order, Order)
    assert order.id == "abc-123"
    assert order.status == "filled"


@pytest.mark.asyncio
async def test_cancel_order(adapter):
    data = {
        "id": "abc-123", "symbol": "BTCUSDT", "side": "buy",
        "order_type": "limit", "quantity": "0.005", "status": "cancelled",
        "filled_qty": "0", "avg_fill_price": None, "fee": "0",
        "price": "94000.00", "stop_price": None,
        "created_at": "2026-04-03T00:00:00", "updated_at": "2026-04-03T00:00:01",
    }
    resp = _mock_response(data)
    session = _mock_session(resp)

    with patch("aiohttp.ClientSession", return_value=session):
        order = await adapter.cancel_order("abc-123")

    assert isinstance(order, Order)
    assert order.status == "cancelled"


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
    resp = _mock_response(data)
    session = _mock_session(resp)

    with patch("aiohttp.ClientSession", return_value=session):
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
    resp = _mock_response(data)
    session = _mock_session(resp)

    with patch("aiohttp.ClientSession", return_value=session):
        trades = await adapter.get_trades()

    assert len(trades) == 1
    assert isinstance(trades[0], Trade)
    assert trades[0].price == 95200.0
