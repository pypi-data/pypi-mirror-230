import atexit
import logging
import os
import platform
import signal
import sys
import threading
import time
from pathlib import Path
from typing import List, Optional, Set
from functools import reduce
from gitignore_parser import parse_gitignore

try:
    from importlib.metadata import version as get_version
except ImportError:  # for Python<3.8
    from importlib_metadata import version as get_version

from snowmate_common.auth.authorizer import AuthError, Authorizer, BAD_REQUEST
from snowmate_common.utils.projects import get_project_settings

import snowmate_collector.interceptor
from snowmate_collector.configs.collector_settings import (
    CollectorSettings,
    get_debug_logger,
    log_debug,
)
from snowmate_collector.consts import api_consts
from snowmate_collector.consts import logs as logs_consts
from snowmate_collector.data_collection.metrics import (
    ExitEvent,
    SamplingRateWasSet,
    ExternalCallsMaxLimitWasSet,
    StartEvent,
)
from snowmate_collector.data_handling.zmq_ipc import (
    set_data_process,
    set_metrics_process,
)
from snowmate_collector.data_serialization.ipc_serializer import IpcPickleSerializer
from snowmate_collector.data_sink.metrics_sink_enum import (
    MetricsDataSinks,
    MetricsSanitySink,
)
from snowmate_collector.data_sink.sanity_sink import SanitySink
from snowmate_collector.data_sink.sink_base import SinkBase
from snowmate_collector.data_sink.sink_enum import DataSinks
from snowmate_collector.exceptions import ProjectDoesNotExistException
from snowmate_collector.data_handling.interfaces import SubProcessBase

VIRTUAL_ENV = "VIRTUAL_ENV"
SNOWMATE_COLLECTOR_LIB_NAME = "snowmate_collector"
COLLECTOR_SAMPLING_RATE = "collectorSamplingRate"
DEFAULT_SAMPLING_RATE = 0.01
COLLECTOR_MAX_FUNCTION_EXTERNAL_CALLS = "collectorMaxFunctionExternalCalls"
DEFAULT_MAX_FUNCTION_EXTERNAL_CALLS = 100

DEBUG_LOGGING_ENABLED = False


def is_path_in_parent(parent_path: str, child_path: str) -> bool:
    """
    This function checks if child_path is in parent path.
    :param parent_path: parent path
    :type parent_path: str
    :param child_path: child path
    :type child_path: str
    :return: true if child_path is in parent_path.
    :rtype: bool
    """
    parent_path = os.path.abspath(parent_path)
    child_path = os.path.abspath(child_path)

    return os.path.commonpath([parent_path]) == os.path.commonpath(
        [parent_path, child_path]
    )


def _is_user_using_tracer() -> bool:
    """
    Currently, Snowmate's Collector does not run on debug mode.
    We check if the user use pydevd tracer
    """
    tracer = sys.gettrace()

    has_tracer = (
        tracer is not None
        and hasattr(tracer, "__module__")
        and "_pydevd_" in tracer.__module__
    )
    if has_tracer:
        CollectorSettings.logger.log(
            CollectorSettings.log_level, logs_consts.DEBUG_MODE
        )
    return has_tracer


def is_test_file(directory_path: str, filename: str) -> bool:
    """
    This function decided if a given file is a test file.

    :param directory_path: directory path.
    :type directory_path: str
    :param filename: filename.
    :type filename: str
    :return: true if it's a test file ,false if it's not.
    :rtype: bool
    """
    return "tests" in Path(directory_path).parts and filename.startswith("test")


def filter_venv(project_files: List[str], project_path: str) -> List[str]:
    """
    This function filters out .venv file from the project files.

    :param project_files: List of the project directory files.s
    :type project_files: List[str]
    :param project_path: project path.
    :type project_path: str
    :return: filtered project files.
    :rtype: List[str]
    """
    if VIRTUAL_ENV in os.environ:
        venv_dir = os.environ[VIRTUAL_ENV]
        if not is_path_in_parent(venv_dir, project_path):
            project_files = list(
                filter(
                    lambda file_path: not is_path_in_parent(venv_dir, file_path),
                    project_files,
                )
            )
    return project_files


