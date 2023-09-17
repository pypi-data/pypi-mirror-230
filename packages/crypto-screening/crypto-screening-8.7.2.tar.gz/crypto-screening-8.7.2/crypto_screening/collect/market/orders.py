# orders.py

from abc import ABCMeta
import datetime as dt
from typing import (
    Iterable, Dict, Optional, ClassVar, List, Tuple
)

from attrs import define

from represent import represent, Modifiers

import pandas as pd

from crypto_screening.dataset import BIDS, ASKS

from crypto_screening.screeners import BaseScreener
from crypto_screening.collect.market.state import (
    MarketState, assets_market_values, SymbolsMarketState,
    is_symbol_in_assets_market_values, symbols_market_values,
    is_symbol_in_symbols_market_values, merge_symbols_market_states_data,
    assets_to_symbols_data, assets_market_state_data,
    symbol_to_assets_data, symbols_market_state_data,
    merge_assets_market_states_data, AssetsMarketState
)

__all__ = [
    "symbols_orders_market_state",
    "merge_assets_orders_market_states",
    "merge_symbols_orders_market_states",
    "assets_orders_market_state",
    "AssetsOrdersMarketState",
    "SymbolsOrdersMarketState",
    "symbols_to_assets_orders_market_state",
    "assets_to_symbols_orders_market_state",
    "ORDERS_ATTRIBUTES"
]

AssetsPrices = Dict[str, Dict[str, Dict[str, List[Tuple[dt.datetime, float]]]]]
SymbolsPrices = Dict[str, Dict[str, List[Tuple[dt.datetime, float]]]]

ORDERS_ATTRIBUTES = {
    "bids": BIDS,
    "asks": ASKS
}

@define(repr=False)
@represent
class OrdersMarketState(MarketState, metaclass=ABCMeta):
    """
    A class to represent the current market state.

    This object contains the state of the market, as Close,
    bids and asks values of specific assets, gathered from the network.

    attributes:

    - screeners:
        The screener objects to collect the values of the assets.
    """

    __modifiers__: ClassVar[Modifiers] = Modifiers(
        **MarketState.__modifiers__
    )
    __modifiers__.excluded.extend(["bids", "asks"])

    ATTRIBUTES: ClassVar[Dict[str, str]] = ORDERS_ATTRIBUTES
# end OrderbookMarketBase

AssetsMarketData = Dict[str, Dict[str, Dict[str, List[Tuple[dt.datetime, Dict[str, float]]]]]]
AssetsMarketDatasets = Dict[str, Dict[str, Dict[str, pd.DataFrame]]]

@define(repr=False)
@represent
class AssetsOrdersMarketState(OrdersMarketState, AssetsMarketState):
    """
    A class to represent the current market state.

    This object contains the state of the market, as Close,
    bids and asks values of specific assets, gathered from the network.

    attributes:

    - screeners:
        The screener objects to collect the values of the assets.

    - bids:
        The bids values of the assets.

    - asks:
        The asks values of the assets.

    >>> from crypto_screening.collect.market.orders import assets_orders_market_state
    >>>
    >>> state = assets_orders_market_state(...)
    """

    bids: AssetsPrices
    asks: AssetsPrices

    def bid(
            self, exchange: str, symbol: str, separator: Optional[str] = None
    ) -> List[Tuple[dt.datetime, float]]:
        """
        Returns the bid price for the symbol.

        :param exchange: The exchange name.
        :param symbol: The symbol to find its bid price.
        :param separator: The separator of the assets.

        :return: The bid price for the symbol.
        """

        return assets_market_values(
            exchange=exchange, symbol=symbol, data=self.bids,
            separator=separator, provider=self
        )
    # end bid

    def ask(
            self, exchange: str, symbol: str, separator: Optional[str] = None
    ) -> List[Tuple[dt.datetime, float]]:
        """
        Returns the ask price for the symbol.

        :param exchange: The exchange name.
        :param symbol: The symbol to find its ask price.
        :param separator: The separator of the assets.

        :return: The ask price for the symbol.
        """

        return assets_market_values(
            exchange=exchange, symbol=symbol, data=self.asks,
            separator=separator, provider=self
        )
    # end ask

    def in_bids_prices(
            self,
            exchange: str,
            symbol: str,
            separator: Optional[str] = None
    ) -> bool:
        """
        Checks if the symbol is in the values' data.

        :param exchange: The exchange name.
        :param symbol: The symbol to search.
        :param separator: The separator of the assets.

        :return: The validation value.
        """

        return is_symbol_in_assets_market_values(
            exchange=exchange, symbol=symbol,
            separator=separator, data=self.bids
        )
    # end in_bids_prices

    def in_asks_prices(
            self,
            exchange: str,
            symbol: str,
            separator: Optional[str] = None
    ) -> bool:
        """
        Checks if the symbol is in the values' data.

        :param exchange: The exchange name.
        :param symbol: The symbol to search.
        :param separator: The separator of the assets.

        :return: The validation value.
        """

        return is_symbol_in_assets_market_values(
            exchange=exchange, symbol=symbol,
            separator=separator, data=self.asks
        )
    # end in_asks_prices
# end AssetsMarketStates

def assets_orders_market_state(
        screeners: Optional[Iterable[BaseScreener]] = None,
        separator: Optional[str] = None,
        length: Optional[int] = None,
        adjust: Optional[bool] = True
) -> AssetsOrdersMarketState:
    """
    Fetches the values and relations between the assets.

    :param screeners: The price screeners.
    :param separator: The separator of the assets.
    :param length: The length of the values.
    :param adjust: The value to adjust the length of the sequences.

    :return: The values of the assets.
    """

    return AssetsOrdersMarketState(
        screeners=screeners,
        **assets_market_state_data(
            columns=OrdersMarketState.ATTRIBUTES,
            screeners=screeners, separator=separator,
            length=length, adjust=adjust
        )
    )
