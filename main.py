#!/usr/bin/env python3
"""Kaelstorm — AI trading agent for BTC/USDT."""

import logging

import config

logging.basicConfig(
    level=getattr(logging, config.LOG_LEVEL, logging.INFO),
    format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
)
log = logging.getLogger("kaelstorm")


def main():
    log.info("Kaelstorm starting (exchange=%s)", config.EXCHANGE)
    log.info("Kaelstorm ready — agent loop not yet implemented")


if __name__ == "__main__":
    main()
