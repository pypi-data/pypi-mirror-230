from snowmate_common.messages_data.messages import TestCase

from snowmate_collector.configs.collector_settings import CollectorSettings
from snowmate_collector.consts import logs as logs_consts
from snowmate_collector.data_sink.http_sink import HTTPSink

_MAX_FUNCTIONS_TO_SHOW_IN_SUMMARY = 5


class SanitySink(HTTPSink):
    """
    Data sink that sends data via http once for sanity.
    """

    def __init__(self) -> None:
        self.did_collected_test_data = False
        super().__init__()

    def export_data(self, msg):
        """
        This function prints a given message.
        :param msg: message to print.
        :type msg: Message
        """
        if not self.did_collected_test_data:
            if isinstance(msg, TestCase):
                CollectorSettings.logger.log(
                    CollectorSettings.log_level,
                    logs_consts.TESTS_DATA_WAS_COLLECTED_SUCCESSFULLY,
                )
                # Send one test data only, as a sanity check.
                super().export_data(msg)
                self.did_collected_test_data = True
