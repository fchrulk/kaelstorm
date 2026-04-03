# Kaelstorm

Autonomous AI trading agent for BTC/USDT. Connects to [mockex](https://github.com/fchrulk/mockex) for paper trading, then swaps to Binance for live trading with real money.

## How it works

```
Market Data → Strategy Engine → Risk Manager → Claude AI Review → Execute
```

- **Pluggable strategies** — rule-based signals (V1: EMA crossover)
- **Risk manager** — position sizing, daily loss limits, drawdown protection, trade cooldown
- **Claude AI reviewer** — mandatory review of every trade before execution
- **Telegram bot** — notifications, commands, semi-autonomous approval flow
- **3-stage progression** — mockex (paper) → Binance testnet (fake money) → Binance production (real money)

## Quick start

```bash
# Clone
git clone git@github.com:fchrulk/kaelstorm.git
cd kaelstorm

# Configure
cp .env.example .env
# Edit .env with your settings

# Install dependencies
pip install -r requirements.txt

# Run (requires mockex at localhost:3000)
python main.py
```

## Configuration

Set `EXCHANGE` in `.env` to switch between modes:

| Mode | Value | Description |
|---|---|---|
| Paper trading | `mockex` | Connects to mockex at `MOCKEX_URL` |
| Testnet | `binance_testnet` | Binance testnet API (fake money) |
| Live | `binance` | Binance production API (real money) |

See `.env.example` for all configuration options.

## Testing

```bash
python -m pytest tests/ -v
```

## Project structure

```
kaelstorm/
├── main.py              # Entry point
├── config.py            # Configuration from .env
├── core/
│   ├── models.py        # Candle, Signal, Order, Trade, Position, Balance
│   └── events.py        # Internal pub/sub event bus
├── exchange/
│   ├── base.py          # Abstract exchange interface
│   ├── mockex.py        # Mockex adapter (REST + WebSocket)
│   └── factory.py       # Exchange adapter factory
├── strategy/            # Trading strategies (Phase 2)
├── risk/                # Risk manager (Phase 3)
├── brain/               # Claude AI reviewer (Phase 3)
├── notify/              # Telegram integration (Phase 4)
├── utils/               # Shared utilities
└── tests/               # Test suite
```

## Roadmap

- [x] **Phase 1** — Foundation: project scaffold, data models, exchange interface, mockex adapter
- [ ] **Phase 2** — Strategy Framework: candle aggregation, EMA crossover strategy, indicators
- [ ] **Phase 3** — Risk Manager + Claude AI Reviewer
- [ ] **Phase 4** — Telegram Integration + Agent Loop
- [ ] **Phase 5** — Binance Adapter (testnet + production)
