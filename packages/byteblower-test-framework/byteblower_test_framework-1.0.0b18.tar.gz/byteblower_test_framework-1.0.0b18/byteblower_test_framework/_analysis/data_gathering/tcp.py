import logging
from datetime import datetime
from typing import List, Optional, Sequence  # for type hinting

# from byteblowerll.byteblower import HTTPResultDataList  # for type hinting
from byteblowerll.byteblower import HTTPResultData  # for type hinting
from byteblowerll.byteblower import (  # for type hinting
    DataRate,
    HTTPClient,
    HTTPRequestMethod,
    HTTPResultHistory,
    HTTPServer,
)

from ..storage.tcp import HttpData
from .data_gatherer import DataGatherer

_SECONDS_PER_NANOSECOND: int = 1000000000


class HttpDataGatherer(DataGatherer):

    __slots__ = (
        '_http_data',
        '_bb_tcp_clients',
        '_bb_tcp_server',
        '_client_index',
    )

    def __init__(
        self,
        http_data: HttpData,
        bb_tcp_clients: List[HTTPClient],
    ) -> None:
        super().__init__()
        self._http_data = http_data
        self._bb_tcp_clients = bb_tcp_clients
        self._bb_tcp_server: Optional[HTTPServer] = None

        self._client_index = 0

    def set_http_server(self, bb_tcp_server: HTTPServer) -> None:
        self._bb_tcp_server = bb_tcp_server

    def updatestats(self) -> None:
        """
        Analyse the result.

        .. warning::
           What would be bad?

           - TCP sessions not going to ``Finished`` state.
        """
        # Let's analyse the result
        value_rx_client = 0
        value_rx_server = 0
        value_tx_client = 0
        value_tx_server = 0
        value_data_speed_client = 0
        value_data_speed_server = 0
        interval_time_client = None
        interval_time_server = None
        intervals_client = set()
        intervals_server = set()
        duration_client = 0
        duration_server = 0
        # NOTE - Not analysing results for finished HTTP clients
        #        in a previous iteration of updatestats:
        # for client in self._bb_tcp_clients:
        for client in self._bb_tcp_clients[self._client_index:]:
            server_client_id = client.ServerClientIdGet()
            try:
                result_history_client: HTTPResultHistory = \
                    client.ResultHistoryGet()
                # Get interval result
                result_history_client.Refresh()
                # Cfr.HTTPResultDataList
                interval_results_client: Sequence[HTTPResultData] = \
                    result_history_client.IntervalGet()
                for result in interval_results_client[:-1]:
                    intervals_client.add(result.TimestampGet())
                    average_data_speed_client: DataRate = \
                        result.AverageDataSpeedGet()
                    duration_client += result.IntervalDurationGet()
                    value_rx_client += result.RxByteCountTotalGet()
                    value_tx_client += result.TxByteCountTotalGet()
                    value_data_speed_client += \
                        average_data_speed_client.ByteRateGet()
                    logging.debug(
                        '\tAdding extra bytes: %d',
                        result.RxByteCountTotalGet()
                    )
                    # NOTE - Use the newest timestamp as the timestamp
                    #        for the results in the data storage
                    if interval_time_client is None:
                        interval_time_client = datetime.fromtimestamp(
                            result.TimestampGet() / _SECONDS_PER_NANOSECOND
                        )
                result_history_client.Clear()
            except Exception:
                logging.debug("Couldn't get result in HttpAnalyser")

            try:
                result_history_server: HTTPResultHistory = \
                    self._bb_tcp_server.ResultHistoryGet(server_client_id)
                # Get interval result
                result_history_server.Refresh()
                # Cfr. HTTPResultDataList
                interval_results_server: Sequence[HTTPResultData] = \
                    result_history_server.IntervalGet()
                for result in interval_results_server[:-1]:
                    intervals_server.add(result.TimestampGet())
                    average_data_speed_server: DataRate = \
                        result.AverageDataSpeedGet()
                    duration_server += result.IntervalDurationGet()
                    value_rx_server += result.RxByteCountTotalGet()
                    value_tx_server += result.TxByteCountTotalGet()
                    value_data_speed_server += \
                        average_data_speed_server.ByteRateGet()
                    logging.debug(
                        '\tAdding extra bytes: %d',
                        result.RxByteCountTotalGet()
                    )
                    # NOTE - Use the newest timestamp as the timestamp
                    #        for the results in the data storage
                    if interval_time_server is None:
                        interval_time_server = datetime.fromtimestamp(
                            result.TimestampGet() / _SECONDS_PER_NANOSECOND
                        )
                result_history_server.Clear()
            except Exception:
                logging.debug("Couldn't get result in HttpAnalyser")

        # NOTE - Don't analyse results for finished HTTP clients
        #        in a next iteration of updatestats:
        self._client_index = len(self._bb_tcp_clients)
        if self._client_index > 0:
            # ! FIXME - Shouldn't we check if HTTP client actually finished?
            self._client_index -= 1
        if interval_time_client is not None:
            # Got client results in this iteration
            if len(intervals_client) > 1:
                logging.warning(
                    'HttpDataGatherer: Got %d intervals (client): %r',
                    len(intervals_client), intervals_client
                )
                value_data_speed_client /= len(intervals_client)
            self._http_data.df_tcp_client.loc[interval_time_client] = (
                duration_client,
                value_tx_client,
                value_rx_client,
                value_data_speed_client,
            )

        if interval_time_server is None:
            # No results in this iteration
            return
        if len(intervals_server) > 1:
            logging.warning(
                'HttpDataGatherer: Got %d intervals (server): %r',
                len(intervals_server), intervals_server
            )
            value_data_speed_server /= len(intervals_server)
        self._http_data.df_tcp_server.loc[interval_time_server] = (
            duration_server,
            value_tx_server,
            value_rx_server,
            value_data_speed_server,
        )

    def summarize(self) -> None:
        """
        Store the final results.

        Stores the average data speed over the complete session.

        .. todo::
           This summary does not support multiple clients yet.
           It is only created for the last client.
        """
        # Take only the last client (if one available)
        # ! FIXME - Take average over multiple clients
        value_data_speed = None
        # Set client results
        total_rx_client = 0
        total_tx_client = 0
        rx_first_client = None
        rx_last_client = None
        tx_first_client = None
        tx_last_client = None
        # Set server results
        total_rx_server = 0
        total_tx_server = 0
        rx_first_server = None
        rx_last_server = None
        tx_first_server = None
        tx_last_server = None
        if len(self._bb_tcp_clients) > 1:
            logging.warning(
                'HttpAnalyser summary only supports one client for now.'
                ' The test used %d clients.', len(self._bb_tcp_clients)
            )
        for client in self._bb_tcp_clients[-1:]:
            server_client_id = client.ServerClientIdGet()
            method: HTTPRequestMethod = client.HttpMethodGet()
            try:
                result_history_client: HTTPResultHistory = client.ResultHistoryGet(
                )
                # Get interval result
                result_history_client.Refresh()
                # Cfr. HTTPResultDataList
                http_client_results: HTTPResultData = result_history_client.CumulativeLatestGet(
                )
                total_rx_client = http_client_results.RxByteCountTotalGet()
                total_tx_client = http_client_results.TxByteCountTotalGet()
                rx_first_client = datetime.fromtimestamp(
                    http_client_results.RxTimestampFirstGet() /
                    _SECONDS_PER_NANOSECOND
                )
                rx_last_client = datetime.fromtimestamp(
                    http_client_results.RxTimestampLastGet() /
                    _SECONDS_PER_NANOSECOND
                )
                tx_first_client = datetime.fromtimestamp(
                    http_client_results.TxTimestampFirstGet() /
                    _SECONDS_PER_NANOSECOND
                )
                tx_last_client = datetime.fromtimestamp(
                    http_client_results.TxTimestampLastGet() /
                    _SECONDS_PER_NANOSECOND
                )

                cumulative_results: Sequence[HTTPResultData] = \
                    result_history_client.CumulativeGet()
                # Take only the last snapshot (if one available)
                for result in cumulative_results[-1:]:
                    average_data_speed: DataRate = result.AverageDataSpeedGet()
                    value_data_speed = average_data_speed.ByteRateGet()
            except Exception as e:
                logging.warning("Couldn't get result in HttpAnalyser: %s", e)

            try:
                result_history_server: HTTPResultHistory = \
                    self._bb_tcp_server.ResultHistoryGet(server_client_id)
                result_history_server.Refresh()

                http_server_results: HTTPResultData = result_history_server.CumulativeLatestGet(
                )
                total_rx_server = http_server_results.RxByteCountTotalGet()
                total_tx_server = http_server_results.TxByteCountTotalGet()
                rx_first_server = datetime.fromtimestamp(
                    http_server_results.RxTimestampFirstGet() /
                    _SECONDS_PER_NANOSECOND
                )
                rx_last_server = datetime.fromtimestamp(
                    http_server_results.RxTimestampLastGet() /
                    _SECONDS_PER_NANOSECOND
                )
                tx_first_server = datetime.fromtimestamp(
                    http_server_results.TxTimestampFirstGet() /
                    _SECONDS_PER_NANOSECOND
                )
                tx_last_server = datetime.fromtimestamp(
                    http_server_results.TxTimestampLastGet() /
                    _SECONDS_PER_NANOSECOND
                )

            except Exception:
                logging.warning("Couldn't get result in HttpAnalyser")

        if method == HTTPRequestMethod.Get:
            self._http_data._http_method = "GET"
        elif method == HTTPRequestMethod.Put:
            self._http_data._http_method = "PUT"
        else:
            logging.warning(
                'HttpDataGatherer: Unsupported HTTP Method (%s).'
                ' Storing original value.', method
            )
            self._http_data._http_method = method

        self._http_data._avg_data_speed = value_data_speed
        # Set client results
        self._http_data._total_rx_client = total_rx_client
        self._http_data._total_tx_client = total_tx_client
        self._http_data._ts_rx_first_client = rx_first_client
        self._http_data._ts_rx_last_client = rx_last_client
        self._http_data._ts_tx_first_client = tx_first_client
        self._http_data._ts_tx_last_client = tx_last_client
        # Set server results
        self._http_data._total_rx_server = total_rx_server
        self._http_data._total_tx_server = total_tx_server
        self._http_data._ts_rx_first_server = rx_first_server
        self._http_data._ts_rx_last_server = rx_last_server
        self._http_data._ts_tx_first_server = tx_first_server
        self._http_data._ts_tx_last_server = tx_last_server
