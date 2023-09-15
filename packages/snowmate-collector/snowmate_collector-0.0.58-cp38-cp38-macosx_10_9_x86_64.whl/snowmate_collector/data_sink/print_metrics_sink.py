from snowmate_collector.configs.collector_settings import CollectorSettings
from snowmate_collector.data_sink.metrics_sink_base import MetricsSinkBase
from snowmate_collector.metrics import Metrics


class MetricsStdoutSink(MetricsSinkBase):
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
        for metric in metrics_data:
            CollectorSettings.logger.log(
                CollectorSettings.log_level,
                f"{metric._metric}, count: {metric.counter}",  # pylint: disable=protected-access
            )

    def configure_sink(self, **kwargs):
        """
        Used to match the SinkBase.
        """

    def join(self, *args, **kwargs):
        """
        Waits for the sink to be done
        """
