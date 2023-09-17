# ohlcv.py

import datetime as dt
from typing import (
    Dict, Optional, Iterable, Any,
    Union, List, Callable, Tuple
)

import pandas as pd

from cryptofeed.types import OrderBook
from cryptofeed.defines import L2_BOOK

from crypto_screening.interval import interval_to_total_time
from crypto_screening.dataset import bid_ask_to_ohlcv, create_dataset
from crypto_screening.symbols import adjust_symbol
from crypto_screening.screeners.base import BaseScreener
from crypto_screening.screeners.screener import OHLCVScreener
from crypto_screening.screeners.callbacks.base import (
    BaseCallback, execute_callbacks
)
from crypto_screening.screeners.recorder import (
    MarketScreener, MarketRecorder, MarketHandler, limit_screener_dataset
)
from crypto_screening.screeners.orderbook import (
    OrderbookScreener, record_orderbook, create_orderbook_screeners
)

__all__ = [
    "OHLCVMarketScreener",
    "OHLCVMarketRecorder",
    "OHLCVScreener",
    "ohlcv_market_screener",
    "create_ohlcv_market_dataset",
    "create_ohlcv_screeners"
]

Indexes = Dict[str, Dict[str, Dict[str, int]]]

def create_ohlcv_market_dataset() -> pd.DataFrame:
    """
    Creates a dataframe for the order book data.

    :return: The dataframe.
    """

    return create_dataset(
        columns=OHLCVMarketRecorder.COLUMNS
    )
# end create_ohlcv_market_dataset

async def record_ohlcv(
        screeners: Iterable[Union[OrderbookScreener, OHLCVScreener]],
        indexes: Indexes,
        data: OrderBook,
        timestamp: float,
        insert: Optional[bool] = True,
        callbacks: Optional[Iterable[BaseCallback]] = None
) -> bool:
    """
    Records the data from the crypto feed into the dataset.

    :param screeners: The screeners.
    :param indexes: The indexes of the OHLCV market.
    :param data: The data from the exchange.
    :param timestamp: The time of the request.
    :param insert: The value to insert data into the datasets.
    :param callbacks: The callbacks for the service.

    :return: The validation value.
    """

    orderbook_screeners: List[OrderbookScreener] = [
        screener for screener in screeners
        if isinstance(screener, OrderbookScreener)
    ]

    if not orderbook_screeners:
        return False
    # end if

    if not await record_orderbook(
        screeners=orderbook_screeners, callbacks=callbacks,
        data=data, timestamp=timestamp
    ):
        return False
    # end if

    exchange = data.exchange.lower()
    symbol = adjust_symbol(symbol=data.symbol)

    ohlcv_screeners: Dict[str, List[OHLCVScreener]] = {}
    ohlcv_datasets: Dict[str, pd.DataFrame] = {}

    for screener in screeners:
        if isinstance(screener, OHLCVScreener):
            (
                ohlcv_screeners.
                setdefault(screener.interval, []).
                append(screener)
            )
        # end if
    # end for

    if not ohlcv_screeners:
        return False
    # end if

    spread = orderbook_screeners[0].market

    for interval, screeners in ohlcv_screeners.items():
        dataset_index = (
            indexes.
            setdefault(exchange, {}).
            setdefault(symbol, {}).
            setdefault(interval, 0)
        )

        span: dt.timedelta = spread.index[-1] - spread.index[dataset_index]

        interval_total_time = interval_to_total_time(interval)

        if (span >= interval_total_time) or (dataset_index == 0):
            ohlcv = bid_ask_to_ohlcv(
                dataset=spread.iloc[dataset_index:], interval=interval
            )

            ohlcv_datasets[interval] = ohlcv
        # end for
    # end for

    for interval, ohlcv in ohlcv_datasets.items():
        data: Dict[dt.datetime, Tuple[float, Dict[str, Any]]] = {}

        if insert:
            for screener in ohlcv_screeners[interval]:
                for index, row in ohlcv.iterrows():
                    index: dt.datetime

                    if index not in screener.ohlcv_market.index:
                        screener.ohlcv_market.loc[index] = row
                    # end if

                    data.setdefault(index, (index.timestamp(), row.to_dict()))
                # end for

                limit_screener_dataset(screener)
            # end for
        # end if

        indexes[exchange][symbol][interval] = len(spread)

        await execute_callbacks(
            callbacks=callbacks, key=OHLCVScreener.NAME,
            timestamp=timestamp, data=list(data.values()),
            exchange=exchange, symbol=symbol, interval=interval
        )
    # end for

    return True
# end record_ohlcv

RecorderParameters = Dict[str, Union[Iterable[str], Dict[str, Callable]]]