# end assets_orders_market_state

SymbolsMarketData = Dict[str, Dict[str, List[Tuple[dt.datetime, Dict[str, float]]]]]
SymbolsMarketDatasets = Dict[str, Dict[str, pd.DataFrame]]

@define(repr=False)
@represent
class SymbolsOrdersMarketState(OrdersMarketState, SymbolsMarketState):
    """
    A class to represent the current market state.

    This object contains the state of the market, as Close,
    bids and asks values of specific assets, gathered from the network.

    attributes:

    - screeners:
        The screener objects to collect the values of the assets.

    - bids:
        The bids values of the assets.

    - asks:
        The asks values of the assets.

    >>> from crypto_screening.collect.market.orders import symbols_orders_market_state
    >>>
    >>> state = symbols_orders_market_state(...)
    """

    bids: SymbolsPrices
    asks: SymbolsPrices

    def bid(self, exchange: str, symbol: str) -> List[Tuple[dt.datetime, float]]:
        """
        Returns the bid price for the symbol.

        :param exchange: The exchange name.
        :param symbol: The symbol to find its bid price.

        :return: The bid price for the symbol.
        """

        return symbols_market_values(
            exchange=exchange, symbol=symbol,
            data=self.bids, provider=self
        )
    # end bid

    def ask(self, exchange: str, symbol: str) -> List[Tuple[dt.datetime, float]]:
        """
        Returns the ask price for the symbol.

        :param exchange: The exchange name.
        :param symbol: The symbol to find its ask price.

        :return: The ask price for the symbol.
        """

        return symbols_market_values(
            exchange=exchange, symbol=symbol,
            data=self.asks, provider=self
        )
    # end ask

    def in_bids_prices(self, exchange: str, symbol: str) -> bool:
        """
        Checks if the symbol is in the values' data.

        :param exchange: The exchange name.
        :param symbol: The symbol to search.

        :return: The validation value.
        """

        return is_symbol_in_symbols_market_values(
            exchange=exchange, symbol=symbol, data=self.bids
        )
    # end in_bids_prices

    def in_asks_prices(self, exchange: str, symbol: str) -> bool:
        """
        Checks if the symbol is in the values' data.

        :param exchange: The exchange name.
        :param symbol: The symbol to search.

        :return: The validation value.
        """

        return is_symbol_in_symbols_market_values(
            exchange=exchange, symbol=symbol, data=self.asks
        )
    # end in_asks_prices
# end SymbolsMarketStates

def symbols_orders_market_state(
        screeners: Optional[Iterable[BaseScreener]] = None,
        length: Optional[int] = None,
        adjust: Optional[bool] = True
) -> SymbolsOrdersMarketState:
    """
    Fetches the values and relations between the assets.

    :param screeners: The price screeners.
    :param length: The length of the values.
    :param adjust: The value to adjust the length of the sequences.

    :return: The values of the assets.
    """

    return SymbolsOrdersMarketState(
        screeners=screeners,
        **symbols_market_state_data(
            columns=OrdersMarketState.ATTRIBUTES, screeners=screeners,
            length=length, adjust=adjust
        )
    )
# end symbols_orders_market_state

def merge_symbols_orders_market_states(
        *states: SymbolsOrdersMarketState, sort: Optional[bool] = True
) -> SymbolsOrdersMarketState:
    """
    Concatenates the states of the market.

    :param states: The states to concatenate.
    :param sort: The value to sort the values by the time.

    :return: The states object.
    """

    screeners = []

    for state in states:
        screeners.extend(state.screeners)
    # end for

    return SymbolsOrdersMarketState(
        screeners=set(screeners),
        **merge_symbols_market_states_data(
            *states, data={
                name: {} for name in OrdersMarketState.ATTRIBUTES
            }, sort=sort
        )
    )
# end merge_symbols_orders_market_states

def merge_assets_orders_market_states(
        *states: AssetsOrdersMarketState, sort: Optional[bool] = True
) -> AssetsOrdersMarketState:
    """
    Concatenates the states of the market.

    :param states: The states to concatenate.
    :param sort: The value to sort the values by the time.

    :return: The states object.
    """

    screeners = []

    for state in states:
        screeners.extend(state.screeners)
    # end for

    return AssetsOrdersMarketState(
        screeners=set(screeners),
        **merge_assets_market_states_data(
            *states, data={
                name: {} for name in OrdersMarketState.ATTRIBUTES
            }, sort=sort
        )
    )
# end merge_assets_orders_market_states

def assets_to_symbols_orders_market_state(
        state: AssetsOrdersMarketState,
        separator: Optional[str] = None
) -> SymbolsOrdersMarketState:
    """
    Converts an assets market state into a symbols market state.

    :param state: The source state.
    :param separator: The separator for the symbols.

    :return: The results state.
    """

    return SymbolsOrdersMarketState(
        **{
            name: assets_to_symbols_data(
                data=getattr(state, name), separator=separator
            ) for name in OrdersMarketState.ATTRIBUTES
        }
    )
# end assets_to_symbols_orders_market_state

def symbols_to_assets_orders_market_state(
        state: SymbolsOrdersMarketState,
        separator: Optional[str] = None
) -> AssetsOrdersMarketState:
    """
    Converts a symbols market state into an assets market state.

    :param state: The source state.
    :param separator: The separator for the symbols.

    :return: The results state.
    """

    return AssetsOrdersMarketState(
        **{
            name: symbol_to_assets_data(
                data=getattr(state, name), separator=separator
            ) for name in OrdersMarketState.ATTRIBUTES
        }
    )
# end symbols_to_assets_orders_market_state