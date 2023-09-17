# base.py

import datetime as dt
import time
from abc import ABCMeta
from typing import Iterable, List, Type, TypeVar, Optional, Dict, Union, Any

import pandas as pd

from represent import Modifiers, represent

from multithreading import Caller, multi_threaded_call

from crypto_screening.dataset import save_dataset, load_dataset, create_dataset
from crypto_screening.symbols import adjust_symbol
from crypto_screening.validate import validate_exchange, validate_symbol
from crypto_screening.collect.symbols import all_exchange_symbols
from crypto_screening.screeners.foundation.state import WaitingState
from crypto_screening.screeners.foundation.data import DataCollector
from crypto_screening.screeners.foundation.protocols import BaseScreenerProtocol
from crypto_screening.screeners.foundation.waiting import (
    base_await_initialization, base_await_dynamic_initialization,
    base_await_dynamic_update, base_await_update
)

__all__ = [
    "BaseScreener",
    "BaseMarketScreener",
    "BaseScreenersContainer",
    "screeners_table",
    "BaseFrozenScreenersContainer"
]

class BaseScreener(DataCollector):
    """
    A class to represent an asset price screener.

    Using this class, you can create a screener object to
    screen the market ask and bid data for a specific asset in
    a specific exchange at real time.

    Parameters:

    - symbol:
        The symbol of an asset to screen.

    - exchange:
        The key of the exchange platform to screen data from.

    - location:
        The saving location for the saved data of the screener.

    - cancel:
        The time to cancel screening process after no new data is fetched.

    - delay:
        The delay to wait between each data fetching.

    - market:
        The dataset of the market data.

    - memory:
        The memory size for the dataset.
    """

    __modifiers__ = Modifiers(hidden=["market"])

    MINIMUM_DELAY = 1

    NAME: Optional[str] = "BASE"
    COLUMNS: Iterable[str] = []

    SCREENER_NAME_TYPE_MATCHES: Dict[str, Any] = {}
    SCREENER_TYPE_NAME_MATCHES: Dict[Any, str] = {}

    __slots__ = "_symbol", "_exchange", "market", "memory"

    def __init__(
            self,
            symbol: str,
            exchange: str,
            memory: Optional[int] = None,
            location: Optional[str] = None,
            cancel: Optional[Union[float, dt.timedelta]] = None,
            delay: Optional[Union[float, dt.timedelta]] = None,
            market: Optional[pd.DataFrame] = None,
    ) -> None:
        """
        Defines the class attributes.

        :param symbol: The symbol of the asset.
        :param exchange: The exchange to get source data from.
        :param location: The saving location for the data.
        :param memory: The memory limitation of the market dataset.
        :param delay: The delay for the process.
        :param cancel: The cancel time for the loops.
        :param market: The data for the market.
        """

        if not self.COLUMNS:
            raise ValueError(
                f"{repr(self)} must define a non-empty "
                f"'COLUMNS' instance or class attribute."
            )
        # end if

        super().__init__(location=location, cancel=cancel, delay=delay)

        self.SCREENER_NAME_TYPE_MATCHES.setdefault(self.NAME, type(self))
        self.SCREENER_TYPE_NAME_MATCHES.setdefault(type(self), self.NAME)

        self._exchange = self.validate_exchange(exchange=exchange)
        self._symbol = self.validate_symbol(exchange=self._exchange, symbol=symbol)

        if market is None:
            market = create_dataset(self.COLUMNS)
        # end if

        self.market = market

        self.memory = memory
    # end __init__

    @property
    def symbol(self) -> str:
        """
        Returns the property value.

        :return: The symbol.
        """

        return self._symbol
    # end symbol

    @property
    def exchange(self) -> str:
        """
        Returns the property value.

        :return: The exchange name.
        """

        return self._exchange
    # end exchange

    def await_initialization(
            self,
            stop: Optional[Union[bool, int]] = False,
            delay: Optional[Union[float, dt.timedelta]] = None,
            cancel: Optional[Union[float, dt.timedelta, dt.datetime]] = None
    ) -> WaitingState[BaseScreenerProtocol]:
        """
        Waits for all the create_screeners to update.

        :param delay: The delay for the waiting.
        :param stop: The value to stop the screener objects.
        :param cancel: The time to cancel the waiting.

        :returns: The total delay.
        """

        self: Union[BaseScreener, BaseScreenerProtocol]

        return base_await_initialization(
            self, stop=stop, delay=delay, cancel=cancel
        )
    # end await_initialization

    def await_update(
            self,
            stop: Optional[Union[bool, int]] = False,
            delay: Optional[Union[float, dt.timedelta]] = None,
            cancel: Optional[Union[float, dt.timedelta, dt.datetime]] = None
    ) -> WaitingState[BaseScreenerProtocol]:
        """
        Waits for all the create_screeners to update.

        :param delay: The delay for the waiting.
        :param stop: The value to stop the screener objects.
        :param cancel: The time to cancel the waiting.

        :returns: The total delay.
        """

        self: Union[BaseScreener, BaseScreenerProtocol]

        return base_await_update(
            self, stop=stop, delay=delay, cancel=cancel
        )
    # end await_update

    @staticmethod
    def validate_exchange(exchange: str) -> str:
        """
        Validates the symbol value.

        :param exchange: The exchange key.

        :return: The validates symbol.
        """

        return validate_exchange(exchange=exchange)
    # end validate_exchange

    @staticmethod
    def validate_symbol(exchange: str, symbol: Any) -> str:
        """
        Validates the symbol value.

        :param exchange: The exchange key.
        :param symbol: The key of the symbol.

        :return: The validates symbol.
        """

        return validate_symbol(
            exchange=exchange, symbol=symbol,
            symbols=all_exchange_symbols(exchange=exchange)
        )
    # end validate_symbol

    def dataset_path(self, location: Optional[str] = None) -> str:
        """
        Creates the path to the saving file for the screener object.

        :param location: The saving location of the dataset.

        :return: The saving path for the dataset.
        """

        location = location or self.location

        if location is None:
            location = "."
        # end if

        return (
            f"{location}/"
            f"{self.exchange.lower()}/"
            f"{self.NAME}-"
            f"{adjust_symbol(self.symbol, separator='-')}.csv"
        )
    # end dataset_path

    def save_dataset(self, location: Optional[str] = None) -> None:
        """
        Saves the data of the screener.

        :param location: The saving location of the dataset.
        """

        if len(self.market) == 0:
            return
        # end if

        save_dataset(
            dataset=self.market,
            path=self.dataset_path(location=location)
        )
    # end save_dataset

    def load_dataset(self, location: Optional[str] = None) -> None:
        """
        Saves the data of the screener.

        :param location: The saving location of the dataset.
        """

        data = load_dataset(path=self.dataset_path(location=location))

        for index, data in zip(data.index[:], data.loc[:]):
            self.market.loc[index] = data
        # end for
    # end load_dataset

    def saving_loop(self) -> None:
        """Runs the process of the price screening."""

        self._saving = True

        delay = self.delay

        if isinstance(self.delay, dt.timedelta):
            delay = delay.total_seconds()
        # end if

        while self.saving:
            start = time.time()

            self.save_dataset()

            end = time.time()

            time.sleep(max([delay - (end - start), self.MINIMUM_DELAY]))
        # end while
    # end saving_loop