class OHLCVMarketRecorder(MarketRecorder):
    """
    A class to represent a crypto data feed recorder.
    This object passes the record method to the handler object to record
    the data fetched by the handler.

    Parameters:

    - screeners:
        The screeners to record data into their market datasets.

    - callbacks:
        The callbacks to run when collecting new data.

    >>> from crypto_screening.screeners.ohlcv import OHLCVMarketRecorder
    >>>
    >>> recorder = OHLCVMarketRecorder(...)
    """

    COLUMNS = OHLCVScreener.COLUMNS

    def __init__(
            self,
            screeners: Iterable[BaseScreener],
            callbacks: Optional[Iterable[BaseCallback]] = None,
            insert: Optional[bool] = None
    ) -> None:
        """
        Defines the class attributes.

        :param screeners: The screener objects.
        :param callbacks: The callbacks for the service.
        :param insert: The value to insert data into the market datasets.
        """

        super().__init__(
            screeners=screeners, callbacks=callbacks, insert=insert
        )

        self._indexes: Indexes = {}
    # end __init__

    @property
    def ohlcv_screeners(self) -> List[OHLCVScreener]:
        """
        Returns a list of all the order-book screeners.

        :return: The order-book screeners.
        """

        return self.find_screeners(base=OHLCVScreener)
    # end ohlcv_screeners

    @property
    def orderbook_screeners(self) -> List[OrderbookScreener]:
        """
        Returns a list of all the ohlcv screeners.

        :return: The ohlcv screeners.
        """

        return self.find_screeners(base=OrderbookScreener)
    # end orderbook_screeners

    def parameters(self) -> RecorderParameters:
        """
        Returns the order book parameters.

        :return: The order book parameters.
        """

        return dict(
            channels=[L2_BOOK],
            callbacks={L2_BOOK: self.record},
            max_depth=1
        )
    # end parameters

    async def process(self, data: OrderBook, timestamp: float) -> bool:
        """
        Records the data from the crypto feed into the dataset.

        :param data: The data from the exchange.
        :param timestamp: The time of the request.
        """

        exchange = data.exchange.lower()
        symbol = adjust_symbol(symbol=data.symbol)

        screeners = []

        screeners.extend(
            self.find_screeners(
                base=OrderbookScreener, exchange=exchange, symbol=symbol
            )
        )
        screeners.extend(
            self.find_screeners(
                base=OHLCVScreener, exchange=exchange, symbol=symbol
            )
        )

        return await record_ohlcv(
            screeners=screeners, data=data, indexes=self._indexes,
            callbacks=self.callbacks, timestamp=timestamp, insert=self.insert
        )
    # end process
# end MarketOHLCVRecorder

class OHLCVMarketScreener(MarketScreener):
    """
    A class to represent an asset price screener.

    Using this class, you can create a screener object to
    screen the market ask and bid data for a specific asset in
    a specific exchange at real time.

    Parameters:

    - screeners:
        The screeners to connect to the market screener.

    - intervals:
        The structure to set a specific interval to the dataset
        of each symbol in each exchange, matching the market data.

    - location:
        The saving location for the saved data of the screener.

    - cancel:
        The time to cancel screening process after no new data is fetched.

    - delay:
        The delay to wait between each data fetching.

    - handler:
        The handler object to handle the data feed.

    - recorder:
        The recorder object to record the data of the market from the feed.

    - screeners:
        The screener object to control and fill with data.

    - refresh:
        The duration of time between each refresh. 0 means no refresh.

    - amount:
        The amount of symbols for each symbols group for an exchange.

    - limited:
        The value to limit the running screeners to active exchanges.

    >>> from crypto_screening.screeners.ohlcv import ohlcv_market_screener
    >>>
    >>> structure = {'1m': {'binance': ['BTC/USDT'], 'bittrex': ['ETH/USDT']}}
    >>>
    >>> screener = ohlcv_market_screener(data=structure)
    >>> screener.run()
    """

    screeners: List[Union[OHLCVScreener, OrderbookScreener]]
    recorder: OHLCVMarketRecorder

    COLUMNS = OHLCVMarketRecorder.COLUMNS

    def __init__(
            self,
            recorder: OHLCVMarketRecorder,
            screeners: Optional[Iterable[Union[OHLCVScreener, OrderbookScreener]]] = None,
            location: Optional[str] = None,
            cancel: Optional[Union[float, dt.timedelta]] = None,
            delay: Optional[Union[float, dt.timedelta]] = None,
            refresh: Optional[Union[float, dt.timedelta, bool]] = None,
            limited: Optional[bool] = None,
            handler: Optional[MarketHandler] = None,
            amount: Optional[int] = None,
            insert: Optional[bool] = None
    ) -> None:
        """
        Creates the class attributes.

        :param location: The saving location for the data.
        :param delay: The delay for the process.
        :param cancel: The cancel time for the loops.
        :param limited: The value to limit the screeners to active only.
        :param refresh: The refresh time for rerunning.
        :param handler: The handler object for the market data.
        :param amount: The maximum amount of symbols for each feed.
        :param recorder: The recorder object for recording the data.
        :param insert: The value to insert data into the market datasets.
        """

        super().__init__(
            location=location, cancel=cancel, amount=amount,
            delay=delay, recorder=recorder, insert=insert, refresh=refresh,
            screeners=screeners, handler=handler, limited=limited
        )
    # end __init__

    @property
    def ohlcv_screeners(self) -> List[OHLCVScreener]:
        """
        Returns a list of all the ohlcv screeners.

        :return: The ohlcv screeners.
        """

        return self.find_screeners(base=OHLCVScreener)
    # end ohlcv_screeners

    @property
    def orderbook_screeners(self) -> List[OrderbookScreener]:
        """
        Returns a list of all the ohlcv screeners.

        :return: The ohlcv screeners.
        """

        return self.find_screeners(base=OrderbookScreener)
    # end orderbook_screeners

    def merge_screeners(self) -> None:
        """Connects the screeners to the recording object."""

        for ohlcv_screener in self.ohlcv_screeners:
            for orderbook_screener in self.orderbook_screeners:
                if (
                    (ohlcv_screener.exchange == orderbook_screener.exchange) and
                    (ohlcv_screener.symbol == orderbook_screener.symbol)
                ):
                    ohlcv_screener.orderbook_market = orderbook_screener.market
                # end if
            # end for
        # end for
    # end merge_screeners
