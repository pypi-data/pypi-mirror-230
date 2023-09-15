from abc import ABC, abstractmethod

from snowmate_collector.metrics import Metrics


class MetricsSinkBase(ABC):
    @abstractmethod
    def export_data(self, metrics_data: Metrics):
        """
        This function exports given metrics.
        :param metrics_data: metrics to export.
        :type metrics_data: Metrics
        """

    @abstractmethod
    def configure_sink(self, **sink_settings):
        """
        This function is used to add specific sink configurations after the sink was initted.
        """

    @abstractmethod
    def join(self, *args, **kwargs):
        """
        This function should wait for the sink clean up.
        """

    def is_auth_needed(self):
        return self.auth_needed
