from enum import Enum

from snowmate_collector.data_sink.metrics_sanity_sink import MetricsSanitySink
from snowmate_collector.data_sink.metrics_http_sink import MetricsHTTPSink
from snowmate_collector.data_sink.print_metrics_sink import MetricsStdoutSink
from snowmate_collector.data_sink.file_metrics_sink import MetricsFileStdoutSink


class MetricsDataSinks(Enum):
    """
    This is an enum containing all the available metrics sinks.
    """

    PRINT = MetricsStdoutSink()
    FILE = MetricsFileStdoutSink()
    SANITY = MetricsSanitySink()
    HTTP = MetricsHTTPSink()