# end BaseScreener

_S = TypeVar("_S")

ScreenersTable = Dict[
    Optional[Type[BaseScreener]],
    Dict[
        Optional[str],
        Dict[Optional[str], Dict[Optional[str], List[BaseScreener]]]
    ]
]

def screeners_table(
        screeners: Iterable[BaseScreener],
        table: Optional[ScreenersTable] = None
) -> ScreenersTable:
    """
    Inserts all the screeners into the table.

    :param screeners: The screeners to insert into the table.
    :param table: The table to use for the data.

    :return: The screeners table.
    """

    if table is None:
        table = {}
    # end if

    for screener in screeners:
        for interval in {
            (
                screener.interval
                if hasattr(screener, "interval") else
                None
            ), None
        }:
            lists = [
                (
                    table.
                    setdefault(type(screener), {}).
                    setdefault(screener.exchange, {}).
                    setdefault(screener.symbol, {}).
                    setdefault(interval, [])
                ),
                (
                    table.
                    setdefault(type(screener), {}).
                    setdefault(screener.exchange, {}).
                    setdefault(None, {}).
                    setdefault(interval, [])
                ),
                (
                    table.
                    setdefault(type(screener), {}).
                    setdefault(None, {}).
                    setdefault(screener.symbol, {}).
                    setdefault(interval, [])
                ),
                (
                    table.
                    setdefault(type(screener), {}).
                    setdefault(None, {}).
                    setdefault(None, {}).
                    setdefault(interval, [])
                ),
                (
                    table.
                    setdefault(type(screener), {}).
                    setdefault(None, {}).
                    setdefault(None, {}).
                    setdefault(None, [])
                ),
                (
                    table.
                    setdefault(None, {}).
                    setdefault(screener.exchange, {}).
                    setdefault(screener.symbol, {}).
                    setdefault(interval, [])
                ),
                (
                    table.
                    setdefault(None, {}).
                    setdefault(screener.exchange, {}).
                    setdefault(None, {}).
                    setdefault(interval, [])
                ),
                (
                    table.
                    setdefault(None, {}).
                    setdefault(None, {}).
                    setdefault(screener.symbol, {}).
                    setdefault(interval, [])
                ),
                (
                    table.
                    setdefault(None, {}).
                    setdefault(None, {}).
                    setdefault(None, {}).
                    setdefault(interval, [])
                )
            ]

            for screeners_list in lists:
                if screener not in screeners_list:
                    screeners_list.append(screener)
                # end if
            # end for
        # end for
    # end for

    return table
