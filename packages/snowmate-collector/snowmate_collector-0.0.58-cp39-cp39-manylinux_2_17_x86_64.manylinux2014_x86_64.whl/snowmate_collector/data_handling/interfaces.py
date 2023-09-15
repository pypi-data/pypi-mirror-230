from abc import ABC, abstractmethod


class SubProcessBase(ABC):
    @abstractmethod
    def spawn_subprocess(self):
        """
        This should spawn a new receiving process.
        """

    @abstractmethod
    def send_message(self, data: bytes):
        """
        This function should send a message to the subprocess.

        :param data: data to send
        :type data: bytes
        """

    @abstractmethod
    def join(self, timeout: int = None) -> bool:
        """
        This function should wait for the subprocess to be done.
        :param timeout: timeout in seconds. None indicates waiting forever.
        :type timeout: int | None
        :return: True if the subprocess joined gracefully, False otherwise.
        :rtype: bool
        """


class MessageHandler(ABC):
    @abstractmethod
    def handle_message(self, msg: bytes):
        """
        This should handle a message.
        :param msg: message to handle.
        :type msg: bytes.
        """

    def get_timeout_method(self):
        return None
