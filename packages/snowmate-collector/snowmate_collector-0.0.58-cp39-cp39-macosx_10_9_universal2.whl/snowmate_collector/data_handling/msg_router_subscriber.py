from typing import Dict

from snowmate_collector.data_handling.interfaces import MessageHandler
from snowmate_collector.data_serialization.ipc_serializer import (
    IpcPickleSerializer,
    IpcSerializerBase,
)
from snowmate_collector.configs.collector_settings import log_debug


class MessageRouter(MessageHandler):
    """
    This class is responsible for routing messages to the relevant handler.
    It implements the MessageHandler interface.
    """

    def __init__(self, serializer: IpcSerializerBase = IpcPickleSerializer()) -> None:
        """
        This object routes a message to a handler according to its type.
        :param serializer: data serailizer, defaults to IpcPickleSerializer()
        :type serializer: IpcSerializerBase, optional
        """
        self.type_to_handler: Dict[MessageHandler] = {}
        self.serializer = serializer

    def add_message_handler(self, msg_type: type, handler: MessageHandler) -> None:
        """
        This function registers a handler for a given message type.
        :param msg_type: message type
        :type msg_type: type
        :param handler: message handler
        :type handler: MessageHandler
        """
        self.type_to_handler[msg_type] = handler

    def handle_message(self, msg: bytes) -> None:
        """
        This function deserializes an IPC message and sends the deserialized data to the relevant route.
        :param msg: serialized msg.
        :type msg: bytes.
        """
        try:
            loaded_msg = self.serializer.deserialize(msg)
            msg_handler = self.type_to_handler.get(type(loaded_msg))
            if msg_handler:
                msg_handler.handle_message(loaded_msg)
        except Exception as e:
            log_debug(f"[MessageRouter.handle_message] Exception: {e}")
            raise e

    def join(self):
        """
        This function waits for all the handlers to be done.
        """
        for _key, subscriber in self.type_to_handler.items():
            subscriber.join()
