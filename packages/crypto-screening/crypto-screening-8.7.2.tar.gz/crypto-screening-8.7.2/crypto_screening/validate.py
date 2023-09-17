# validate.py

from typing import Optional, Iterable, Any

from crypto_screening.utils.process import string_in_values
from crypto_screening.symbols import adjust_symbol
from crypto_screening.interval import interval_to_total_time
from crypto_screening.exchanges import EXCHANGE_NAMES

__all__ = [
    "is_valid_symbol",
    "validate_exchange",
    "validate_symbol",
    "is_valid_exchange",
    "validate_interval",
    "is_valid_interval"
]

def is_valid_symbol(symbol: str, symbols: Iterable[str]) -> bool:
    """
    Returns a value for the symbol being valid for the source exchange.

    :param symbol: The symbol of the assets.
    :param symbols: The valid symbols.

    :return: The validation-value.
    """

    return (
        adjust_symbol(symbol=symbol) in
        [adjust_symbol(symbol=s) for s in symbols]
    )
# end is_valid_symbol

def validate_symbol(
        exchange: str,
        symbol: str,
        symbols: Iterable[str],
        exchanges: Optional[Iterable[str]] = None,
        provider: Optional[Any] = None
) -> str:
    """
    Returns a value for the symbol being valid for the source exchange.

    :param exchange: The name of the exchange platform.
    :param symbol: The symbol of the assets.
    :param symbols: The valid symbols.
    :param exchanges: The valid exchanges.
    :param provider: Any provider object.

    :return: The valid symbol.
    """

    validate_exchange(
        exchange=exchange, exchanges=exchanges, provider=provider
    )

    if not is_valid_symbol(symbol=symbol, symbols=symbols):
        raise ValueError(
            f"'{symbol}' is not a valid "
            f"symbol for the '{exchange}' exchange. "
            f"Valid symbols: {', '.join(symbols or [])}"
            f"{f' for {repr(provider)}.' if provider else ''}"
        )
    # end if

    return symbol
# end validate_symbol

def validate_interval(interval: str) -> str:
    """
    Validates the interval value.

    :param interval: The interval for the data.

    :return: The valid interval.
    """

    interval_to_total_time(interval)

    return interval
# end validate_interval

def is_valid_interval(interval: str) -> bool:
    """
    Validates the interval value.

    :param interval: The interval for the data.

    :return: The validates value.
    """

    try:
        validate_interval(interval)

        return True

    except ValueError:
        return False
    # end try
# end is_valid_interval

def is_valid_exchange(
        exchange: str, exchanges: Optional[Iterable[str]] = None
) -> bool:
    """
    checks of the source os a valid exchange name.

    :param exchange: The source name to validate.
    :param exchanges: The valid exchanges.

    :return: The validation value.
    """

    if exchanges is None:
        exchanges = EXCHANGE_NAMES
    # end if

    return string_in_values(value=exchange, values=exchanges)
# end is_valid_exchange

def validate_exchange(
        exchange: str,
        exchanges: Optional[Iterable[str]] = None,
        provider: Optional[Any] = None
) -> str:
    """
    Validates the source value.

    :param exchange: The name of the exchange platform.
    :param exchanges: The valid exchanges.
    :param provider: Any provider object.

    :return: The valid exchange.
    """

    if exchanges is None:
        exchanges = EXCHANGE_NAMES
    # end if

    if not is_valid_exchange(exchange=exchange, exchanges=exchanges):
        raise ValueError(
            f"'{exchange}' is not a valid exchange name. "
            f"Valid exchanges: {', '.join(exchanges or [])}"
            f"{f' for {repr(provider)}.' if provider else ''}"
        )
    # end if

    return exchange
# end validate_exchange