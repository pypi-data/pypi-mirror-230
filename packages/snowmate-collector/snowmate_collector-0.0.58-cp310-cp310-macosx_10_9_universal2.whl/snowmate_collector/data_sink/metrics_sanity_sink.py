from snowmate_collector.configs.collector_settings import CollectorSettings
from snowmate_collector.consts import logs as logs_consts
from snowmate_collector.data_collection.metrics import (
    CollectorFailure,
    ExternalFunction
)
from snowmate_collector.data_sink.metrics_http_sink import MetricsHTTPSink
from snowmate_collector.metrics import Metrics

TESTS_DATA_METRIC_TYPES = (CollectorFailure, ExternalFunction)


class MetricsSanitySink(MetricsHTTPSink):
    """
    Metrics sink that sends data via http once for sanity.
    """

    def __init__(self) -> None:
        self.were_tests_metrics_collected = False
        self.were_general_metrics_collected = False
        super().__init__()

    def is_auth_needed(self):
        return self.auth_needed

    def export_data(self, metrics_data: Metrics):
        """
        This function adds the metrics it receives to the request queue.
        :param metrics_data: metrics data.
        :type metrics_data: Metrics
        """
        super().export_data(metrics_data)

        self._log_once(metrics_data)

    def _log_once(self, msg: Metrics):
        """
        Log once only for a test failure metric and for a general metric
        :param msg: metrics data.
        :type msg: Metrics
        """
        for metric in msg:
            if metric.metric_type in TESTS_DATA_METRIC_TYPES:
                if not self.were_tests_metrics_collected:
                    CollectorSettings.logger.log(
                        CollectorSettings.log_level,
                        logs_consts.TESTS_METRICS_WERE_COLLECTED_SUCCESSFULLY,
                    )
                    self.were_tests_metrics_collected = True
            else:
                if not self.were_general_metrics_collected:
                    CollectorSettings.logger.log(
                        CollectorSettings.log_level,
                        logs_consts.GENERAL_METRICS_WERE_COLLECTED_SUCCESSFULLY,
                    )
                    self.were_general_metrics_collected = True