def filter_snowmateignore(
    project_files: List[str],
    project_path: str,
    snowmateignore_relative_path: Optional[str] = ".snowmateignore",
) -> List[str]:
    """
    This function filters out files declared in .snowignore from the project files.

    :param project_files: List of the project directory files.
    :type project_files: List[str]
    :param project_path: project path.
    :type project_path: str
    :param snowmateignore_relative_path: .snowmateignore path (relative to project_path).
    :type snowmateignore_relative_path: Optional[str]
    :return: filtered project files.
    :rtype: List[str]
    """
    snowmateignore_full_path = os.path.join(project_path, snowmateignore_relative_path)
    if os.path.exists(snowmateignore_full_path):
        try:
            matches = parse_gitignore(snowmateignore_full_path)
            project_files = list(
                filter(
                    lambda file_path: not matches(file_path),
                    project_files,
                )
            )
        except Exception:
            pass
    return project_files


def get_project_files(project_path: str) -> Set[str]:
    """
    :param project_path: project path.
    :type project_path: str
    :return: All of the relevant python files in the projects.
    :rtype: Set[str]
    """
    is_dot_in_path = "." in sys.path
    project_files = [
        os.path.join(directory_path, filename)
        for directory_path, _, filenames in os.walk(project_path)
        for filename in filenames
        if os.path.splitext(filename)[1] == ".py"
        and not is_test_file(directory_path, filename)
    ]
    if is_dot_in_path:
        is_dot_in_path = True
        absolute_path = os.path.abspath(".")
        replaced_project_files = [
            file_path.replace(absolute_path, os.path.join(absolute_path, "."))
            for file_path in project_files
        ]
        project_files.extend(replaced_project_files)
    project_files = filter_venv(project_files, project_path)
    project_files = filter_snowmateignore(project_files, project_path)
    project_files = set(project_files)
    return project_files


def terminate_subprocess(subprocess: SubProcessBase, timeout: int = 10) -> bool:
    """
    This function terminates a subprocess, either gracefully or brutally.
    :param subprocess: subprocess to terminate.
    :type subprocess: SubProcessBase
    :return: True if the subprocess was terminated gracefully,
             False if a timeout was reached or an exception occured.
    :rtype: bool
    """
    is_terminated = False

    if subprocess.pid:
        os.kill(subprocess.pid, signal.SIGTERM)

        try:
            is_terminated = subprocess.join(timeout=timeout)
        except Exception:
            pass

        if not is_terminated:
            os.kill(subprocess.pid, signal.SIGKILL)

        return is_terminated

    return True


def collector_exit():
    """
    This func is called when user code stops,
    its prevents the code from exiting till we finish sending all message in
    queue or if a timeout is reached.
    @return:
    """
    subprocesses = [
        CollectorSettings.metrics_subprocess,
        CollectorSettings.data_subprocess,
    ]

    if reduce(lambda x, y: x is not None or y is not None, subprocesses):
        try:
            if not CollectorSettings.sanity:
                CollectorSettings.logger.log(
                    CollectorSettings.log_level, logs_consts.PROCESS_FINISHED
                )

            for subprocess in subprocesses:
                is_graceful_exit = terminate_subprocess(subprocess)
                if not is_graceful_exit:
                    CollectorSettings.logger.log(
                        CollectorSettings.log_level, logs_consts.PROCESS_TIMEOUT
                    )

            CollectorSettings.logger.log(
                CollectorSettings.log_level, logs_consts.COLLECTOR_DONE
            )

            send_exit_metric()

        except Exception:
            # only because there are many unknown exceptions
            # that can be thrown at exist combining snowlib and debugger
            pass


def send_exit_metric():
    exit_obj = ExitEvent(
        CollectorSettings.tenant_id,
        CollectorSettings.project_id,
        CollectorSettings.python_version,
        CollectorSettings.lib_version,
    )
    exit_msg = CollectorSettings.serializer.serialize(exit_obj)

    CollectorSettings.metrics_subprocess.send_message(exit_msg)


