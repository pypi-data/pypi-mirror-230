from snowmate_collector.data_sink.sink_base import SinkBase

FILE_PATH = "/tmp/collector_tests_output.txt"
FILE_MODE = "a+"


class FileStdoutSink(SinkBase):
    """
    Data sink that saves the output to a file.
    """

    def __init__(self) -> None:
        self.auth_needed = False

    def export_data(self, msg):
        """
        This function prints a given message.
        :param msg: message to print.
        :type msg: Message
        """
        # pylint: disable=unspecified-encoding
        with open(FILE_PATH, FILE_MODE) as output_file:
            output_file.write(f"{msg}\n")

    def configure_sink(self, **kwargs):
        """
        Used to match the SinkBase.
        """

    def join(self, *args, **kwargs):
        """
        Waits for the sink to be done
        """
