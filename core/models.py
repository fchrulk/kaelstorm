"""Core data models for Kaelstorm."""

from dataclasses import dataclass, field


@dataclass
class Candle:
    """OHLCV candle."""
    timestamp: int  # milliseconds
    open: float
    high: float
    low: float
    close: float
    volume: float
    interval: str  # e.g., "1m", "5m", "15m"


@dataclass
class Signal:
    """Trading signal produced by a strategy."""
    direction: str  # "buy" | "sell" | "hold"
    strength: float  # 0.0 to 1.0
    reason: str
    strategy_name: str
    suggested_quantity: float | None = None
    stop_loss: float | None = None
    take_profit: float | None = None

    def __post_init__(self):
        if self.direction not in ("buy", "sell", "hold"):
            raise ValueError(f"direction must be 'buy', 'sell', or 'hold', got '{self.direction}'")
        if not 0.0 <= self.strength <= 1.0:
            raise ValueError(f"strength must be between 0.0 and 1.0, got {self.strength}")


@dataclass
class Order:
    """Order placed on an exchange."""
    id: str
    symbol: str
    side: str  # "buy" | "sell"
    order_type: str  # "market" | "limit" | "stop"
    quantity: float
    status: str  # "open" | "filled" | "cancelled" | "pending"
    price: float | None = None
    stop_price: float | None = None
    filled_qty: float = 0.0
    avg_fill_price: float | None = None
    fee: float = 0.0
    created_at: str | None = None
    updated_at: str | None = None


@dataclass
class Trade:
    """Executed trade (fill)."""
    id: str
    order_id: str
    symbol: str
    side: str
    quantity: float
    price: float
    fee: float
    realized_pnl: float = 0.0
    executed_at: str | None = None


@dataclass
class Position:
    """Open position."""
    symbol: str
    side: str  # "buy" (long)
    quantity: float
    entry_price: float

    def unrealized_pnl(self, current_price: float) -> float:
        """Calculate unrealized PnL at the given market price."""
        return (current_price - self.entry_price) * self.quantity


@dataclass
class Balance:
    """Account balance."""
    cash: float
    reserved: float
    position_value: float

    @property
    def equity(self) -> float:
        return self.cash + self.reserved + self.position_value
