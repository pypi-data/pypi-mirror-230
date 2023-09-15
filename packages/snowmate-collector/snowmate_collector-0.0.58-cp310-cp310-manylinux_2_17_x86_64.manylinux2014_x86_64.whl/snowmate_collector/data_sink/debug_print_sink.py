from snowmate_collector.data_sink.sink_base import SinkBase
from snowmate_collector.configs.collector_settings import CollectorSettings, log_debug


class StdoutSink(SinkBase):
    """
    Data sink that prints the data to stdout.
    """

    def __init__(self) -> None:
        self.auth_needed = False

    def export_data(self, msg):
        """
        This function prints a given message.
        :param msg: message to print.
        :type msg: Message
        """
        log_debug(f"[StdoutSink.export_data] message id: {id(msg)}")
        CollectorSettings.logger.log(
            CollectorSettings.log_level, f"message id: {id(msg)} - {msg}"
        )

    def configure_sink(self, **kwargs):
        """
        Used to match the SinkBase.
        """

    def join(self, *args, **kwargs):
        """
        Waits for the sink to be done
        """
