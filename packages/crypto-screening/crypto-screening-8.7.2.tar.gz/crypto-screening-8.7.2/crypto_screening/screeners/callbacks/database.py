# database.py

import datetime as dt
from typing import Optional, Any, Dict, List, Tuple

from sqlalchemy import Engine, text, inspect
from sqlalchemy.orm import sessionmaker

from crypto_screening.dataset import DATE_TIME
from crypto_screening.screeners.database import (
    create_engine, parts_to_database_table_name
)
from crypto_screening.screeners.callbacks.base import BaseCallback

__all__ = [
    "DatabaseCallback"
]

class DatabaseCallback(BaseCallback):
    """A class to represent a callback."""

    CONNECTABLE: bool = True

    DATATYPES = {
        str: "TEXT",
        bool: "BOOL",
        int: "INTEGER",
        float: "FLOAT",
        dt.datetime: "DATETIME"
    }

    def __init__(
            self,
            database: str,
            engine: Optional[Engine] = None,
            key: Optional[Any] = None
    ) -> None:
        """
        Defines the class attributes.

        :param database: The path to the database.
        :param engine: The engine for the database.
        :param key: The key od the data.
        """

        super().__init__(key=key)

        self.database = database

        self.engine = engine

        if isinstance(self.engine, Engine):
            self._connected = True
        # end if

        self._session: Optional = None

        self.tables: Dict[Tuple[str, str, str, Optional[str]], str] = {}
        self.table_names: Optional[List[str]] = None
    # end __init__

    async def handle(
            self,
            data: Dict[str, Any],
            timestamp: float,
            key: Optional[Any] = None) -> bool:
        """
        Records the data from the crypto feed into the dataset.

        :param data: The data from the exchange.
        :param timestamp: The time of the request.
        :param key: The key for the data type.

        :return: The validation value.
        """

        if self._session is None:
            self._session = sessionmaker(bind=self.engine)()
        # end if

        if self.table_names is None:
            self.table_names = inspect(self.engine).get_table_names()
        # end if

        for index, row in data[self.DATA]:
            key, exchange, symbol, interval = (
                key or self.key, data[self.EXCHANGE],
                data[self.SYMBOL], data.get(self.INTERVAL, None)
            )

            if (key, exchange, symbol, interval) not in self.tables:
                table = parts_to_database_table_name(
                    name=key, exchange=exchange,
                    symbol=symbol, interval=interval
                )

                self.tables[(key, exchange, symbol, interval)] = table

                if table not in self.table_names:
                    creation = ', '.join(
                        f"{column} {self.DATATYPES[type(value)]}"
                        for column, value in row.items()
                    )

                    self._session.execute(
                        text(
                            "CREATE TABLE " + table +
                            f" ({DATE_TIME} TEXT, {creation}, "
                            f"PRIMARY KEY ({DATE_TIME}));"
                        )
                    )
                # end if

            else:
                table = self.tables.setdefault(
                    (key, exchange, symbol, interval),
                    parts_to_database_table_name(
                        name=key, exchange=exchange,
                        symbol=symbol, interval=interval
                    )
                )
            # end if

            index = dt.datetime.fromtimestamp(index)

            attributes = (repr(str(value)) for value in row.values())

            self._session.execute(
                text(
                    "INSERT INTO " + table +
                    f" VALUES ('{index}', {', '.join(attributes)});"
                )
            )

            self._session.commit()
        # end for

        if data[self.DATA]:
            return True

        else:
            return False
        # end if
    # end process

    async def start(self) -> None:
        """Connects to the socket service."""

        self.engine = self.engine or create_engine(self.database)
    # end start
# end DatabaseCallback