# end screeners_table

@represent
class BaseFrozenScreenersContainer:
    """
    A class to represent a multi-exchange multi-pairs crypto data screener.
    Using this class enables extracting screener objects and screeners
    data by the exchange name and the symbol of the pair.

    parameters:

    - screeners:
        The screener objects to form a market.

    >>> from crypto_screening.screeners import BaseFrozenScreenersContainer, BaseScreener
    >>>
    >>> container = BaseFrozenScreenersContainer(
    >>>     screeners=[BaseScreener(exchange="binance", symbol="BTC/USDT")]
    >>> )
    """

    def __init__(self, screeners: Iterable[BaseScreener]) -> None:
        """
        Defines the class attributes.

        :param screeners: The data screener object.
        """

        self._screeners = list(screeners)

        self._table = screeners_table(self.screeners)
    # end __init__

    @property
    def screeners(self) -> List[BaseScreener]:
        """
        Returns a list of all the screeners.

        :return: The screeners.
        """

        return list(self._screeners)
    # end screeners

    def structure(self) -> Dict[str, List[str]]:
        """
        Returns the structure of the market data.

        :return: The structure of the market.
        """

        return {
            exchange: list([symbol for symbol in symbols if symbol is not None])
            for exchange, symbols in self._table[None].items()
            if exchange is not None
        }
    # end structure

    def find_screeners(
            self,
            exchange: Optional[str] = None,
            symbol: Optional[str] = None,
            base: Optional[Type[_S]] = None,
            interval: Optional[str] = None,
            adjust: Optional[bool] = True
    ) -> List[_S]:
        """
        Returns the data by according to the parameters.

        :param base: The base type of the screener.
        :param exchange: The exchange name.
        :param symbol: The symbol name.
        :param interval: The interval for the search.
        :param adjust: The value to adjust for the screeners.

        :return: The data.
        """

        try:
            return list(self._table[base][exchange][symbol][interval])

        except KeyError:
            if not adjust:
                raise ValueError(
                    f"Cannot find screeners  matching to "
                    f"type - {base}, exchange - {exchange}, "
                    f"symbol - {symbol}, interval - {interval} "
                    f"inside {repr(self)}"
                )
            # end if
        # end try

        return []
    # end find_screeners

    def find_screener(
            self,
            exchange: Optional[str] = None,
            symbol: Optional[str] = None,
            base: Optional[Type[_S]] = None,
            interval: Optional[str] = None,
            index: Optional[int] = None,
            adjust: Optional[bool] = False
    ) -> _S:
        """
        Returns the data by according to the parameters.

        :param base: The base type of the screener.
        :param exchange: The exchange name.
        :param symbol: The symbol name.
        :param interval: The interval for the search.
        :param index: The index of the screener in the list.
        :param adjust: The value to adjust for the screeners.

        :return: The data.
        """

        try:
            return self.find_screeners(
                exchange=exchange, symbol=symbol,
                base=base, interval=interval, adjust=adjust
            )[index or 0]

        except IndexError:
            if not adjust:
                raise IndexError(
                    f"Cannot find screeners matching to "
                    f"type - {base}, exchange - {exchange}, "
                    f"symbol - {symbol}, interval - {interval}, "
                    f"index - {index} inside {repr(self)}"
                )
            # end if
        # end try
    # end find_orderbook_screener

    def screener_in_market(
            self,
            exchange: Optional[str] = None,
            symbol: Optional[str] = None,
            base: Optional[Type[_S]] = None,
            interval: Optional[str] = None
    ) -> bool:
        """
        Returns the data by according to the parameters.

        :param base: The base type of the screener.
        :param exchange: The exchange name.
        :param symbol: The symbol name.
        :param interval: The interval to search.

        :return: The data.
        """

        try:
            self.find_screener(
                exchange=exchange, symbol=symbol,
                base=base, interval=interval
            )

            return True

        except ValueError:
            return False
        # end try
    # end screener_in_market
