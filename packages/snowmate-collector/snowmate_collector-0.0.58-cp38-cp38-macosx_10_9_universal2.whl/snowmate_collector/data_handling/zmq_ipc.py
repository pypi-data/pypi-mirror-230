import os
import signal
import stat
import sys
import threading
import time
from typing import Callable, Dict, List, Union

import zmq

from snowmate_collector.configs.collector_settings import CollectorSettings, log_debug
from snowmate_collector.data_collection.function_call_data import UserFunctionCall
from snowmate_collector.data_handling.function_call_msg_handler import (
    FunctionCallMsgHandler,
)
from snowmate_collector.data_handling.interfaces import MessageHandler, SubProcessBase
from snowmate_collector.data_handling.metrics_msg_handler import MetricsMsgHandler
from snowmate_collector.data_handling.msg_router_subscriber import MessageRouter
from snowmate_collector.data_handling.sub_process_manger import (
    SubProcessEnum,
    SubProcessSingleton,
)

CONCURRENT_WORKERS: int = 1
SOCKET_ADDRESS: str = "tcp://*"
SOCKET_SEND_HIGH_WATERMARK: int = 1100000
SOCKET_SYNC_MESSAGE_SEND: bytes = b"SYN"
MAX_FD = 1024
STD_ERR = 2
SOCKET_SUBSCRIPTION_TOPIC: bytes = b""
SOCKET_RECEIVE_TIMEOUT_MILLISECONDS: int = 2000
SOCKET_SYNC_MESSAGE_RECEIVE: bytes = b"ACK"
TIMEOUT_HANDLER = "timeout_handler"

SHOULD_STOP = False


def sigterm_handler(*_args, **_kwargs):
    """
    Called in the receiver process (worker).
    This function is being called if the process receives sigterm signal.
    """
    global SHOULD_STOP  # pylint: disable=global-statement
    SHOULD_STOP = True


def init_handler_builder(
    subprocess_type: SubProcessEnum, custom_handler: Union[Callable, None] = None
) -> Callable:
    return InitSubProcess.get_handler(subprocess_type, custom_handler)


def close_all_parent_network_sockets() -> None:
    """
    Called in the receiver process (worker).
    This function does the best effort to clean up all of the parent process threads and fds.
    """
    for file_descriptor in range(STD_ERR, MAX_FD):
        try:
            fd_stat = os.fstat(file_descriptor)
            if (
                stat.S_ISSOCK(fd_stat.st_mode)
                and not stat.S_ISPORT(fd_stat.st_mode)
                and fd_stat.st_ino == 0
            ):  # close every network socket
                try:
                    os.close(file_descriptor)
                    log_debug(
                        f"[close_all_parent_network_sockets] closed file descriptor: {file_descriptor}"
                    )
                except Exception as e:
                    log_debug(
                        f"[close_all_parent_network_sockets] failed to close file "
                        f"descriptor: {file_descriptor}, Exception: {e}"
                    )

        except Exception:
            pass


