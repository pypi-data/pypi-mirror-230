from snowmate_collector.data_sink.metrics_sink_base import MetricsSinkBase
from snowmate_collector.metrics import Metrics

FILE_PATH = "/tmp/collector_metrics_output.txt"
FILE_MODE = "a+"


class MetricsFileStdoutSink(MetricsSinkBase):
    """
    Metrics sink that prints to stdout.
    """

    def __init__(self) -> None:
        self.auth_needed = False

    def is_auth_needed(self):
        return self.auth_needed

    def export_data(self, metrics_data: Metrics):
        """
        This function prints a given message.
        :param metrics_data: metrics to print.
        :type metrics_data: Metrics
        """
        # pylint: disable=unspecified-encoding
        with open(FILE_PATH, FILE_MODE) as output_file:
            for metric in metrics_data:
                # pylint: disable=protected-access
                output_file.write(f"{metric._metric}, count: {metric.counter}\n")

    def configure_sink(self, **kwargs):
        """
        Used to match the SinkBase.
        """

    def join(self, *args, **kwargs):
        """
        Waits for the sink to be done
        """
