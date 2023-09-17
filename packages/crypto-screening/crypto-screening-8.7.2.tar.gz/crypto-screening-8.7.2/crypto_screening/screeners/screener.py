# screener.py

import datetime as dt
from typing import Optional, Union

import pandas as pd

from crypto_screening.dataset import (
    OHLCV_COLUMNS, load_dataset, save_dataset,
    ORDERBOOK_COLUMNS, ORDERS_COLUMNS, TRADES_COLUMNS
)
from crypto_screening.validate import validate_interval
from crypto_screening.screeners.base import BaseScreener

__all__ = [
    "OrderbookScreener",
    "OrdersScreener",
    "OHLCVScreener",
    "TradesScreener"
]

class OrderbookScreener(BaseScreener):
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
        The dataset of the market data as BID/ASK spread.

    - memory:
        The memory size for the dataset.
    """

    NAME = "ORDERBOOK"

    COLUMNS = ORDERBOOK_COLUMNS

    __slots__ = ()

    @property
    def orderbook_market(self) -> pd.DataFrame:
        """
        Returns the market to hold the recorder data.

        :return: The market object.
        """

        return self.market
    # end orderbook_market
# end OrderbookScreener

class OrdersScreener(BaseScreener):
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
        The dataset of the market data as orders.

    - memory:
        The memory size for the dataset.
    """

    NAME = "ORDERS"

    COLUMNS = ORDERS_COLUMNS

    __slots__ = ()

    @property
    def orders_market(self) -> pd.DataFrame:
        """
        Returns the market to hold the recorder data.

        :return: The market object.
        """

        return self.market
    # end orders_market
# end OrdersScreener

class TradesScreener(BaseScreener):
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
        The dataset of the market data as trades.

    - memory:
        The memory size for the dataset.
    """

    NAME = "TRADES"

    COLUMNS = TRADES_COLUMNS

    __slots__ = ()

    @property
    def trades_market(self) -> pd.DataFrame:
        """
        Returns the market to hold the recorder data.

        :return: The market object.
        """

        return self.market
    # end trades_market
# end TradesScreener

class OHLCVScreener(BaseScreener):
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

    - interval:
        The interval for the data structure of OHLCV.

    - market:
        The dataset of the market data as OHLCV.

    - orderbook_market:
        The dataset of the market data as BID/ASK spread.

    - memory:
        The memory size for the dataset.
    """

    INTERVAL = "1m"
    NAME = "OHLCV"

    COLUMNS = OHLCV_COLUMNS

    __slots__ = "interval", "orderbook_market"

    def __init__(
            self,
            symbol: str,
            exchange: str,
            memory: Optional[int] = None,
            interval: Optional[str] = None,
            location: Optional[str] = None,
            cancel: Optional[Union[float, dt.timedelta]] = None,
            delay: Optional[Union[float, dt.timedelta]] = None,
            market: Optional[pd.DataFrame] = None,
            orderbook_market: Optional[pd.DataFrame] = None
    ) -> None:
        """
        Defines the class attributes.

        :param symbol: The symbol of the asset.
        :param interval: The interval for the data.
        :param exchange: The exchange to get source data from.
        :param location: The saving location for the data.
        :param delay: The delay for the process.
        :param cancel: The cancel time for the loops.
        :param memory: The memory limitation of the market dataset.
        :param market: The data for the market.
        :param orderbook_market: The base market dataset.
        """

        super().__init__(
            symbol=symbol, exchange=exchange, location=location,
            cancel=cancel, delay=delay, market=market, memory=memory
        )

        self.interval = self.validate_interval(interval or self.INTERVAL)

        self.orderbook_market = orderbook_market
    # end __init__

    @staticmethod
    def validate_interval(interval: str) -> str:
        """
        Validates the symbol value.

        :param interval: The interval for the data.

        :return: The validates symbol.
        """

        return validate_interval(interval=interval)
    # end validate_symbol

    @property
    def ohlcv_market(self) -> pd.DataFrame:
        """
        Returns the market to hold the recorder data.

        :return: The market object.
        """

        return self.market
    # end ohlcv_market

    def orderbook_dataset_path(self, location: Optional[str] = None) -> str:
        """
        Creates the path to the saving file for the screener object.

        :param location: The saving location of the dataset.

        :return: The saving path for the dataset.
        """

        return (
            self.dataset_path(location=location).
            replace(self.NAME, OrderbookScreener.NAME)
        )
    # end orderbook_dataset_path

    def save_orderbook_dataset(self, location: Optional[str] = None) -> None:
        """
        Saves the data of the screener.

        :param location: The saving location of the dataset.
        """

        if len(self.orderbook_market) > 0:
            save_dataset(
                dataset=self.orderbook_market,
                path=self.orderbook_dataset_path(location=location)
            )
        # end if
    # end save_orderbook_dataset

    def ohlcv_dataset_path(self, location: Optional[str] = None) -> str:
        """
        Creates the path to the saving file for the screener object.

        :param location: The saving location of the dataset.

        :return: The saving path for the dataset.
        """

        return self.dataset_path(location=location)
    # end ohlcv_dataset_path

    def save_ohlcv_dataset(self, location: Optional[str] = None) -> None:
        """
        Saves the data of the screener.

        :param location: The saving location of the dataset.
        """

        if len(self.ohlcv_market) > 0:
            save_dataset(
                dataset=self.ohlcv_market,
                path=self.ohlcv_dataset_path(location=location)
            )
        # end if
    # end save_ohlcv_dataset

    def save_datasets(self, location: Optional[str] = None) -> None:
        """
        Saves the data of the screener.

        :param location: The saving location of the dataset.
        """

        self.save_ohlcv_dataset(location=location)
        self.save_orderbook_dataset(location=location)
    # end save_datasets

    def load_ohlcv_dataset(self, location: Optional[str] = None) -> None:
        """
        Saves the data of the screener.

        :param location: The saving location of the dataset.
        """

        data = load_dataset(path=self.ohlcv_dataset_path(location=location))

        for index, data in zip(data.index[:], data.loc[:]):
            self.ohlcv_market.loc[index] = data
        # end for
    # end load_ohlcv_dataset

    def load_orderbook_dataset(self, location: Optional[str] = None) -> None:
        """
        Saves the data of the screener.

        :param location: The saving location of the dataset.
        """

        data = load_dataset(path=self.orderbook_dataset_path(location=location))

        for index, data in zip(data.index[:], data.loc[:]):
            self.orderbook_market.loc[index] = data
        # end for
    # end load_orderbook_dataset

    def load_datasets(self, location: Optional[str] = None) -> None:
        """
        Saves the data of the screener.

        :param location: The saving location of the dataset.
        """

        self.load_ohlcv_dataset(location=location)
        self.load_orderbook_dataset(location=location)
    # end load_datasets

    def orderbook_screener(self) -> OrderbookScreener:
        """
        Creates the orderbook screener object.

        :return: The orderbook screener.
        """

        return OrderbookScreener(
            symbol=self.symbol, exchange=self.exchange, location=self.location,
            cancel=self.cancel, delay=self.delay, market=self.orderbook_market
        )
    # end orderbook_screener
# end OHLCVScreener