class ZmqDataReceiver:
    """
    This class is responsible for receiving data from the sender process.
    It is accessed in the worker process context, NEVER in the user process context.
    """

    def __init__(self) -> None:
        """
        Init the object with default empty values.
        """
        self._worker_port = 0
        self._sync_port = 0
        self._ack_port = 0
        self._ack_client = None
        self._worker_socket = None
        self.subscribers: List[MessageHandler] = []
        self.sync_interval: int = 0
        self.receive_counter: int = 0
        self.liveness_probing: bool = False

    def _init_worker_socket_if_needed(self) -> None:
        """
        This function performs a handshake with the main process in order to
        initiate the communication channel.
        """
        if self._worker_socket is not None:
            # Socket already initialized
            return

        # Init the socket
        # We use pubsub socket to avoid losing messages, and to be able to add multiple subscribers.
        zmq_context = zmq.Context()  # pylint: disable=abstract-class-instantiated
        self._worker_socket = zmq_context.socket(socket_type=zmq.SUB)
        self._worker_socket.connect(addr=f"tcp://localhost:{self._worker_port}")
        self._worker_socket.setsockopt(zmq.SUBSCRIBE, SOCKET_SUBSCRIPTION_TOPIC)
        self._worker_socket.setsockopt(
            zmq.RCVTIMEO, SOCKET_RECEIVE_TIMEOUT_MILLISECONDS
        )

        # Init the sync socket
        sync_client = zmq_context.socket(socket_type=zmq.REQ)
        sync_client.connect(addr=f"tcp://localhost:{self._sync_port}")

        if self.liveness_probing:
            self._ack_client = zmq_context.socket(socket_type=zmq.DEALER)
            self._ack_client.connect(addr=f"tcp://localhost:{self._ack_port}")

        is_initialized: bool = False
        while not is_initialized:
            try:
                # Wait for the sync message
                self._worker_socket.recv(flags=zmq.NOBLOCK)

                # Send the sync message
                sync_client.send(data=SOCKET_SYNC_MESSAGE_RECEIVE)

                is_initialized = True

            except zmq.ZMQError:
                pass

    def add_subscriber(self, handler: MessageHandler) -> None:
        """
        Used to add a subscriber to the received data.
        """
        self.subscribers.append(handler)

    def wait_for_subscribers(self):
        """
        This function waits for all subscribers to be done.
        """
        for subscriber in self.subscribers:
            subscriber.join()

    def start(
        self,
        data_port: int,
        _sync_port: int,
        ack_port: int,
        sync_interval: int = 10,
        liveness_probing: bool = True,
    ) -> None:
        """
        This function is the recevier process main loop.
        The main loop will exit after sigterm was sent from the
        atexit and there were no messages for 2 seconds.
        :param data_port: The port used to transfer data.
        :type data_port: int
        :param _sync_port: The port used for handshake.
        :type _sync_port: int.
        :param ack_port: The port used for ack.
        :type ack_port: int.
        :param sync_interval: The interval to send ack.
        :type sync_interval: int.
        :param liveness_probing: Whether to send acks for liveness to the sender.
        :type liveness_probing: bool.
        """
        # Register the sigterm handler.
        # IMPORTANT! This will work only when running in the main thread of the main interpreter.
        #            This limitation is built in the `signal` module.
        signal.signal(signal.SIGTERM, sigterm_handler)

        # Init ports and sockets + handshake
        self._worker_port = data_port
        self._sync_port = _sync_port
        self._ack_port = ack_port
        self.sync_interval = sync_interval
        self.liveness_probing = liveness_probing
        self._init_worker_socket_if_needed()
        running = True

        try:
            while running:
                # Worker loop
                try:
                    # Receive and handle message
                    self._recv_and_handle_message()
                except zmq.error.Again:
                    if SHOULD_STOP:
                        # If we got sigterm, wait for all subscribers to be done.
                        self.wait_for_subscribers()
                    else:
                        # If we didn't get sigterm, call the timeout handler.
                        self.call_timeout_handler()
                    running = not SHOULD_STOP
                    continue
        except Exception:
            pass
        os._exit(0)  # pylint: disable=protected-access

    def call_timeout_handler(self):
        """
        This function calls the timeout handler of all subscribers.
        """
        for subscriber in self.subscribers:
            timeout_method = subscriber.get_timeout_method()
            if timeout_method:
                timeout_method()

    def _recv_and_handle_message(self):
        """
        This function receives a message from the sender process and handles it.
        """
        multipart_message = self._worker_socket.recv()
        if multipart_message != SOCKET_SYNC_MESSAGE_SEND:
            # If the message is not a sync message, handle it.
            for subscriber in self.subscribers:
                try:
                    subscriber.handle_message(multipart_message)
                except (
                    Exception
                ) as e:  # Many errors could happen while handling a message ,
                    # We dont want them to crush the subprocess.
                    log_debug(
                        f"[ZmqDataReceiver._recv_and_handle_message] Exception: {e}"
                    )

            if self.liveness_probing:
                self.receive_counter += 1
                if self.receive_counter >= self.sync_interval:
                    try:
                        self._ack_client.send_multipart(
                            msg_parts=[
                                bytes(str(id(self)), encoding="utf-8"),
                                SOCKET_SYNC_MESSAGE_RECEIVE,
                            ]
                        )
                        self.receive_counter = 0
                    except zmq.ZMQError:
                        pass
                    except Exception:
                        pass


class SenderStateEnum:
    NOT_INITIATED = 0
    INITIATED = 1
    RECEIVER_NOT_RESPONDING = -1


