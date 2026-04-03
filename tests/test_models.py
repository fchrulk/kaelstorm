"""Tests for core data models."""

import pytest
from core.models import Candle, Signal, Order, Trade, Position, Balance


def test_candle_creation():
    c = Candle(
        timestamp=1700000000000,
        open=95000.0, high=95500.0, low=94800.0, close=95200.0,
        volume=12.5, interval="5m",
    )
    assert c.timestamp == 1700000000000
    assert c.close == 95200.0
    assert c.interval == "5m"


def test_signal_creation():
    s = Signal(
        direction="buy", strength=0.75,
        reason="EMA9 crossed above EMA21",
        strategy_name="ema_crossover",
    )
    assert s.direction == "buy"
    assert s.strength == 0.75
    assert s.stop_loss is None
    assert s.take_profit is None


def test_signal_validation_invalid_direction():
    with pytest.raises(ValueError, match="direction must be"):
        Signal(
            direction="long", strength=0.5,
            reason="test", strategy_name="test",
        )


def test_signal_validation_strength_range():
    with pytest.raises(ValueError, match="strength must be"):
        Signal(
            direction="buy", strength=1.5,
            reason="test", strategy_name="test",
        )


def test_order_creation():
    o = Order(
        id="abc-123", symbol="BTCUSDT", side="buy",
        order_type="market", quantity=0.005,
        status="open",
    )
    assert o.id == "abc-123"
    assert o.price is None
    assert o.filled_qty == 0.0


def test_trade_creation():
    t = Trade(
        id="t-1", order_id="abc-123", symbol="BTCUSDT",
        side="buy", quantity=0.005, price=95200.0, fee=4.76,
    )
    assert t.fee == 4.76
    assert t.realized_pnl == 0.0


def test_position_unrealized_pnl():
    p = Position(
        symbol="BTCUSDT", side="buy",
        quantity=0.01, entry_price=95000.0,
    )
    assert p.unrealized_pnl(95500.0) == pytest.approx(5.0)
    assert p.unrealized_pnl(94500.0) == pytest.approx(-5.0)


def test_balance_equity():
    b = Balance(cash=50000.0, reserved=5000.0, position_value=45000.0)
    assert b.equity == pytest.approx(100000.0)
