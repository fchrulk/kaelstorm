# CLAUDE.md — Kaelstorm

## What is this?

Kaelstorm is an autonomous AI trading agent for BTC/USDT. It connects to mockex for paper trading simulation, then swaps to Binance's real API for live trading. Uses a hybrid approach: rule-based strategies generate signals, a risk manager enforces limits, and Claude AI reviews every trade before execution.

## Architecture

```
Market Data (WebSocket)
    ↓
Candle Aggregator (1s → 5m, 15m, etc.)
    ↓
Strategy Engine (pluggable strategies)
    ↓ Signal
Risk Manager (position size, daily loss, drawdown, cooldown)
    ↓ Approved Signal
Claude AI Reviewer (mandatory — approve/reject/modify)
    ↓ AI-Approved Signal
Autonomy Gate (semi: Telegram approval, full: auto-execute)
    ↓
Exchange Adapter (mockex | binance_testnet | binance)
    ↓
Order Execution + Stop-Loss Placement
    ↓
Telegram Notification
```

## 3-Stage Progression

1. **mockex** — paper trading against live Binance data relayed through mockex
2. **Binance Testnet** — real Binance API with fake money
3. **Binance Production** — real money, same code, different URL and API keys

Switch via: `EXCHANGE=mockex|binance_testnet|binance`

## Files

| File/Dir | Purpose |
|---|---|
| `main.py` | Entry point — async agent startup, signal handling, graceful shutdown |
| `config.py` | Configuration from .env with defaults |
| `core/models.py` | Data classes: Candle, Signal, Order, Trade, Position, Balance |
| `core/events.py` | Internal event bus (pub/sub) |
| `exchange/base.py` | Abstract BaseExchange interface |
| `exchange/mockex.py` | Mockex adapter (REST + WebSocket at localhost:3000) |
| `exchange/factory.py` | Exchange adapter factory (mockex/binance/binance_testnet) |
| `strategy/` | Pluggable strategies (not yet implemented) |
| `risk/` | Risk manager (not yet implemented) |
| `brain/` | Claude AI signal reviewer (not yet implemented) |
| `notify/` | Telegram bot integration (not yet implemented) |
| `utils/` | Shared utilities, indicator calculations |
| `tests/` | Test suite (pytest + pytest-asyncio) |

## Running

```bash
cd /Users/fchrulk/Playground/kaelstorm
python main.py
```

Requires mockex running at `http://localhost:3000` (default).

## Dependencies

See `requirements.txt`:
- `aiohttp` — HTTP client for REST API calls
- `websockets` — WebSocket connections
- `anthropic` — Claude API client
- `python-telegram-bot` — Telegram bot
- `python-dotenv` — .env file loading
- `pytest`, `pytest-asyncio` — testing

## Testing

```bash
python -m pytest tests/ -v
```

All tests use mocks — no running mockex needed.

## Key Behaviors

- Exchange adapters implement `BaseExchange` abstract interface
- MockexAdapter maps directly to mockex's REST + WebSocket API
- Event bus for decoupled internal communication
- Signal model validates direction (buy/sell/hold) and strength (0.0-1.0)
- Position model calculates unrealized PnL from current price
- Main loop uses asyncio with SIGINT/SIGTERM graceful shutdown

## Design Specs & Plans

See `docs/specs/` for design specs.
See `docs/plans/` for implementation plans.

### Implementation Status

- [x] Phase 1: Foundation (scaffold, models, event bus, exchange interface, mockex adapter)
- [ ] Phase 2: Strategy Framework (candle aggregation, base strategy, EMA crossover, indicators)
- [ ] Phase 3: Risk Manager + Claude Reviewer
- [ ] Phase 4: Telegram Integration + Agent Loop
- [ ] Phase 5: Binance Adapter