# end MarketOHLCVRecorder

def create_ohlcv_screeners(
        data: Dict[str, Union[Iterable[str], Dict[str, Iterable[str]]]],
        location: Optional[str] = None,
        memory: Optional[int] = None,
        cancel: Optional[Union[float, dt.timedelta]] = None,
        delay: Optional[Union[float, dt.timedelta]] = None,
) -> List[OHLCVScreener]:
    """
    Defines the class attributes.

    :param data: The data for the screeners.
    :param location: The saving location for the data.
    :param cancel: The time to cancel the waiting.
    :param delay: The delay for the process.
    :param memory: The memory limitation of the market dataset.
    """

    screeners = []

    for exchange, symbols in data.items():
        if isinstance(symbols, dict):
            for symbol, intervals in symbols.items():
                for interval in intervals:
                    screeners.append(
                        OHLCVScreener(
                            symbol=symbol, exchange=exchange,
                            delay=delay, location=location,
                            cancel=cancel, interval=interval,
                            memory=memory
                        )
                    )
            # end for

        else:
            for symbol in symbols:
                screeners.append(
                    OHLCVScreener(
                        symbol=symbol, exchange=exchange, delay=delay,
                        location=location, cancel=cancel, memory=memory
                    )
                )
        # end if
    # end for

    return screeners
# end create_ohlcv_screeners

def ohlcv_market_screener(
        data: Dict[str, Union[Iterable[str], Dict[str, Iterable[str]]]],
        screeners: Optional[Iterable[OrderbookScreener]] = None,
        location: Optional[str] = None,
        cancel: Optional[Union[float, dt.timedelta]] = None,
        delay: Optional[Union[float, dt.timedelta]] = None,
        limited: Optional[bool] = None,
        handler: Optional[MarketHandler] = None,
        amount: Optional[int] = None,
        memory: Optional[int] = None,
        callbacks: Optional[Iterable[BaseCallback]] = None,
        refresh: Optional[Union[float, dt.timedelta, bool]] = None,
        recorder: Optional[OHLCVMarketRecorder] = None,
        insert: Optional[bool] = None
) -> OHLCVMarketScreener:
    """
    Creates the market screener object for the data.

    :param data: The market data.
    :param screeners: The base screeners.
    :param handler: The handler object for the market data.
    :param limited: The value to limit the screeners to active only.
    :param refresh: The refresh time for rerunning.
    :param amount: The maximum amount of symbols for each feed.
    :param recorder: The recorder object for recording the data.
    :param location: The saving location for the data.
    :param delay: The delay for the process.
    :param cancel: The cancel time for the loops.
    :param callbacks: The callbacks for the service.
    :param insert: The value to insert data into the market datasets.
    :param memory: The memory limitation of the market dataset.

    :return: The market screener object.
    """

    orderbook_screeners = (screeners or []) or create_orderbook_screeners(
        data=data, location=location,
        cancel=cancel, delay=delay, memory=memory
    )

    ohlcv_screeners = create_ohlcv_screeners(
        data=data, location=location, cancel=cancel, delay=delay
    )

    screeners = []
    screeners.extend(orderbook_screeners)
    screeners.extend(ohlcv_screeners)

    market = OHLCVMarketScreener(
        recorder=recorder or OHLCVMarketRecorder(
            screeners=screeners, callbacks=callbacks, insert=insert
        ), screeners=screeners, insert=insert,
        handler=handler, location=location, amount=amount,
        cancel=cancel, delay=delay, limited=limited, refresh=refresh
    )

    market.merge_screeners()

    return market
# end orderbook_market_recorder