from snowmate_collector.configs.collector_settings import CollectorSettings
from snowmate_collector.data_handling.interfaces import MessageHandler
from snowmate_collector.metrics import Metrics, Metric

PENDING_MESSAGES_THRESHOLD: int = 50


class MetricsMsgHandler(MessageHandler):
    """
    This class is responsible for handling metrics messages.
    It implements the MessageHandler interface.
    """

    def __init__(self, metrics_sink):
        """
        This handler parses and sends a function call message.
        :param msg_parser: the msg parser
        :type msg_parser: Any
        """
        self.serializer = CollectorSettings.serializer
        self.msg_to_counters = {}
        self.pending_message = 0
        self.metrics_sink = metrics_sink

    def create_metrics_data(self) -> Metrics:
        """
        This function creates a Metrics object from the counters.
        :return: Metrics object.
        :rtype: Metrics
        """
        metrics = Metrics()
        for metric, counter in self.msg_to_counters.items():
            metrics.add_metric(
                Metric(
                    metric=metric,
                    counter=counter
                )
            )
        return metrics

    def send_counters(self):
        """
        This function sends the counters to the metrics sink.
        """
        metrics_data = self.create_metrics_data()
        self.metrics_sink.export_data(metrics_data)
        self.msg_to_counters = {}
        self.pending_message = 0

    def handle_message(self, msg):
        """
        This function parses and exports a metrics message.
        :param msg: message.
        :type msg: Any
        """
        try:
            loaded_msg = self.serializer.deserialize(msg)
            # If the metric is already in the dict, increment the counter.
            # Otherwise, add it to the dict.
            if loaded_msg in self.msg_to_counters:
                self.msg_to_counters[loaded_msg] += 1
            else:
                self.msg_to_counters[loaded_msg] = 1
            self.pending_message += 1
            # If we reached the threshold, send the counters.
            if self.pending_message == PENDING_MESSAGES_THRESHOLD:
                self.send_counters()
        except Exception:
            pass

    def get_timeout_method(self):
        """
        Returns the timeout method.
        """
        return self.timeout_handler

    def timeout_handler(self):
        """
        This function should be called when the timeout is reached.
        """
        self.send_counters()

    def join(self):
        """
        This function waits for the sink to be done.
        """
        try:
            self.send_counters()
            self.metrics_sink.join()
        except Exception:
            pass