def start(  # pylint: disable=too-many-statements,too-many-branches
    project_path: str,
    project_id: str = os.getenv("SNOWMATE_PROJECT_ID", ""),
    data_sink: Optional[SinkBase] = DataSinks.HTTP,
    _sampling_percentage: Optional[float] = None,
    _external_calls_max: Optional[int] = None,
    auth_url: str = "https://auth.snowmate.io",
    api_url: str = "https://api.snowmate.io",
    should_obfuscate_data: Optional[bool] = True,
    client_id: Optional[str] = os.getenv("SNOWMATE_CLIENT_ID", ""),
    secret_key: Optional[str] = os.getenv("SNOWMATE_SECRET_KEY", ""),
    log_level: Optional[int] = logging.WARNING,
    metrics_sink: Optional[MetricsDataSinks] = MetricsDataSinks.HTTP,
    _timer_interval_seconds=300,
    sanity: bool = False,
    **communicator_settings,
):
    """
    Start the instrumentation of a Python project.

    :param project_path: str - The full path to the project to be instrumented.

    :param project_id: str - The id of the Snowmate project you created through Snowmate's web app.

    :param data_sink: Optional[SinkBase] - The data sink to use for sending the collected data.
    Defaults to DataSinks.HTTP  (Sends the data to Snowmate's SaaS)

    :param _sampling_percentage: Optional[float] - The percentage of functions to sample,
    as a float between 0 and 100. Defaults to 0.01.

    :param _external_calls_max: Optional[int] - The maximum number of external calls to
    allow per function. Defaults to 100.

    :param auth_url: str - The URL of the Snowmate's authentication service.
    Defaults to "https://auth.snowmate.io".

    :param api_url: str - The URL of the Snowmate API service. Defaults to "https://api.snowmate.io".

    :param should_obfuscate_data: Optional[bool] - Whether to obfuscate the collected
    data before sending it. Defaults to True.

    :param client_id: Optional[str] - Snowmate's client ID. If you did not create one,
    you can obtain in through Snowmate's web app.

    :param secret_key: Optional[str] - Snowmate's secret key. If you did not create one,
    you can obtain in through Snowmate's web app.

    :param log_level: Optional[int] - The logging level to use for the collector.
    Defaults to logging.WARNING.

    :param metrics_sink: Optional[MetricsDataSinks] - The metrics data sink to use for sending metadata.

    :param _timer_interval_seconds: int - The interval, in seconds, at which to check timer
        Defaults to 300 (5 minutes).

    :param sanity: bool - Whether to perform sanity checks on the collector setup. Defaults to False.
        It's recommended to run it on the first time after adding Snowmate collector.

    :param communicator_settings: Any - Additional settings to pass to the communication layer.
    """

    if DEBUG_LOGGING_ENABLED:
        CollectorSettings.debug_logger = get_debug_logger()
        log_debug("[snowmate_collector.start] Starting Snowmate collector")

    if sanity is True:
        CollectorSettings.sanity = True
        data_sink = DataSinks.SANITY
        metrics_sink = MetricsDataSinks.SANITY
        _sampling_percentage = 100
        CollectorSettings.logger.log(
            CollectorSettings.log_level, logs_consts.RUNNING_IN_SANITY_MODE
        )

    data_sink = data_sink.value
    metrics_sink = metrics_sink.value
    project_path = get_formatted_project_path(project_path)
    if _is_user_using_tracer():
        return
    CollectorSettings.log_level = log_level
    authorizer = None
    if (
        data_sink.is_auth_needed() or metrics_sink.is_auth_needed()
    ) and communicator_settings.get("no_auth") is None:
        try:
            authorizer = Authorizer(auth_url, client_id, secret_key)
            CollectorSettings.tenant_id = authorizer.user_details[api_consts.TENANT_ID]
        except AuthError as e:
            if (str(e)) == BAD_REQUEST:
                CollectorSettings.logger.error(
                    logs_consts.COLLECTOR_COMMUNICATION_ERROR
                )
            else:
                CollectorSettings.logger.error(logs_consts.AUTH_ERROR)
            return
        if sanity:
            CollectorSettings.logger.log(
                CollectorSettings.log_level, logs_consts.SUCCESSFUL_AUTH
            )

    try:
        data_sink.configure_sink(
            api_url=api_url,
            authorizer=authorizer,
            project_id=project_id,
            **communicator_settings,
        )
        metrics_sink.configure_sink(
            api_url=api_url,
            authorizer=authorizer,
            project_id=project_id,
            **communicator_settings,
        )

    except ProjectDoesNotExistException:
        CollectorSettings.logger.error(logs_consts.NO_SUCH_PROJECT_ID)
        raise ProjectDoesNotExistException()
    except Exception:
        CollectorSettings.logger.error(logs_consts.COLLECTOR_COMMUNICATION_ERROR)
        return

    CollectorSettings.data_sink = data_sink
    CollectorSettings.metrics_sink = metrics_sink
    CollectorSettings.project_path = project_path
    CollectorSettings.project_id = project_id
    CollectorSettings.should_obfuscate_data = should_obfuscate_data
    CollectorSettings.project_files = get_project_files(CollectorSettings.project_path)
    CollectorSettings.serializer = IpcPickleSerializer()
    set_data_process()
    set_metrics_process()
    CollectorSettings.python_version = platform.python_version()
    CollectorSettings.lib_version = get_version(SNOWMATE_COLLECTOR_LIB_NAME)
    CollectorSettings.timer_interval = _timer_interval_seconds

    if authorizer and (_sampling_percentage is None or _external_calls_max is None):
        rate_changing_thread = threading.Thread(
            target=collector_remote_settings,
            args=(
                authorizer.bearer_access_token,
                api_url,
                project_id,
                CollectorSettings.timer_interval,
            ),
            kwargs={
                "skip_sampling_percentage": _sampling_percentage is not None,
                "skip_external_calls_max": _external_calls_max is not None,
            },
            daemon=True,
        )
        rate_changing_thread.start()

    send_start_event()
    if _sampling_percentage is None:
        _sampling_percentage = DEFAULT_SAMPLING_RATE
    if _external_calls_max is None:
        _external_calls_max = DEFAULT_MAX_FUNCTION_EXTERNAL_CALLS
    CollectorSettings.sampling_percentage = _sampling_percentage
    CollectorSettings.external_calls_max = _external_calls_max

    send_sampling_rate_event()
    send_external_calls_max_event()

    sample_ratio = sampling_percentage_to_ratio(_sampling_percentage)
    snowmate_collector.interceptor.apply(  # pylint: disable=c-extension-no-member
        CollectorSettings.project_files, sample_ratio
    )
    if not CollectorSettings.atexit_registered:
        atexit.register(collector_exit)
        CollectorSettings.atexit_registered = True


