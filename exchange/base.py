"""Abstract base class for exchange adapters."""

from abc import ABC, abstractmethod
from typing import Callable

from core.models import Balance, Order, Position, Trade


class BaseExchange(ABC):
    """Interface that all exchange adapters must implement."""

    def __init__(self):
        self.on_order_update: Callable[[Order], None] | None = None
        self.on_balance_update: Callable[[Balance], None] | None = None
        self.on_trade_executed: Callable[[Trade], None] | None = None

    @abstractmethod
    async def connect(self) -> None:
        """Establish connection to the exchange (WebSocket + REST)."""

    @abstractmethod
    async def disconnect(self) -> None:
        """Close all connections and clean up."""

    @abstractmethod
    async def place_order(
        self, side: str, order_type: str, quantity: float,
        price: float | None = None, stop_price: float | None = None,
    ) -> Order:
        """Place an order on the exchange."""

    @abstractmethod
    async def cancel_order(self, order_id: str) -> Order:
        """Cancel an open order."""

    @abstractmethod
    async def get_balance(self) -> Balance:
        """Get current account balance."""

    @abstractmethod
    async def get_position(self) -> Position | None:
        """Get current open position, or None if flat."""

    @abstractmethod
    async def get_open_orders(self) -> list[Order]:
        """Get all open orders."""

    @abstractmethod
    async def get_trades(self) -> list[Trade]:
        """Get recent trade history."""

    @abstractmethod
    async def subscribe_market_data(self, callback: Callable) -> None:
        """Subscribe to market data stream. Callback receives raw stream messages."""