# end MappedScreenersContainer

@represent
class BaseScreenersContainer(BaseFrozenScreenersContainer):
    """
    A class to represent a multi-exchange multi-pairs crypto data screener.
    Using this class enables extracting screener objects and screeners
    data by the exchange name and the symbol of the pair.

    parameters:

    - screeners:
        The screener objects to form a market.

    >>> from crypto_screening.screeners import BaseScreenersContainer, BaseScreener
    >>>
    >>> container = BaseScreenersContainer(
    >>>     screeners=[BaseScreener(exchange="binance", symbol="BTC/USDT")]
    >>> )
    """

    @property
    def screeners(self) -> List[BaseScreener]:
        """
        Returns a list of all the screeners.

        :return: The screeners.
        """

        return self._screeners
    # end screeners

    @screeners.setter
    def screeners(self, value: List[BaseScreener]) -> None:
        """
        Returns a list of all the screeners.

        :param value: The screeners.
        """

        previous_screeners = set(self._screeners)

        self._screeners = value

        new_screeners = set(value)

        added = new_screeners - previous_screeners
        removed = previous_screeners - new_screeners

        self.add(added)
        self.remove(removed)
    # end screeners

    def update_screeners(self) -> None:
        """Updates the records of the object."""
    # end update_screeners

    def add(
            self,
            screeners: Iterable[BaseScreener],
            adjust: Optional[bool] = True,
            update: Optional[bool] = True
    ) -> None:
        """
        Updates the data with the new screeners.

        :param screeners: The new screeners to add.
        :param adjust: The value to adjust for screeners.
        :param update: The value to update.
        """

        new_screeners = []

        for screener in screeners:
            if screener not in self._screeners:
                new_screeners.append(screener)

            elif not adjust:
                raise ValueError(
                    f"Cannot add screener {repr(screener)} to "
                    f"{repr(self)} because it is already present."
                )
            # end if
        # end for

        self._screeners.extend(new_screeners)

        screeners_table(new_screeners, table=self._table)

        if update:
            self.update_screeners()
        # end if
    # end update

    def remove(
            self,
            screeners: Iterable[BaseScreener],
            adjust: Optional[bool] = True,
            update: Optional[bool] = True
    ) -> None:
        """
        Updates the data with the new screeners.

        :param screeners: The new screeners to add.
        :param adjust: The value to adjust for screeners.
        :param update: The value to update.
        """

        for screener in screeners:
            if screener in self._screeners:
                self._screeners.remove(screener)

            elif not adjust:
                raise ValueError(
                    f"Cannot remove screener {repr(screener)} from "
                    f"{repr(self)} because it is not present."
                )
            # end if
        # end for

        self._table.clear()

        screeners_table(self._screeners, table=self._table)

        if update:
            self.update_screeners()
        # end if
    # end remove