class ZmqDataSender:
    def __init__(self) -> None:
        self.zmq_context = zmq.Context()  # pylint: disable=abstract-class-instantiated
        self.pub_socket = None
        self.pub_port = None
        self.sync_socket = None
        self.sync_port = None
        self.ack_socket = None
        self.ack_port = None
        self.sync_interval: int = 0
        self.send_counter: int = 0
        self.num_subscribers = 0
        self.pid = 0
        self.state: SenderStateEnum = SenderStateEnum.NOT_INITIATED
        self.liveness_probing: bool = False

    def start(self, sync_interval: int = 20, liveness_probing: bool = True) -> None:
        """
        This function initite zmq context and ports.
        :param sync_interval: The interval to check for acks.
        :type sync_interval: int
        :param liveness_probing: Whether to check for liveness of the receiver.
        :type liveness_probing: bool
        """
        self.sync_interval = sync_interval

        self.zmq_context = zmq.Context()  # pylint: disable=abstract-class-instantiated

        # Init data socket
        self.pub_socket = self.zmq_context.socket(socket_type=zmq.PUB)
        self.pub_socket.sndhwm = SOCKET_SEND_HIGH_WATERMARK
        self.pub_port = self.pub_socket.bind_to_random_port(addr=SOCKET_ADDRESS)

        self.liveness_probing = liveness_probing
        if liveness_probing:
            self.ack_socket = self.zmq_context.socket(socket_type=zmq.ROUTER)
            self.ack_port = self.ack_socket.bind_to_random_port(addr=SOCKET_ADDRESS)

        self.sync_socket = self.zmq_context.socket(socket_type=zmq.REP)
        self.sync_port = self.sync_socket.bind_to_random_port(addr=SOCKET_ADDRESS)

    def initate_connection(self) -> None:
        """
        This function performs a handshake with the receiver process.
        """
        self.pid = self.pid
        while self.num_subscribers < CONCURRENT_WORKERS:
            # Send sync message
            self.pub_socket.send(data=SOCKET_SYNC_MESSAGE_SEND)
            try:
                # Wait for sync message
                self.sync_socket.recv(flags=zmq.NOBLOCK)
                self.num_subscribers += 1
            except zmq.ZMQError:
                continue
        self.state = SenderStateEnum.INITIATED

    def send(self, data: bytes) -> None:
        """
        This function sends data to the receiver process.
        :param data: data to be sent.
        :type data: bytes
        """
        self.pub_socket.send(data=data)

        if self.liveness_probing is True:
            self.send_counter += 1
            if self.send_counter >= self.sync_interval:
                is_alive = self.check_receiver_liveness()
                if (is_alive is False) and (is_alive is not None):
                    self.state = SenderStateEnum.RECEIVER_NOT_RESPONDING
                self.send_counter = 0

    def check_receiver_liveness(self) -> bool:
        """
        This function checks if the receiver process is alive.
        It assumes that the receiver process sends acks AT LEAST every sync_interval.
        :return: True if the receiver is alive, False otherwise.
        :rtype: bool
        """
        try:
            msg = self.ack_socket.recv_multipart(flags=zmq.NOBLOCK)
            _receiver_id = msg[1]  # pylint: disable=unsubscriptable-object, unused-variable
            ack = msg[2]  # pylint: disable=unsubscriptable-object
            return ack == SOCKET_SYNC_MESSAGE_RECEIVE
        except zmq.ZMQError:
            pass
        except Exception:
            pass
        return False

    def clean_up(self) -> None:
        """
        This function cleans up the sender sockets.
        NOTICE! It is called in the worker process context.
        """
        self.sync_socket.close()
        self.pub_socket.close()
        close_all_parent_network_sockets()


