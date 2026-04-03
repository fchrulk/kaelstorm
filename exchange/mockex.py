"""Mockex exchange adapter — connects to mockex via REST + WebSocket."""

import asyncio
import json
import logging
from typing import Callable

import aiohttp
import websockets

from exchange.base import BaseExchange
from core.models import Balance, Order, Position, Trade

log = logging.getLogger("kaelstorm.exchange.mockex")


class MockexAdapter(BaseExchange):
    """Exchange adapter for mockex paper trading server."""

    def __init__(self, base_url: str = "http://localhost:3000"):
        super().__init__()
        self._base_url = base_url.rstrip("/")
        self._ws = None
        self._ws_task = None

    async def connect(self) -> None:
        log.info("Connecting to mockex at %s", self._base_url)

    async def disconnect(self) -> None:
        if self._ws_task:
            self._ws_task.cancel()
            try:
                await self._ws_task
            except asyncio.CancelledError:
                pass
            self._ws_task = None
        if self._ws:
            await self._ws.close()
            self._ws = None
        log.info("Disconnected from mockex")

    async def place_order(
        self, side: str, order_type: str, quantity: float,
        price: float | None = None, stop_price: float | None = None,
    ) -> Order:
        body = {"side": side, "order_type": order_type, "quantity": quantity}
        if price is not None:
            body["price"] = price
        if stop_price is not None:
            body["stop_price"] = stop_price

        async with aiohttp.ClientSession() as session:
            async with session.post(f"{self._base_url}/api/orders", json=body) as resp:
                data = await resp.json()
                if resp.status >= 400:
                    raise ValueError(data.get("error", "Order failed"))
                return self._parse_order(data)

    async def cancel_order(self, order_id: str) -> Order:
        async with aiohttp.ClientSession() as session:
            async with session.delete(f"{self._base_url}/api/orders/{order_id}") as resp:
                data = await resp.json()
                if resp.status >= 400:
                    raise ValueError(data.get("error", "Cancel failed"))
                return self._parse_order(data)

    async def get_balance(self) -> Balance:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{self._base_url}/api/account") as resp:
                data = await resp.json()
                return Balance(
                    cash=float(data.get("cash", 0)),
                    reserved=float(data.get("reserved", 0)),
                    position_value=float(data.get("position_value", 0)),
                )

    async def get_position(self) -> Position | None:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{self._base_url}/api/positions") as resp:
                data = await resp.json()
                if not data or not data.get("symbol"):
                    return None
                return Position(
                    symbol=data["symbol"],
                    side=data["side"],
                    quantity=float(data["quantity"]),
                    entry_price=float(data["entry_price"]),
                )

    async def get_open_orders(self) -> list[Order]:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{self._base_url}/api/orders", params={"status": "open"}) as resp:
                data = await resp.json()
                return [self._parse_order(o) for o in data]

    async def get_trades(self) -> list[Trade]:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{self._base_url}/api/trades") as resp:
                data = await resp.json()
                return [self._parse_trade(t) for t in data]

    async def subscribe_market_data(self, callback: Callable) -> None:
        """Connect to mockex WebSocket and stream market data + trading events."""
        ws_url = self._base_url.replace("http://", "ws://").replace("https://", "wss://") + "/ws"
        while True:
            try:
                log.info("Connecting to mockex WebSocket at %s", ws_url)
                async with websockets.connect(ws_url) as ws:
                    self._ws = ws
                    log.info("Connected to mockex WebSocket")
                    async for raw in ws:
                        try:
                            msg = json.loads(raw)
                        except json.JSONDecodeError:
                            continue

                        if "stream" in msg:
                            await callback(msg)
                        elif "type" in msg:
                            self._handle_trading_message(msg)
            except asyncio.CancelledError:
                raise
            except Exception as e:
                log.warning("Mockex WS error: %s — reconnecting in 3s", e)
            await asyncio.sleep(3)

    def _handle_trading_message(self, msg: dict) -> None:
        """Route trading messages to registered callbacks."""
        msg_type = msg.get("type")
        data = msg.get("data", {})

        if msg_type == "order_update" and self.on_order_update:
            self.on_order_update(self._parse_order(data))
        elif msg_type == "trade_executed" and self.on_trade_executed:
            self.on_trade_executed(self._parse_trade(data))
        elif msg_type == "balance_update" and self.on_balance_update:
            self.on_balance_update(Balance(
                cash=float(data.get("cash", 0)),
                reserved=float(data.get("reserved", 0)),
                position_value=float(data.get("position_value", 0)),
            ))

    @staticmethod
    def _parse_order(data: dict) -> Order:
        return Order(
            id=data["id"],
            symbol=data.get("symbol", "BTCUSDT"),
            side=data["side"],
            order_type=data["order_type"],
            quantity=float(data["quantity"]),
            status=data["status"],
            price=float(data["price"]) if data.get("price") else None,
            stop_price=float(data["stop_price"]) if data.get("stop_price") else None,
            filled_qty=float(data.get("filled_qty", 0)),
            avg_fill_price=float(data["avg_fill_price"]) if data.get("avg_fill_price") else None,
            fee=float(data.get("fee", 0)),
            created_at=data.get("created_at"),
            updated_at=data.get("updated_at"),
        )

    @staticmethod
    def _parse_trade(data: dict) -> Trade:
        return Trade(
            id=data["id"],
            order_id=data.get("order_id", ""),
            symbol=data.get("symbol", "BTCUSDT"),
            side=data["side"],
            quantity=float(data["quantity"]),
            price=float(data["price"]),
            fee=float(data.get("fee", 0)),
            realized_pnl=float(data.get("realized_pnl", 0)),
            executed_at=data.get("executed_at"),
        )
