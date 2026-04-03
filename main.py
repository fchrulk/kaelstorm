#!/usr/bin/env python3
"""Kaelstorm — AI trading agent for BTC/USDT."""

import asyncio
import logging
import signal

import config
from exchange.factory import create_exchange

logging.basicConfig(
    level=getattr(logging, config.LOG_LEVEL, logging.INFO),
    format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
)
log = logging.getLogger("kaelstorm")


async def run():
    """Main async entry point."""
    log.info("Kaelstorm starting (exchange=%s)", config.EXCHANGE)

    # Create exchange adapter
    exchange = create_exchange(
        config.EXCHANGE,
        mockex_url=config.MOCKEX_URL,
        binance_api_key=config.BINANCE_API_KEY,
        binance_api_secret=config.BINANCE_API_SECRET,
    )

    # Connect to exchange
    await exchange.connect()
    log.info("Connected to %s", config.EXCHANGE)

    # Fetch initial state
    balance = await exchange.get_balance()
    log.info("Account balance: cash=%.2f, equity=%.2f", balance.cash, balance.equity)

    position = await exchange.get_position()
    if position:
        log.info("Open position: %s %s %.8f @ %.2f",
                 position.side, position.symbol, position.quantity, position.entry_price)
    else:
        log.info("No open position")

    log.info("Kaelstorm ready — strategy engine not yet implemented (Phase 2)")

    # Keep running until interrupted
    stop_event = asyncio.Event()
    loop = asyncio.get_event_loop()
    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, stop_event.set)

    await stop_event.wait()
    log.info("Shutting down...")
    await exchange.disconnect()
    log.info("Kaelstorm stopped")


def main():
    asyncio.run(run())


if __name__ == "__main__":
    main()