class ZmqIpcSubprocess(SubProcessBase):
    def __init__(
        self,
        name: SubProcessEnum,
        sync_interval: int = 50,
        liveness_probing: bool = False,
    ) -> None:
        """
        This wraps a zmq based data receiver.
        :param name: The name of the subprocess.
        :type name: SubProcessEnum
        :param sync_interval: The interval to check for acks from the subprocess.
        :type sync_interval: int
        :param liveness_probing: Whether to check for liveness of the subprocess.
        :type liveness_probing: bool
        """
        self.data_sender = ZmqDataSender()
        self.data_receiver = ZmqDataReceiver()
        self.pid = 0
        self.name = name
        self.sync_interval = sync_interval
        self.liveness_probing = liveness_probing

    def spawn_subprocess(self, suppress_stderr: bool = False) -> None:
        """
        This function spwans new receiver process.
        :param suppress_stderr: Whether to suppress stderr of the subprocess.
        :type suppress_stderr: bool
        """
        self.data_sender.start(
            sync_interval=self.sync_interval, liveness_probing=self.liveness_probing
        )
        self.pid = os.fork()
        if self.pid <= 0:
            # Worker process context.
            # Initiate connection with the sender process.
            for thread in threading.enumerate():  # Best effort to close all threads
                try:
                    thread.stop()
                except Exception:
                    pass
            # Try to clean up all parent network sockets
            self.data_sender.clean_up()
            try:
                # This is a dirty hack to suppress stderr of the subprocess.
                # In production, ALWAYS set suppress_stderr to True so we won't
                # show the user errors generated by our subprocess.
                if suppress_stderr:
                    try:
                        log_debug(
                            "[ZmqIpcSubprocess.spawn_subprocess] suppressing stderr"
                        )
                        with open(os.devnull, "w", encoding="utf-8") as f:
                            sys.stderr = f
                    except Exception as e:
                        log_debug(f"[ZmqIpcSubprocess.spawn_subprocess] Exception: {e}")

                self.data_receiver.start(
                    self.data_sender.pub_port,
                    self.data_sender.sync_port,
                    self.data_sender.ack_port,
                    liveness_probing=self.liveness_probing,
                    # make the receiver send acks at twice the rate of the sender's liveness sampling
                    sync_interval=int(self.sync_interval / 2),
                )
            except KeyboardInterrupt:
                os._exit(0)  # pylint: disable=protected-access
            except Exception:
                os._exit(0)  # pylint: disable=protected-access
        else:
            log_debug(
                f"[ZmqIpcSubprocess.spawn_subprocess]"
                f"[{'DATA' if self.name == SubProcessEnum.DATA else 'METRICS'}] "
                f"receiver pid: {self.pid}"
            )
            self.data_sender.initate_connection()

    def add_subscriber(self, handler: MessageHandler) -> None:
        """
        Add data handler to the receiver process.
        """
        self.data_receiver.add_subscriber(handler)

    def send_message(self, data: bytes) -> None:
        """
        This function sends data through ZMQ to the receiver process.
        """
        self.data_sender.send(data)
        if (
            self.liveness_probing
            and self.data_sender.state == SenderStateEnum.RECEIVER_NOT_RESPONDING
        ):
            # send SIGTERM to the child process to make sure it's dead
            try:
                os.kill(self.pid, signal.SIGKILL)
            except OSError:
                pass
            subprocess_init_handler = init_handler_builder(self.name)
            subprocess_init_handler()

    def join(self, timeout: int = None) -> bool:
        """
        This function wait for the subprocess to be killed.
        :param timeout: timeput for waiting on join. None indicates wait forever
        :type timeout: bool | None
        :return: True if joined gracefully, False if timeout was reached
        :rtype: bool
        """
        if timeout is None:
            os.waitpid(self.pid, 0)
            return True

        start_time = time.time()
        while True:
            if self.pid:
                pid, status = os.waitpid(self.pid, os.WNOHANG)
                if pid == self.pid and (os.WIFEXITED(status) or os.WIFSIGNALED(status)):
                    return True

            elapsed_time = time.time() - start_time
            if elapsed_time >= timeout:
                return False

            time.sleep(timeout / 10)


def set_metrics_process():
    metrics_zmq = ZmqIpcSubprocess(SubProcessEnum.METRICS)
    metrics_msg_router = MetricsMsgHandler(CollectorSettings.metrics_sink)
    metrics_zmq.add_subscriber(metrics_msg_router)
    CollectorSettings.metrics_subprocess = SubProcessSingleton(metrics_zmq)


def set_data_process():
    data_zmq = ZmqIpcSubprocess(SubProcessEnum.DATA)
    data_msg_router = MessageRouter()
    data_msg_router.add_message_handler(UserFunctionCall, FunctionCallMsgHandler())
    data_zmq.add_subscriber(data_msg_router)
    CollectorSettings.data_subprocess = SubProcessSingleton(data_zmq)


class SubProcessInitHandlers:
    """
    This class holds initiation handlers for the different types of subprocesses.
    The handlers must not raise exceptions!
    """

    @staticmethod
    def init_data_subprocess(*_args, **_kwargs):
        """
        This function is being called if the data subprocess needs initiation.
        """
        try:
            set_data_process()
        except Exception:
            pass

    @staticmethod
    def init_metrics_subprocess(*_args, **_kwargs):
        """
        This function is being called if the metrics subprocess needs initiation.
        """
        try:
            set_metrics_process()
        except Exception:
            pass


class InitSubProcess:
    handlers: Dict[SubProcessEnum, Callable] = {
        SubProcessEnum.DATA: SubProcessInitHandlers.init_data_subprocess,  # pylint: disable=protected-access
        SubProcessEnum.METRICS: SubProcessInitHandlers.init_metrics_subprocess,  # pylint: disable=protected-access
    }

    @staticmethod
    def get_handler(
        subprocess_type: SubProcessEnum, custom_handler: Union[Callable, None] = None
    ) -> Callable:
        """
        This function returns the handler for the given subprocess type.
        :param subprocess_type: The subprocess type.
        :type subprocess_type: SubProcessEnum
        :param custom_handler: A custom handler to run after the init handler.
                               It must receive the same arguments as the init handler.
        :type custom_handler: Callable | None
        :return: The handler for the given subprocess type.
        :rtype: Callable
        """

        def handler(*args, **kwargs):
            init_subprocess_handler = InitSubProcess.handlers.get(subprocess_type, None)
            if init_subprocess_handler is not None:
                init_subprocess_handler(*args, **kwargs)
            if custom_handler is not None:
                custom_handler(*args, **kwargs)

        return handler
