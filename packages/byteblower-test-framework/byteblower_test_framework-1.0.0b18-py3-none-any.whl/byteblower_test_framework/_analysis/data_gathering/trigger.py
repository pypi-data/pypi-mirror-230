import logging
from abc import ABC, abstractmethod
from typing import Sequence  # for type hinting

import pandas
from byteblowerll.byteblower import (  # for type hinting
    FrameTagTx,
    LatencyBasic,
    LatencyBasicResultData,
    LatencyBasicResultHistory,
    LatencyBasicResultSnapshot,
    LatencyDistribution,
    LatencyDistributionResultSnapshot,
    StreamResultData,
    StreamResultHistory,
    TriggerBasic,
    TriggerBasicResultData,
    TriggerBasicResultHistory,
    VLANTag,
)

from ..._endpoint.ipv4.port import IPv4Port
from ..._endpoint.ipv6.port import IPv6Port
from ..._traffic.frame import VLAN_HEADER_LENGTH
from ..._traffic.frameblastingflow import FrameBlastingFlow  # for type hinting
from ..storage.frame_count import FrameCountData
from ..storage.trigger import LatencyData, LatencyDistributionData
from .data_gatherer import DataGatherer


class _GenericFilterBuilder(object):

    __slots__ = ()

    @staticmethod
    def _vlan_id(flow: FrameBlastingFlow) -> Sequence[int]:
        destination_port = flow.destination
        layer2_5 = destination_port.layer2_5
        for l2_5 in layer2_5:
            if not isinstance(l2_5, VLANTag):
                logging.warning(
                    'Flow Analyser %r:'
                    ' Unsupported Layer 2.5 configuration: %r', flow.name,
                    type(l2_5)
                )
            yield l2_5.IDGet()

    @staticmethod
    def _build_layer2_5_filter(flow: FrameBlastingFlow) -> str:
        # Quick filter without VLAN ID:
        # l2_5_filter = 'vlan and ' * len(destination_port.layer2_5)
        l2_5_filter = ' and '.join(
            (
                f'vlan {vlan_id}'
                for vlan_id in _GenericFilterBuilder._vlan_id(flow)
            )
        )
        if l2_5_filter:
            return l2_5_filter + ' and '
        return l2_5_filter

    @staticmethod
    def build_bpf_filter(
        flow: FrameBlastingFlow, src_udp: int, dest_udp: int
    ) -> str:
        source_port = flow.source
        destination_port = flow.destination
        l2_5_filter = _GenericFilterBuilder._build_layer2_5_filter(flow)
        if isinstance(source_port, IPv6Port) and isinstance(destination_port,
                                                            IPv6Port):
            dest_ip = str(destination_port.ip)
            src_ip = str(source_port.ip)
            return f'{l2_5_filter}ip6 dst {dest_ip} and ip6 src {src_ip}' \
                f' and udp dst port {dest_udp} and udp src port {src_udp}'
        if isinstance(source_port, IPv4Port) and isinstance(destination_port,
                                                            IPv4Port):
            # NOTE: Also includes NattedPort (extends from IPv4Port)
            dest_ip = str(destination_port.ip)
            if source_port.is_natted:
                # Source IP and UDP are private
                logging.debug(
                    'Resolving NAT: %r (%r) -> %r (%r)', source_port.name,
                    src_udp, destination_port.name, dest_udp
                )
                nat_info = source_port.nat_discover(
                    destination_port,
                    public_udp_port=dest_udp,
                    nat_udp_port=src_udp
                )
                logging.debug('NAT translation: %r', nat_info)
                # Public source IP address and UDP port
                src_ip, src_udp = nat_info
            else:
                src_ip = str(source_port.ip)
            return f'{l2_5_filter}ip dst {dest_ip} and ip src {src_ip}' \
                f' and udp dst port {dest_udp} and udp src port {src_udp}'
        raise ValueError(
            'FrameLossAnalyser: Cannot create BPF filter for Flow {flow}'
            ': Unsupported Port type: Source: {src_name} > {src_type}'
            ' | destination: {dest_name} > {dest_type}'.format(
                flow=flow.name,
                src_name=source_port.name,
                src_type=type(source_port),
                dest_name=destination_port.name,
                dest_type=type(destination_port)
            )
        )


