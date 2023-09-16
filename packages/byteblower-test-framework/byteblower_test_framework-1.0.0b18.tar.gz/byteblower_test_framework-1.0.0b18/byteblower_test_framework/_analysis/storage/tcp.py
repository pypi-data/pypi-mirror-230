from typing import Optional  # for type hinting

import pandas
from pandas import Timestamp  # for type hinting

from .data_store import DataStore


class HttpData(DataStore):

    __slots__ = (
        '_http_method',
        '_df_tcp_client',
        '_df_tcp_server',
        '_avg_data_speed',
        '_total_rx_client',
        '_total_tx_client',
        '_total_rx_server',
        '_total_tx_server',
        '_ts_rx_first_client',
        '_ts_rx_last_client',
        '_ts_tx_first_client',
        '_ts_tx_last_client',
        '_ts_rx_first_server',
        '_ts_rx_last_server',
        '_ts_tx_first_server',
        '_ts_tx_last_server',
    )

    def __init__(self) -> None:
        self._df_tcp_client = pandas.DataFrame(
            columns=[
                'duration',
                'TX Bytes',
                'RX Bytes',
                'AVG dataspeed',
            ]
        )

        self._df_tcp_server = pandas.DataFrame(
            columns=[
                'duration',
                'TX Bytes',
                'RX Bytes',
                'AVG dataspeed',
            ]
        )
        self._http_method: Optional[str] = None
        self._avg_data_speed: Optional[float] = None
        self._total_rx_client: int = 0
        self._total_tx_client: int = 0
        self._total_rx_server: int = 0
        self._total_tx_server: int = 0
        self._ts_rx_first_client: Optional[Timestamp] = None
        self._ts_rx_last_client: Optional[Timestamp] = None
        self._ts_tx_first_client: Optional[Timestamp] = None
        self._ts_tx_last_client: Optional[Timestamp] = None

        self._ts_rx_first_server: Optional[Timestamp] = None
        self._ts_rx_last_server: Optional[Timestamp] = None
        self._ts_tx_first_server: Optional[Timestamp] = None
        self._ts_tx_last_server: Optional[Timestamp] = None

    @property
    def http_method(self) -> str:
        """Return the configured HTTP Request Method."""
        return self._http_method

    @property
    def df_tcp_client(self) -> pandas.DataFrame:
        """TCP result history."""
        return self._df_tcp_client

    @property
    def df_tcp_server(self) -> pandas.DataFrame:
        """TCP result history."""
        return self._df_tcp_server

    @property
    def avg_data_speed(self) -> Optional[float]:
        """Average data speed in Bytes per second."""
        return self._avg_data_speed

    @property
    def total_rx_client(self) -> float:
        """Number of received bytes at HTTP Client."""
        return self._total_rx_client

    @property
    def total_tx_client(self) -> float:
        """Number of transmitted bytes at HTTP Client."""
        return self._total_tx_client

    @property
    def total_rx_server(self) -> float:
        """Number of received bytes at HTTP Server."""
        return self._total_rx_server

    @property
    def total_tx_server(self) -> float:
        """Number of transmitted bytes at HTTP Server."""
        return self._total_tx_server

    @property
    def ts_rx_first_client(self) -> Optional[Timestamp]:
        """Time when the first packet was received at the HTTP Client."""
        return self._ts_rx_first_client

    @property
    def ts_rx_last_client(self) -> Optional[Timestamp]:
        """Time when the last packet was received at the HTTP Client."""
        return self._ts_rx_last_client

    @property
    def ts_tx_first_client(self) -> Optional[Timestamp]:
        """Time when the first packet was transmitted at the HTTP Client."""
        return self._ts_tx_first_client

    @property
    def ts_tx_last_client(self) -> Optional[Timestamp]:
        """Time when the last packet was transmitted at the HTTP Client."""
        return self._ts_tx_last_client

    @property
    def ts_rx_first_server(self) -> Optional[Timestamp]:
        """Time when the first packet was received at the HTTP Server."""
        return self._ts_rx_first_server

    @property
    def ts_rx_last_server(self) -> Optional[Timestamp]:
        """Time when the last packet was received at the HTTP Server."""
        return self._ts_rx_last_server

    @property
    def ts_tx_first_server(self) -> Optional[Timestamp]:
        """Time when the first packet was transmitted at the HTTP Server."""
        return self._ts_tx_first_server

    @property
    def ts_tx_last_server(self) -> Optional[Timestamp]:
        """Time when the last packet was transmitted at the HTTP Server."""
        return self._ts_tx_last_server
