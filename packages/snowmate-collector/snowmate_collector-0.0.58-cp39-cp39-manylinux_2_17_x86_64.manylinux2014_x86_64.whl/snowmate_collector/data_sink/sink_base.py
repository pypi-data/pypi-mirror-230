from abc import ABC, abstractmethod

from typing import Any


class SinkBase(ABC):
    @abstractmethod
    def export_data(self, msg: Any):
        """
        This function exports a given message.
        :param msg: message to export.
        :type msg: Any
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