class FilterBuilder(ABC):

    __slots__ = ()

    # FIXME - This probably won't work
    #       * since abstract methods are only check
    #       * at object instanciation.
    @staticmethod
    @abstractmethod
    def build_bpf_filter(flow: FrameBlastingFlow) -> str:
        raise NotImplementedError(
            'Abstract method: FilterBuilder.build_bpf_filter'
        )


class FrameFilterBuilder(object):

    __slots__ = ()

    @staticmethod
    def build_bpf_filter(flow: FrameBlastingFlow) -> str:
        src_dest_udp_set = {
            (source_frame.udp_src, source_frame.udp_dest)
            for source_frame in flow._frame_list
        }
        # TODO - Support for multiple UDP src/dest combinations
        #        with multiple frames
        if len(src_dest_udp_set) < 1:
            logging.warning(
                'Frame loss analyser: Flow %r: No frames configured?'
                ' Cannot analyze this Flow.', flow.name
            )
            src_dest_udp_set = set((0, 0))
        elif len(src_dest_udp_set) > 1:
            logging.warning(
                'Frame loss analyser: Flow %r: Multiple UDP source/destination'
                ' port combinations is not yet supported.'
                ' You may expect reported loss.', flow.name
            )
        src_dest_udp = next(iter(src_dest_udp_set))
        return _GenericFilterBuilder.build_bpf_filter(
            flow, src_dest_udp[0], src_dest_udp[1]
        )


class ImixFilterBuilder(object):

    __slots__ = ()

    @staticmethod
    def build_bpf_filter(flow: FrameBlastingFlow) -> str:
        src_dest_udp_set = {
            (source_frame.udp_src, source_frame.udp_dest)
            for source_frame in flow._frame_list
        }
        # TODO - Support for multiple UDP src/dest combinations
        if len(src_dest_udp_set) < 1:
            logging.warning(
                'Frame loss analyser: Flow %r: No frames IMIX configured?'
                ' Cannot analyze this Flow.', flow.name
            )
            src_dest_udp_set = set((0, 0))
        elif len(src_dest_udp_set) > 1:
            logging.warning(
                'Frame loss analyser: Flow %r: Multiple UDP source/destination'
                ' port combinations in IMIX is not yet supported.'
                ' You may expect reported loss.', flow.name
            )
        src_dest_udp = next(iter(src_dest_udp_set))
        return _GenericFilterBuilder.build_bpf_filter(
            flow, src_dest_udp[0], src_dest_udp[1]
        )


class BaseFrameCountDataGatherer(DataGatherer):

    __slots__ = (
        '_framecount_data',
        '_flow',
        '_trigger',
        '_rx_vlan_header_size',
        '_rx_result',
    )

    def __init__(
        self, framecount_data: FrameCountData, flow: FrameBlastingFlow
    ) -> None:
        super().__init__()
        self._framecount_data = framecount_data
        self._flow = flow
        self._trigger: TriggerBasic = \
            self._flow.destination.bb_port.RxTriggerBasicAdd()
        self._rx_vlan_header_size: int = 0
        self._rx_result: TriggerBasicResultHistory = \
            self._trigger.ResultHistoryGet()

    def prepare(self) -> None:
        bpf_filter = self._FILTER_BUILDER.build_bpf_filter(self._flow)
        logging.debug(
            'Flow: %r: Setting BPF filter to %r', self._flow.name, bpf_filter
        )
        self._trigger.FilterSet(bpf_filter)
        self._trigger.ResultClear()
        self._rx_result.Clear()
        # NOTE: We calculate the VLAN header sizes at start of the Flow,
        #       since this is the point where the filter was created.
        # TODO: For TX, it should actually be done when creating the Frame
        #       * objects (setting frame content) at ByteBlower API/Server.
        destination_vlan_config = list(self._flow.destination.vlan_config)
        self._rx_vlan_header_size = len(
            destination_vlan_config
        ) * VLAN_HEADER_LENGTH

    def updatestats(self) -> None:
        self._rx_result.Refresh()

        # Add all the results
        result_cumul: TriggerBasicResultData = None  # for type hinting
        for result_cumul in self._rx_result.CumulativeGet()[:-1]:
            try:
                ts_ns: int = result_cumul.TimestampGet()
                result_interval: TriggerBasicResultData = \
                    self._rx_result.IntervalGetByTime(ts_ns)
                ts = pandas.to_datetime(ts_ns)
                self._framecount_data._over_time.loc[ts] = [
                    result_cumul.IntervalDurationGet(),
                    result_cumul.PacketCountGet(),
                    result_cumul.ByteCountGet(),
                    result_interval.IntervalDurationGet(),
                    result_interval.PacketCountGet(),
                    result_interval.ByteCountGet(),
                ]
            except Exception:
                logging.warning(
                    "Something went wrong during processing of RX stats.",
                    exc_info=True
                )

        # Clear the history
        self._rx_result.Clear()

    def summarize(self) -> None:
        self._rx_result.Refresh()

        rx: TriggerBasicResultData = self._rx_result.CumulativeLatestGet()
        total_rx_bytes = rx.ByteCountGet()
        total_rx_packets = rx.PacketCountGet()
        if total_rx_packets:
            ts_rx_first_ns = rx.TimestampFirstGet()
            ts_rx_last_ns = rx.TimestampLastGet()
        else:
            ts_rx_first_ns = None
            ts_rx_last_ns = None

        self._framecount_data._total_bytes = total_rx_bytes
        self._framecount_data._total_vlan_bytes = \
            total_rx_packets * self._rx_vlan_header_size
        self._framecount_data._total_packets = total_rx_packets
        self._framecount_data._timestamp_first = \
            pandas.to_datetime(ts_rx_first_ns)
        self._framecount_data._timestamp_last = \
            pandas.to_datetime(ts_rx_last_ns)


