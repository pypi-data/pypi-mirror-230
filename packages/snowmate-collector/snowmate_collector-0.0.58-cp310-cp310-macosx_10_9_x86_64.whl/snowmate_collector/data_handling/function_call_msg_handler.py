from snowmate_collector.configs.collector_settings import CollectorSettings, log_debug
from snowmate_collector.data_collection.function_call_data import FunctionCall
from snowmate_collector.data_handling.interfaces import MessageHandler
from snowmate_collector.data_handling.msg_parsers.function_call_parser import (
    FunctionCallParser,
)


class FunctionCallMsgHandler(MessageHandler):
    """
    This class is responsible for handling function call messages.
    It implements the MessageHandler interface.
    """

    def __init__(
        self,
        msg_parser=FunctionCallParser(),
    ):
        """
        This handler parses and sends a function call message.
        :param msg_parser: the msg parser, defaults to FunctionCallParser()
        :type msg_parser: FunctionCallParser, optional
        """
        self.msg_parser = msg_parser

    def handle_message(self, msg: FunctionCall):
        """
        This function parses and exports a function call.
        :param msg: message.
        :type msg: FunctionCall
        """
        try:
            msg = self.msg_parser.parse(msg)
            CollectorSettings.data_sink.export_data(msg)
        except Exception as e:
            log_debug(f"[FunctionCallMsgHandler.handle_message] Exception: {e}")

    def join(self):
        """
        This function waits for the sink to be done.
        """
        CollectorSettings.data_sink.join()
