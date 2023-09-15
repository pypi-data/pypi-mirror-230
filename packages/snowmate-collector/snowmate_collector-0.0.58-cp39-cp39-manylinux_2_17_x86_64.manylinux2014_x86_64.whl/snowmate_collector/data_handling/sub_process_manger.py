import threading

from snowmate_collector.data_handling.interfaces import MessageHandler, SubProcessBase


class SubProcessEnum:
    """
    This is an enum class for the different types of subprocesses.
    """

    DATA = 0
    METRICS = 1


class SubProcessSingleton:
    """
    This object wraps the subprocess, and spawns it on the first send_message.
    """

    def __init__(self, subprocess_obj: SubProcessBase) -> None:
        """
        Create the subprocess singleton in the sender process.
        :param subprocess_obj: the subprocess object.
        :type subprocess_obj: SubProcessBase
        """
        self.mutex = threading.Lock()
        self.subprocess_obj = subprocess_obj
        self.pid = 0
        self.initted = False

    def send_message(self, data: bytes) -> None:
        """
        This function sends a message to the worker subprocess.
        If the subprocess is not initialized, it will be initialized (should happen only once).
        :param data: message data
        :type data: bytes
        """
        with self.mutex:
            if not self.initted:
                self.subprocess_obj.spawn_subprocess()
                self.pid = self.subprocess_obj.pid
                self.initted = True
        self.subprocess_obj.send_message(data)

    def join(self, timeout: int = None) -> bool:
        """
        This function waits for the subprocess to finish.
        """
        return self.subprocess_obj.join(timeout=timeout)

    def add_subscriber(self, handler: MessageHandler) -> None:
        """
        This function adds a message handler to the subprocess.
        :param handler: message handler.
        :type handler: MessageHandler
        """
        self.subprocess_obj.add_subscriber(handler)
