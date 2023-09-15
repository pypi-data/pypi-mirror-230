from enum import Enum

from snowmate_collector.data_sink.debug_print_sink import StdoutSink
from snowmate_collector.data_sink.debug_file_sink import FileStdoutSink
from snowmate_collector.data_sink.debug_none_sink import StdoutNoneSink
from snowmate_collector.data_sink.http_sink import HTTPSink
from snowmate_collector.data_sink.sanity_sink import SanitySink


class DataSinks(Enum):
    """
    This is an enum containing all the available data sinks.
    """

    PRINT = StdoutSink()
    FILE = FileStdoutSink()
    NONE = StdoutNoneSink()
    SANITY = SanitySink()
    HTTP = HTTPSink()