class FrameCountDataGatherer(BaseFrameCountDataGatherer):

    _FILTER_BUILDER = FrameFilterBuilder


class ImixCountDataGatherer(BaseFrameCountDataGatherer):

    _FILTER_BUILDER = ImixFilterBuilder


class BaseLatencyFrameCountDataGatherer(DataGatherer):

    __slots__ = (
        '_framecount_data',
        '_latency_data',
        '_flow',
        '_trigger',
        '_rx_vlan_header_size',
        '_rx_result',
    )

    def __init__(
        self, framecount_data: FrameCountData, latency_data: LatencyData,
        flow: FrameBlastingFlow
    ) -> None:
        super().__init__()
        self._framecount_data = framecount_data
        self._latency_data = latency_data
        self._flow = flow
        self._trigger: LatencyBasic = \
            self._flow.destination.bb_port.RxLatencyBasicAdd()
        self._rx_vlan_header_size: int = 0
        self._rx_result: LatencyBasicResultHistory = \
            self._trigger.ResultHistoryGet()

    def prepare(self) -> None:
        bpf_filter = self._FILTER_BUILDER.build_bpf_filter(self._flow)
        logging.debug(
            'Flow: %r: Setting BPF filter to %r', self._flow.name, bpf_filter
        )
        self._trigger.FilterSet(bpf_filter)
        # Set the time tag format and metrics
        # NOTE - Using the first frame
        #      - All frames are generated on the same server,
        #        so they should have the same format.
        #      - All frames "should have" been generated the same way,
        #        using the same tags, so should have the same metrics too.
        # TODO - We should do some sanity check on all Frames
        #      * whether the format and metrics are identical.
        frame_list = self._flow._frame_list
        if len(frame_list) > 0:
            first_bb_frame = frame_list[0]._frame
            tx_frame_tag: FrameTagTx = first_bb_frame.FrameTagTimeGet()
            self._trigger.FrameTagSet(tx_frame_tag)
        self._trigger.ResultClear()
        self._rx_result.Clear()
        # NOTE: We calculate the VLAN header sizes at start of the Flow,
        #       since this is the point where the filter was created.
        # TODO: For TX, it should actually be done when creating the Frame
        #       * objects (setting frame content) at ByteBlower API/Server.
        destination_vlan_config = list(self._flow.destination.vlan_config)
        self._rx_vlan_header_size = len(
            destination_vlan_config
        ) * VLAN_HEADER_LENGTH

    def updatestats(self) -> None:
        self._rx_result.Refresh()
        # Add all the results
        result_cumul: LatencyBasicResultData
        for result_cumul in self._rx_result.CumulativeGet()[:-1]:
            try:
                result_interval: LatencyBasicResultData = \
                    self._rx_result.IntervalGetByTime(
                    result_cumul.TimestampGet()
                )

                if not result_interval.PacketCountGet():
                    continue

                ts = pandas.to_datetime(result_cumul.TimestampGet())
                self._framecount_data.over_time.loc[ts] = [
                    result_cumul.IntervalDurationGet(),
                    result_cumul.PacketCountGet(),
                    result_cumul.ByteCountGet(),
                    result_interval.IntervalDurationGet(),
                    result_interval.PacketCountGet(),
                    result_interval.ByteCountGet(),
                ]
                if result_interval.PacketCountGet():
                    # NOTE - If we did not receive any data,
                    #        we will not have latency values.
                    self._latency_data.df_latency.loc[ts] = [
                        result_interval.LatencyMinimumGet() / 1000000,
                        result_interval.LatencyMaximumGet() / 1000000,
                        result_interval.LatencyAverageGet() / 1000000,
                        result_interval.JitterGet() / 1000000,
                    ]
            except Exception:
                logging.warning(
                    "Something went wrong during processing of RX stats.",
                    exc_info=True
                )
        # Clear the history
        self._rx_result.Clear()

    def summarize(self) -> None:
        self._rx_result.Refresh()

        rx: LatencyBasicResultSnapshot = self._rx_result.CumulativeLatestGet()
        total_rx_bytes = rx.ByteCountGet()
        total_rx_packets = rx.PacketCountGet()
        if total_rx_packets:
            ts_rx_first_ns = rx.TimestampFirstGet()
            ts_rx_last_ns = rx.TimestampLastGet()
        else:
            ts_rx_first_ns = None
            ts_rx_last_ns = None

        self._framecount_data._total_bytes = total_rx_bytes
        self._framecount_data._total_vlan_bytes = \
            total_rx_packets * self._rx_vlan_header_size
        self._framecount_data._total_packets = total_rx_packets
        self._framecount_data._timestamp_first = \
            pandas.to_datetime(ts_rx_first_ns)
        self._framecount_data._timestamp_last = \
            pandas.to_datetime(ts_rx_last_ns)

        final_packet_count_valid = rx.PacketCountValidGet()
        self._latency_data._final_packet_count_valid = \
            final_packet_count_valid
        self._latency_data._final_packet_count_invalid = \
            rx.PacketCountInvalidGet()
        if final_packet_count_valid:
            # NOTE - If we did not receive any data (with valid latency tag),
            #        we will not have latency values.
            self._latency_data._final_min_latency = \
                rx.LatencyMinimumGet() / 1000000
            self._latency_data._final_max_latency = \
                rx.LatencyMaximumGet() / 1000000
            self._latency_data._final_avg_latency = \
                rx.LatencyAverageGet() / 1000000
            self._latency_data._final_avg_jitter = \
                rx.JitterGet() / 1000000