def sampling_percentage_to_ratio(sampling_percentage: float) -> float:
    return max(min(sampling_percentage, 100.0), 0.0) / 100.0


def send_start_event():
    start_metric = StartEvent(
        CollectorSettings.tenant_id,
        CollectorSettings.project_id,
        CollectorSettings.python_version,
        CollectorSettings.lib_version,
    )

    start_msg = CollectorSettings.serializer.serialize(start_metric)
    CollectorSettings.metrics_subprocess.send_message(start_msg)


def send_sampling_rate_event():
    start_metric = SamplingRateWasSet(
        CollectorSettings.tenant_id,
        CollectorSettings.project_id,
        CollectorSettings.python_version,
        CollectorSettings.lib_version,
        CollectorSettings.sampling_percentage,
    )

    start_msg = CollectorSettings.serializer.serialize(start_metric)
    CollectorSettings.metrics_subprocess.send_message(start_msg)


def send_external_calls_max_event():
    external_calls_max_metric = ExternalCallsMaxLimitWasSet(
        CollectorSettings.tenant_id,
        CollectorSettings.project_id,
        CollectorSettings.python_version,
        CollectorSettings.lib_version,
        CollectorSettings.external_calls_max,
    )

    external_calls_max_msg = CollectorSettings.serializer.serialize(
        external_calls_max_metric
    )
    CollectorSettings.metrics_subprocess.send_message(external_calls_max_msg)


def collector_remote_settings(
    access_token: str,
    api_url: str,
    project_id: str,
    timer_interval,
    skip_sampling_percentage: bool = False,
    skip_external_calls_max: bool = False,
):
    skip_all = skip_sampling_percentage and skip_external_calls_max
    if skip_all:
        return

    while True:
        try:
            response = get_project_settings(
                access_token=access_token, api_url=api_url, project_id=project_id
            )
            remote_sample_rate = response.get(
                COLLECTOR_SAMPLING_RATE, DEFAULT_SAMPLING_RATE
            )
            remote_external_calls_max = response.get(
                COLLECTOR_MAX_FUNCTION_EXTERNAL_CALLS,
                DEFAULT_MAX_FUNCTION_EXTERNAL_CALLS,
            )
            if (
                not skip_sampling_percentage
                and remote_sample_rate != CollectorSettings.sampling_percentage
            ):
                CollectorSettings.sampling_percentage = remote_sample_rate
                snowmate_collector.interceptor.set_collecting_rate(  # pylint: disable=c-extension-no-member
                    sampling_percentage_to_ratio(CollectorSettings.sampling_percentage)
                )
                send_sampling_rate_event()
            if (
                not skip_external_calls_max
                and remote_external_calls_max != CollectorSettings.external_calls_max
            ):
                CollectorSettings.external_calls_max = remote_external_calls_max
                send_external_calls_max_event()
            time.sleep(timer_interval)

        except Exception:
            pass


def get_formatted_project_path(project_path: str) -> str:
    """
    This function return the project path after formatting.

    :param project_path: Non formatted porject path.
    :type project_path: str
    :return: Formatted project path.
    :rtype: str
    """
    if not os.path.basename(project_path):
        project_path = project_path[0:-1]
    return project_path
