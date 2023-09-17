# container.py

from typing import Optional, List

from crypto_screening.screeners.screener import (
    OHLCVScreener, OrderbookScreener, TradesScreener, OrdersScreener
)
from crypto_screening.screeners.base import (
    BaseFrozenScreenersContainer, BaseScreenersContainer
)

__all__ = [
    "FrozenScreenersContainer",
    "ScreenersContainer"
]

class FrozenScreenersContainer(BaseFrozenScreenersContainer):
    """
    A class to represent a multi-exchange multi-pairs crypto data screener.
    Using this class enables extracting screener objects and screeners
    data by the exchange name and the symbol of the pair.

    parameters:

    - screeners:
        The screener objects to form a market.

    >>> from crypto_screening.screeners.container import FrozenScreenersContainer
    >>> from crypto_screening.screeners import BaseScreener
    >>>
    >>> container = FrozenScreenersContainer(
    >>>     screeners=[BaseScreener(exchange="binance", symbol="BTC/USDT")]
    >>> )
    """

    @property
    def orderbook_screeners(self) -> List[OrderbookScreener]:
        """
        Returns a list of all the order-book screeners.

        :return: The order-book screeners.
        """

        return self.find_screeners(base=OrderbookScreener)
    # end orderbook_screeners

    @property
    def orders_screeners(self) -> List[OrdersScreener]:
        """
        Returns a list of all the order-book screeners.

        :return: The orders screeners.
        """

        return self.find_screeners(base=OrdersScreener)
    # end orders_screeners

    @property
    def ohlcv_screeners(self) -> List[OHLCVScreener]:
        """
        Returns a list of all the order-book screeners.

        :return: The OHLCV screeners.
        """

        return self.find_screeners(base=OHLCVScreener)
    # end ohlcv_screeners

    @property
    def trades_screeners(self) -> List[TradesScreener]:
        """
        Returns a list of all the order-book screeners.

        :return: The trades screeners.
        """

        return self.find_screeners(base=TradesScreener)
    # end trades_screeners

    def orderbook_screener_in_market(
            self,
            exchange: Optional[str] = None,
            symbol: Optional[str] = None
    ) -> bool:
        """
        Returns the data by according to the parameters.

        :param exchange: The exchange name.
        :param symbol: The symbol name.

        :return: The data.
        """

        return self.screener_in_market(
            exchange=exchange, symbol=symbol, base=OrderbookScreener
        )
    # end orderbook_screener_in_market

    def orders_screener_in_market(
            self,
            exchange: Optional[str] = None,
            symbol: Optional[str] = None
    ) -> bool:
        """
        Returns the data by according to the parameters.

        :param exchange: The exchange name.
        :param symbol: The symbol name.

        :return: The data.
        """

        return self.screener_in_market(
            exchange=exchange, symbol=symbol, base=OrdersScreener
        )
    # end orders_screener_in_market

    def find_orderbook_screener(
            self,
            exchange: Optional[str] = None,
            symbol: Optional[str] = None,
            index: Optional[int] = None
    ) -> OrderbookScreener:
        """
        Returns the data by according to the parameters.

        :param exchange: The exchange name.
        :param symbol: The symbol name.
        :param index: The index of the screener in the list.

        :return: The data.
        """

        return self.find_screener(
            exchange=exchange, symbol=symbol,
            base=OrderbookScreener, index=index
        )
    # end find_orderbook_screener

    def find_orders_screener(
            self,
            exchange: Optional[str] = None,
            symbol: Optional[str] = None,
            index: Optional[int] = None
    ) -> OrdersScreener:
        """
        Returns the data by according to the parameters.

        :param exchange: The exchange name.
        :param symbol: The symbol name.
        :param index: The index of the screener in the list.

        :return: The data.
        """

        return self.find_screener(
            exchange=exchange, symbol=symbol,
            base=OrdersScreener, index=index
        )
    # end find_orders_screener

    def find_orderbook_screeners(
            self,
            exchange: Optional[str] = None,
            symbol: Optional[str] = None,
            adjust: Optional[bool] = True
    ) -> List[OrderbookScreener]:
        """
        Returns the data by according to the parameters.

        :param exchange: The exchange name.
        :param symbol: The symbol name.
        :param adjust: The value to adjust for the screeners.

        :return: The data.
        """

        return self.find_screeners(
            exchange=exchange, symbol=symbol,
            base=OrderbookScreener, adjust=adjust
        )
    # end find_orderbook_screener

    def find_orders_screeners(
            self,
            exchange: Optional[str] = None,
            symbol: Optional[str] = None,
            adjust: Optional[bool] = True
    ) -> List[OrdersScreener]:
        """
        Returns the data by according to the parameters.

        :param exchange: The exchange name.
        :param symbol: The symbol name.
        :param adjust: The value to adjust for the screeners.

        :return: The data.
        """

        return self.find_screeners(
            exchange=exchange, symbol=symbol,
            base=OrdersScreener, adjust=adjust
        )
    # end find_orders_screeners

    def ohlcv_screener_in_market(
            self,
            exchange: Optional[str] = None,
            symbol: Optional[str] = None,
            interval: Optional[str] = None
    ) -> bool:
        """
        Returns the data by according to the parameters.

        :param exchange: The exchange name.
        :param symbol: The symbol name.
        :param interval: The interval for the dataset.

        :return: The data.
        """

        try:
            self.find_ohlcv_screener(
                exchange=exchange, symbol=symbol, interval=interval
            )

            return True

        except ValueError:
            return False
    # end ohlcv_screener_in_market

    def trades_screener_in_market(
            self,
            exchange: Optional[str] = None,
            symbol: Optional[str] = None
    ) -> bool:
        """
        Returns the data by according to the parameters.

        :param exchange: The exchange name.
        :param symbol: The symbol name.

        :return: The data.
        """

        return self.screener_in_market(
            exchange=exchange, symbol=symbol, base=TradesScreener
        )
    # end trades_screener_in_market

    def find_ohlcv_screener(
            self,
            exchange: Optional[str] = None,
            symbol: Optional[str] = None,
            interval: Optional[str] = None,
            index: Optional[int] = None
    ) -> OHLCVScreener:
        """
        Returns the data by according to the parameters.

        :param exchange: The exchange name.
        :param symbol: The symbol name.
        :param interval: The interval for the dataset.
        :param index: The index for the screener.

        :return: The data.
        """

        return self.find_screener(
            exchange=exchange, symbol=symbol, base=OHLCVScreener,
            interval=interval, index=index
        )
    # end find_screeners

    def find_trades_screener(
            self,
            exchange: Optional[str] = None,
            symbol: Optional[str] = None,
            index: Optional[int] = None
    ) -> TradesScreener:
        """
        Returns the data by according to the parameters.

        :param exchange: The exchange name.
        :param symbol: The symbol name.
        :param index: The index for the screener.

        :return: The data.
        """

        return self.find_screener(
            exchange=exchange, symbol=symbol, base=TradesScreener,
            index=index
        )
    # end find_trades_screener

    def find_ohlcv_screeners(
            self,
            exchange: Optional[str] = None,
            symbol: Optional[str] = None,
            interval: Optional[str] = None,
            adjust: Optional[bool] = True
    ) -> List[OHLCVScreener]:
        """
        Returns the data by according to the parameters.

        :param exchange: The exchange name.
        :param symbol: The symbol name.
        :param interval: The interval for the datasets.
        :param adjust: The value to adjust for the screeners.

        :return: The data.
        """

        return self.find_screeners(
            exchange=exchange, symbol=symbol, base=OHLCVScreener,
            interval=interval, adjust=adjust
        )
    # end find_ohlcv_screeners

    def find_trades_screeners(
            self,
            exchange: Optional[str] = None,
            symbol: Optional[str] = None,
            adjust: Optional[bool] = True
    ) -> List[TradesScreener]:
        """
        Returns the data by according to the parameters.

        :param exchange: The exchange name.
        :param symbol: The symbol name.
        :param adjust: The value to adjust for the screeners.

        :return: The data.
        """

        return self.find_screeners(
            exchange=exchange, symbol=symbol, base=TradesScreener,
            adjust=adjust
        )
    # end find_trades_screeners
# end FrozenScreenersContainer

class ScreenersContainer(BaseScreenersContainer, FrozenScreenersContainer):
    """
    A class to represent a multi-exchange multi-pairs crypto data screener.
    Using this class enables extracting screener objects and screeners
    data by the exchange name and the symbol of the pair.

    parameters:

    - screeners:
        The screener objects to form a market.

    >>> from crypto_screening.screeners.container import ScreenersContainer
    >>> from crypto_screening.screeners import BaseScreener
    >>>
    >>> container = ScreenersContainer(
    >>>     screeners=[BaseScreener(exchange="binance", symbol="BTC/USDT")]
    >>> )
    """
# end ScreenersContainer