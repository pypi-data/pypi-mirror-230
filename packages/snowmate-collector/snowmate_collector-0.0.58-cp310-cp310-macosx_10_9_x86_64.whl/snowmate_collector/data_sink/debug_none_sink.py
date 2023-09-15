from snowmate_collector.data_sink.sink_base import SinkBase


class StdoutNoneSink(SinkBase):
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
        # pylint: disable=unnecessary-pass
        pass

    def configure_sink(self, **kwargs):
        """
        Used to match the SinkBase.
        """

    def join(self, *args, **kwargs):
        """
        Waits for the sink to be done
        """
