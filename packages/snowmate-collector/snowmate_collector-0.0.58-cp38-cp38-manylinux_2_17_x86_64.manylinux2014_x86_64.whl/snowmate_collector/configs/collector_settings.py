import logging
import sys
from os import getpid
from threading import current_thread
from datetime import datetime
from typing import Dict, List, TextIO

from snowmate_collector.consts.logs import LOGGER_NAME, DEBUG_LOGGER_NAME
from snowmate_collector.data_handling.interfaces import SubProcessBase
from snowmate_collector.data_serialization.ipc_serializer_base import IpcSerializerBase
from snowmate_collector.data_sink.metrics_sink_base import MetricsSinkBase
from snowmate_collector.data_sink.sink_base import SinkBase


def get_logger(
    name: str,
    format_string: str = "Snowmate - %(levelname)s - %(message)s",
    stream: TextIO = sys.stderr,
) -> logging.Logger:
    logger_obj = logging.getLogger(name)
    formatter = logging.Formatter(format_string)
    console_handler = logging.StreamHandler(stream=stream)
    console_handler.setFormatter(formatter)
    logger_obj.addHandler(console_handler)
    return logger_obj


def get_debug_logger(
    name: str = DEBUG_LOGGER_NAME,
    format_string: str = "Snowmate - %(levelname)s - %(message)s",
    stream: TextIO = sys.stderr,
) -> logging.Logger:
    l = get_logger(name, format_string, stream)
    l.setLevel(logging.DEBUG)
    return l


def log_debug(msg: str):
    if CollectorSettings.debug_logger:
        CollectorSettings.debug_logger.log(
            logging.DEBUG,
            f"[{datetime.now()}] pid: {getpid()}, tid: {current_thread().ident}, msg: {msg}",
        )


logger = get_logger(LOGGER_NAME)


class CollectorSettings:
    project_path: str = None
    project_id: str = None
    lib_version: str = ""
    python_version: str = ""
    project_files: List[str] = []
    modules_for_recording: Dict[str, bool] = {}
    serializer: IpcSerializerBase = None
    data_sink: SinkBase = None
    data_subprocess: SubProcessBase = None
    metrics_subprocess: SubProcessBase = None
    tenant_id: str = ""
    log_level: int = logging.WARNING
    logger: logging.Logger = logger
    debug_logger: logging.Logger = None
    atexit_registered = False
    should_obfuscate_data: bool = True
    sanity: bool = False
    metrics_sink: MetricsSinkBase = None