# end BaseScreenersContainer

class BaseMarketScreener(DataCollector, BaseScreenersContainer, metaclass=ABCMeta):
    """
    A class to represent an asset price screener.

    Using this class, you can create a screener object to
    screen the market ask and bid data for a specific asset in
    a specific exchange at real time.

    Parameters:

    - location:
        The saving location for the saved data of the screener.

    - cancel:
        The time to cancel screening process after no new data is fetched.

    - delay:
        The delay to wait between each data fetching.

    - screeners:
        The screener object to control and fill with data.
    """

    def __init__(
            self,
            screeners: Optional[Iterable[BaseScreener]] = None,
            location: Optional[str] = None,
            cancel: Optional[Union[float, dt.timedelta]] = None,
            delay: Optional[Union[float, dt.timedelta]] = None
    ) -> None:
        """
        Defines the class attributes.

        :param location: The saving location for the data.
        :param delay: The delay for the process.
        :param cancel: The cancel time for the loops.
        """

        DataCollector.__init__(self, location=location, cancel=cancel, delay=delay)

        BaseScreenersContainer.__init__(self, screeners=screeners)

        self._saving_screeners: List[BaseScreener] = []
    # end __init__

    def await_initialization(
            self,
            stop: Optional[Union[bool, int]] = False,
            delay: Optional[Union[float, dt.timedelta]] = None,
            cancel: Optional[Union[float, dt.timedelta, dt.datetime]] = None
    ) -> WaitingState[BaseScreener]:
        """
        Waits for all the create_screeners to update.

        :param delay: The delay for the waiting.
        :param stop: The value to stop the screener objects.
        :param cancel: The time to cancel the waiting.

        :returns: The total delay.
        """

        return base_await_dynamic_initialization(
            self.screeners, stop=stop, delay=delay, cancel=cancel
        )
    # end await_initialization

    def await_update(
            self,
            stop: Optional[Union[bool, int]] = False,
            delay: Optional[Union[float, dt.timedelta]] = None,
            cancel: Optional[Union[float, dt.timedelta, dt.datetime]] = None
    ) -> WaitingState[BaseScreener]:
        """
        Waits for all the create_screeners to update.

        :param delay: The delay for the waiting.
        :param stop: The value to stop the screener objects.
        :param cancel: The time to cancel the waiting.

        :returns: The total delay.
        """

        return base_await_dynamic_update(
            self.screeners, stop=stop, delay=delay, cancel=cancel
        )
    # end await_update

    def save_datasets(self, location: Optional[str] = None) -> None:
        """
        Runs the data handling loop.

        :param location: The saving location.
        """

        callers = []

        for screener in self.screeners:
            location = location or screener.location or self.location

            callers.append(
                Caller(
                    target=screener.save_dataset,
                    kwargs=dict(location=location)
                )
            )
        # end for

        multi_threaded_call(callers=callers)
    # end save_datasets

    def load_datasets(self, location: Optional[str] = None) -> None:
        """
        Runs the data handling loop.

        :param location: The saving location.
        """

        callers = []

        for screener in self.screeners:
            location = location or screener.location or self.location

            callers.append(
                Caller(
                    target=screener.load_dataset,
                    kwargs=dict(location=location)
                )
            )
        # end for

        multi_threaded_call(callers=callers)
    # end load_datasets

    def saving_loop(self) -> None:
        """Runs the process of the price screening."""

        for screener in self.screeners:
            if not screener.saving:
                screener.start_saving()

                self._saving_screeners.append(screener)
            # end if
        # end for
    # end saving_loop

    def stop_saving(self) -> None:
        """Stops the saving of the screeners."""

        for screener in self._saving_screeners:
            screener.stop_saving()
        # end for
    # end stop_saving
# end BaseMarketScreener