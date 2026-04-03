"""Application configuration loaded from .env with defaults."""

import os
from pathlib import Path

from dotenv import load_dotenv

_env_path = Path(__file__).resolve().parent / ".env"
load_dotenv(_env_path)


def _get(key: str, default: str = "") -> str:
    return os.getenv(key, default)


def _int(key: str, default: int = 0) -> int:
    return int(_get(key, str(default)))


def _float(key: str, default: float = 0.0) -> float:
    return float(_get(key, str(default)))


def _bool(key: str, default: bool = False) -> bool:
    return _get(key, str(default)).lower() in ("true", "1", "yes")


# Exchange
EXCHANGE = _get("EXCHANGE", "mockex")
MOCKEX_URL = _get("MOCKEX_URL", "http://localhost:3000")
BINANCE_API_KEY = _get("BINANCE_API_KEY")
BINANCE_API_SECRET = _get("BINANCE_API_SECRET")

# Strategy
STRATEGIES = [s.strip() for s in _get("STRATEGIES", "ema_crossover").split(",") if s.strip()]
SYMBOL = _get("SYMBOL", "BTCUSDT")

# Risk Management
MAX_POSITION_PCT = _float("MAX_POSITION_PCT", 10.0)
MAX_DAILY_LOSS_PCT = _float("MAX_DAILY_LOSS_PCT", 5.0)
MAX_DRAWDOWN_PCT = _float("MAX_DRAWDOWN_PCT", 15.0)
MAX_OPEN_TRADES = _int("MAX_OPEN_TRADES", 3)
TRADE_COOLDOWN_SECONDS = _int("TRADE_COOLDOWN_SECONDS", 300)
DEFAULT_STOP_LOSS_PCT = _float("DEFAULT_STOP_LOSS_PCT", 3.0)

# Claude AI
CLAUDE_API_KEY = _get("CLAUDE_API_KEY")
CLAUDE_MODEL = _get("CLAUDE_MODEL", "haiku")
CLAUDE_MIN_INTERVAL_SECONDS = _int("CLAUDE_MIN_INTERVAL_SECONDS", 120)
CLAUDE_FALLBACK = _get("CLAUDE_FALLBACK", "block")

# Telegram
TELEGRAM_BOT_TOKEN = _get("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = _get("TELEGRAM_CHAT_ID")

# Autonomy
AUTONOMY_MODE = _get("AUTONOMY_MODE", "semi")

# Agent
CANCEL_ON_SHUTDOWN = _bool("CANCEL_ON_SHUTDOWN", True)
LOG_LEVEL = _get("LOG_LEVEL", "INFO")
