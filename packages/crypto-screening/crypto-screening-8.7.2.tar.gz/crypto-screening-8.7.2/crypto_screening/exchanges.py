# exchanges.py

import json
from pathlib import Path

from cryptofeed.exchanges import EXCHANGE_MAP

from crypto_screening.utils.base import data

__all__ = [
    "EXCHANGES",
    "EXCHANGE_NAMES",
    "BUILTIN_EXCHANGE_NAMES",
    "BUILTIN_EXCHANGES",
    "BUILTIN_EXCHANGES_SYMBOLS"
]

EXCLUDED = [
    'exx', 'delta', 'settlement_period',
    'okcoin', 'kraken_futures', 'deribit'
]

with open(str(Path(data()) / Path("all_exchanges_symbols.json")), "r") as file:
    BUILTIN_EXCHANGES_SYMBOLS = {
        exchange: set(symbols)
        for exchange, symbols in json.load(file).items()
        if exchange.lower() not in EXCLUDED
    }
# end open

BUILTIN_EXCHANGE_NAMES = set(BUILTIN_EXCHANGES_SYMBOLS.keys())
BUILTIN_EXCHANGES = {
    name.lower(): EXCHANGE_MAP[name.upper()]
    for name in BUILTIN_EXCHANGE_NAMES
    if name in EXCHANGE_MAP
}
EXCHANGES = {
    name.lower(): exchange
    for name, exchange in EXCHANGE_MAP.items()
    if name.lower() not in EXCLUDED
}
EXCHANGE_NAMES = set(EXCHANGES.keys())