class LatencyFrameCountDataGatherer(BaseLatencyFrameCountDataGatherer):

    _FILTER_BUILDER = FrameFilterBuilder


class LatencyImixCountDataGatherer(BaseLatencyFrameCountDataGatherer):

    _FILTER_BUILDER = ImixFilterBuilder


class BaseLatencyCDFFrameCountDataGatherer(DataGatherer):
    """Data gathering for latency CDF and frame count."""

    __slots__ = (
        '_framecount_data',
        '_latency_distribution_data',
        '_flow',
        '_trigger',
        '_rx_vlan_header_size',
    )

    def __init__(
        self, framecount_data: FrameCountData,
        latency_distribution_data: LatencyDistributionData,
        max_threshold_latency: float, flow: FrameBlastingFlow
    ) -> None:
        super().__init__()
        self._framecount_data = framecount_data
        self._latency_distribution_data = latency_distribution_data
        self._flow = flow
        self._trigger: LatencyDistribution = \
            self._flow.destination.bb_port.RxLatencyDistributionAdd()
        self._trigger.RangeSet(0, int(50 * max_threshold_latency * 1000000))
        self._rx_vlan_header_size: int = 0

    def prepare(self) -> None:
        bpf_filter = self._FILTER_BUILDER.build_bpf_filter(self._flow)
        logging.debug(
            'Flow: %r: Setting BPF filter to %r', self._flow.name, bpf_filter
        )
        self._trigger.FilterSet(bpf_filter)
        # Set the time tag format and metrics
        # NOTE - Using the first frame
        #      - All frames are generated on the same server,
        #        so they should have the same format.
        #      - All frames "should have" been generated the same way,
        #        using the same tags, so should have the same metrics too.
        # TODO - We should do some sanity check on all Frames
        #      * whether the format and metrics are identical.
        frame_list = self._flow._frame_list
        if len(frame_list) > 0:
            first_bb_frame = frame_list[0]._frame
            tx_frame_tag: FrameTagTx = first_bb_frame.FrameTagTimeGet()
            self._trigger.FrameTagSet(tx_frame_tag)
        self._trigger.ResultClear()
        self._flow._stream.ResultClear()
        # NOTE: We calculate the VLAN header sizes at start of the Flow,
        #       since this is the point where the filter was created.
        # TODO: For TX, it should actually be done when creating the Frame
        #       * objects (setting frame content) at ByteBlower API/Server.
        destination_vlan_config = list(self._flow.destination.vlan_config)
        self._rx_vlan_header_size = len(
            destination_vlan_config
        ) * VLAN_HEADER_LENGTH

    def summarize(self) -> None:
        self._trigger.Refresh()
        self._flow._stream.Refresh()

        rx: LatencyDistributionResultSnapshot = self._trigger.ResultGet()
        total_rx_bytes = rx.ByteCountGet()
        total_rx_packets = rx.PacketCountGet()
        if total_rx_packets:
            ts_rx_first_ns = rx.TimestampFirstGet()
            ts_rx_last_ns = rx.TimestampLastGet()
        else:
            ts_rx_first_ns = None
            ts_rx_last_ns = None

        # Frame count analysis
        self._framecount_data._total_bytes = total_rx_bytes
        self._framecount_data._total_vlan_bytes = \
            total_rx_packets * self._rx_vlan_header_size
        # TODO - Do we need the "valid" packet count here ?
        #      ? Where does ``ByteCountGet()`` relate to ?
        self._framecount_data._total_packets = total_rx_packets
        self._framecount_data._timestamp_first = \
            pandas.to_datetime(ts_rx_first_ns)
        self._framecount_data._timestamp_last = \
            pandas.to_datetime(ts_rx_last_ns)

        # Latency (distribution) analysis
        final_packet_count_valid = rx.PacketCountValidGet()
        self._latency_distribution_data._final_packet_count_valid = \
            final_packet_count_valid
        self._latency_distribution_data._final_packet_count_invalid = \
            rx.PacketCountInvalidGet()
        self._latency_distribution_data._final_packet_count_below_min = \
            rx.PacketCountBelowMinimumGet()
        self._latency_distribution_data._final_packet_count_above_max = \
            rx.PacketCountAboveMaximumGet()
        if final_packet_count_valid:
            # NOTE - If we did not receive any data (with valid latency tag),
            #        we will not have latency values.
            self._latency_distribution_data._final_min_latency = \
                rx.LatencyMinimumGet() / 1000000
            self._latency_distribution_data._final_max_latency = \
                rx.LatencyMaximumGet() / 1000000
            self._latency_distribution_data._final_avg_latency = \
                rx.LatencyAverageGet() / 1000000
            self._latency_distribution_data._final_avg_jitter = \
                rx.JitterGet() / 1000000

        bucket_count = rx.BucketCountGet()
        packet_count_buckets: Sequence[int] = rx.PacketCountBucketsGet()
        logging.debug(
            'Flow: %r: Got %r Packet count buckets', self._flow.name,
            bucket_count
        )
        # XXX - Not sure if we can directly use ``packet_count_buckets``.
        self._latency_distribution_data._packet_count_buckets = [
            packet_count_buckets[x] for x in range(0, bucket_count)
        ]
        self._latency_distribution_data._bucket_width = rx.BucketWidthGet()


class LatencyCDFFrameCountDataGatherer(BaseLatencyCDFFrameCountDataGatherer):

    _FILTER_BUILDER = FrameFilterBuilder


class LatencyCDFImixCountDataGatherer(BaseLatencyCDFFrameCountDataGatherer):

    _FILTER_BUILDER = ImixFilterBuilder
