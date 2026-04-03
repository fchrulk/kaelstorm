"""Tests for MockexAdapter WebSocket methods."""

import pytest
import asyncio
import json
from unittest.mock import AsyncMock, patch, MagicMock

from exchange.mockex import MockexAdapter


class FakeWebSocket:
    """Fake WebSocket that yields messages then raises CancelledError."""

    def __init__(self, messages: list[str]):
        self._messages = list(messages)

    def __aiter__(self):
        return self

    async def __anext__(self):
        if self._messages:
            return self._messages.pop(0)
        raise StopAsyncIteration

    async def close(self):
        pass

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        return False


@pytest.mark.asyncio
async def test_subscribe_market_data_calls_callback():
    adapter = MockexAdapter(base_url="http://localhost:3000")
    received = []

    messages = [
        json.dumps({"stream": "btcusdt@trade", "data": {"p": "95200.00"}}),
        json.dumps({"stream": "btcusdt@kline_1s", "data": {"k": {"t": 1, "o": "95000", "h": "95500", "l": "94800", "c": "95200", "v": "1.5", "x": True}}}),
    ]

    fake_ws = FakeWebSocket(messages)

    async def callback(msg):
        received.append(msg)

    with patch("websockets.connect", return_value=fake_ws):
        task = asyncio.create_task(adapter.subscribe_market_data(callback))
        await asyncio.sleep(0.1)
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass

    assert len(received) == 2
    assert received[0]["stream"] == "btcusdt@trade"
    assert received[1]["stream"] == "btcusdt@kline_1s"


@pytest.mark.asyncio
async def test_ws_handles_trading_messages():
    adapter = MockexAdapter(base_url="http://localhost:3000")

    order_data = {
        "type": "order_update",
        "data": {"id": "o-1", "status": "filled", "symbol": "BTCUSDT",
                 "side": "buy", "order_type": "market", "quantity": "0.005",
                 "filled_qty": "0.005", "avg_fill_price": "95200.00", "fee": "4.76"},
    }

    orders_received = []
    adapter.on_order_update = lambda o: orders_received.append(o)

    fake_ws = FakeWebSocket([json.dumps(order_data)])

    with patch("websockets.connect", return_value=fake_ws):
        task = asyncio.create_task(adapter.subscribe_market_data(lambda msg: None))
        await asyncio.sleep(0.1)
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass

    assert len(orders_received) == 1
    assert orders_received[0].id == "o-1"
