# sockets.py

import json
import warnings
import asyncio
import datetime as dt
from typing import Dict, Any, Optional, Union, Iterable, List, Tuple

from crypto_screening.screeners.callbacks import SocketCallback, BaseCallback
from crypto_screening.screeners.base import BaseScreener
from crypto_screening.screeners.collectors.base import ScreenersDataCollector

__all__ = [
    "SocketScreenersDataCollector",
    "SocketCallback"
]

class SocketScreenersDataCollector(ScreenersDataCollector):
    """
    A class to represent an asset price screener.

    Using this class, you can create a screener object to
    screen the market ask and bid data for a specific asset in
    a specific exchange at real time.

    Parameters:

    - screeners:
        The screener object to control and fill with data.

    - location:
        The saving location for the saved data of the screener.

    - cancel:
        The time to cancel screening process after no new data is fetched.

    - delay:
        The delay to wait between each data fetching.

    - screeners:
        The screener object to control and fill with data.

    - address:
        The host for the socket connection.

    - port:
        The port for the socket connection.
    """

    def __init__(
            self,
            address: str,
            port: int,
            screeners: Optional[Iterable[BaseScreener]] = None,
            location: Optional[str] = None,
            cancel: Optional[Union[float, dt.timedelta]] = None,
            delay: Optional[Union[float, dt.timedelta]] = None
    ) -> None:
        """
        Defines the class attributes.

        :param address: The address for the socket.
        :param port: The port for the socket.
        :param location: The saving location for the data.
        :param delay: The delay for the process.
        :param cancel: The cancel time for the loops.
        """

        super().__init__(
            screeners=screeners, location=location,
            cancel=cancel, delay=delay
        )

        self.address = address
        self.port = port

        self.loop: Optional[asyncio.AbstractEventLoop] = None

        self.chunks: Dict[float, List[Dict[str, Any]]] = {}
        self.fail_record: Dict[str, List[Tuple[bytes, Exception]]] = {}
    # end __init__

    async def receive(
            self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter
    ) -> None:
        """
        Receives the data from the senders.

        :param reader: The data reader.
        :param writer: The data writer.
        """

        payload = await reader.read(SocketCallback.MAX_BUFFER)

        try:
            data = json.loads(
                f'[{payload.decode().replace("}{", "},{")}]'
            )

            for payload in data:
                if (
                    (payload[SocketCallback.PROTOCOL] == SocketCallback.UDP_PROTOCOL) and
                    (payload[SocketCallback.FORMAT] == SocketCallback.CHUNKED_FORMAT)
                ):
                    key = payload[SocketCallback.TIMESTAMP]

                    chunks = self.chunks.setdefault(key, [])

                    chunks.append(payload[BaseCallback.DATA])

                    if len(chunks) == payload[SocketCallback.CHUNKS]:
                        payload = json.loads(''.join(chunks[key]))

                        chunks.pop(key)

                        packet = payload[BaseCallback.DATA]

                        self.collect(
                            dict(
                                name=payload[SocketCallback.KEY],
                                data=packet[BaseCallback.DATA],
                                exchange=packet[BaseCallback.EXCHANGE],
                                symbol=packet[BaseCallback.SYMBOL],
                                interval=packet[BaseCallback.INTERVAL]
                            )
                        )
                    # end if

                else:
                    packet = payload[BaseCallback.DATA]

                    self.collect(
                        dict(
                            name=payload[SocketCallback.KEY],
                            data=packet[BaseCallback.DATA],
                            exchange=packet[BaseCallback.EXCHANGE],
                            symbol=packet[BaseCallback.SYMBOL],
                            interval=packet[BaseCallback.INTERVAL]
                        )
                    )
                # end for
            # end for

        except Exception as e:
            self.fail_record.setdefault(
                writer.get_extra_info('peername'), []
            ).append((payload, e))
        # end try
    # end receive

    async def receiving_loop(
            self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter
    ) -> None:
        """
        Receives the data from the senders.

        :param reader: The data reader.
        :param writer: The data writer.
        """

        while self.screening:
            try:
                await self.receive(reader=reader, writer=writer)

            except (
                ConnectionResetError, ConnectionError,
                ConnectionAbortedError, ConnectionRefusedError
            ) as e:
                warnings.warn(str(e))

                self.terminate()
            # end try
        # end while
    # end receiving_loop

    def screening_loop(
            self,
            loop: Optional[asyncio.AbstractEventLoop] = None
    ) -> None:
        """
        Runs the process of the price screening.

        :param loop: The event loop.
        """

        if loop is None:
            loop = asyncio.new_event_loop()
        # end if

        self.loop = loop

        asyncio.set_event_loop(loop)

        async def run() -> None:
            """Runs the program to receive data."""

            server = await asyncio.start_server(
                self.receiving_loop, self.address, self.port
            )

            await server.serve_forever()
        # end run

        self._screening = True

        asyncio.run(run())
    # end screening_loop
# end SocketScreenersDataCollector