import asyncio
import threading
import time
from dataclasses import dataclass
from typing import Dict, Tuple, List
from urllib.parse import urljoin

import aiohttp
from snowmate_common.sender import AUTHORIZATION_HEADER
from snowmate_common.utils.projects import does_project_exist

from snowmate_collector.exceptions import ProjectDoesNotExistException
from snowmate_collector.data_sink.metrics_sink_base import MetricsSinkBase
from snowmate_collector.metrics import Metrics

CONTENT_TYPE_HEADER: str = "Content-type"
SLEEP_NO_MESSAGES_TIME: float = 0.1
WAIT_FOR_DONE_SLEEP: int = 1


@dataclass
class Request:
    url: str
    headers: Dict
    json: Dict


def create_metric_request_data(
        base_url: str,
        access_token: str,
        metrics_data: Dict
) -> Tuple[str, Dict[str, str], Dict]:
    """
    This function creates the request data for sending metrics.
    :param base_url: base url of the server.
    :type base_url: str
    :param access_token: access token.
    :type access_token: str
    :param metrics_data: metrics data.
    :type metrics_data: Dict
    :return: url, headers, payload
    :rtype: Tuple[str, Dict[str, str], Dict]
    """
    url = urljoin(base_url, "metrics")
    headers = {
        AUTHORIZATION_HEADER: f"Bearer {access_token}",
        CONTENT_TYPE_HEADER: "application/json"
    }
    payload = metrics_data

    return url, headers, payload


class MetricsHTTPSink(MetricsSinkBase):
    """
    Metrics sink that sends the data to the Snowmate server via http.
    """

    def __init__(self) -> None:
        self.authorizer = None
        self.access_token = ""
        self.client_id = None
        self.secret_key = None
        self.requests_queue = []
        self.event_loop_on = False
        self.joined = False
        self.done = False
        self.auth_needed = True
        self.api_url = ""

    def start_async_loop(self) -> None:
        """
        This function start asyncio loop.
        This way the sink can send data to the server in a non-blocking way.
        """
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(self.asyncio_loop(loop))

    async def asyncio_loop(
        self, loop: asyncio.unix_events._UnixSelectorEventLoop
    ) -> None:
        """
        This function processes the requests queue and sends it via http.
        :param loop: asyncio loop
        :type loop: asyncio.unix_events._UnixSelectorEventLoop
        """
        without_tsl_checking: aiohttp.TCPConnector = aiohttp.TCPConnector(
            verify_ssl=False
        )
        # Open session once and use it for all requests.
        async with aiohttp.ClientSession(connector=without_tsl_checking) as session:
            # Create a list of tasks to wait for.
            asyncio_tasks = []
            while not self.joined or self.requests_queue:
                # Populate the tasks list from the queue.
                await self.process_tasks(loop, session, asyncio_tasks)
            if self.joined:
                try:
                    # Wait for all the tasks to finish.
                    await asyncio.gather(*asyncio_tasks)
                except aiohttp.client_exceptions.ClientConnectorError:
                    pass
                finally:
                    self.done = True

    async def process_tasks(
        self,
        loop: asyncio.unix_events._UnixSelectorEventLoop,
        session: aiohttp.ClientSession,
        asyncio_tasks: List,
    ) -> None:
        """
        This function processes the requests queue and creates asyncio tasks from it.
        :param loop: asyncio loop
        :type loop: asyncio.unix_events._UnixSelectorEventLoop
        :param session: http session
        :type session: aiohttp.ClientSession
        :param asyncio_tasks: list of asyncio tasks for population.
        :type asyncio_tasks: List
        """
        if self.requests_queue:
            task = self.requests_queue.pop()
            if task:
                try:
                    coro = self.create_asyncio_task(  # pylint: disable=too-many-function-args
                        loop, session, task
                    )
                    asyncio_tasks.append(coro)
                except Exception:
                    pass
        else:
            await asyncio.sleep(SLEEP_NO_MESSAGES_TIME)

    def export_data(self, metrics_data: Metrics):
        """
        This function adds the metrics it receives to the request queue.
        :param metrics_data: metrics data.
        :type metrics_data: Metrics
        """
        if not self.event_loop_on:
            self.start_asyncio_loop()

        try:
            self.add_request_to_queue(metrics_data.to_json())
        except Exception:
            pass

    def add_request_to_queue(self, metrics_data: Dict) -> None:  # pylint: disable=arguments-renamed
        """
        This function adds request to the processing queue.
        :param metrics_data: request payload.
        :type metrics_data: Dict.
        """
        url, headers, payload = create_metric_request_data(
            self.api_url,
            self.access_token,
            metrics_data
        )

        self.requests_queue.append(
            Request(url=url, json=payload, headers=headers)
        )

    @staticmethod
    def create_asyncio_task(
        loop: asyncio.unix_events._UnixSelectorEventLoop,
        session: aiohttp.ClientSession,
        http_request: Request,
    ) -> asyncio.coroutine:
        """
        This function makes asyncio task from a Request.
        :param loop: current asyncio loop.
        :type loop: asyncio.unix_events._UnixSelectorEventLoop
        :param session: http session
        :type session: aiohttp.ClientSession
        :param http_request: request to send.
        :type http_request: Request
        :return: coroutine of http sending.
        :rtype: asyncio.coroutine
        """
        return loop.create_task(
            (
                session.post(
                    url=http_request.url,
                    headers=http_request.headers,
                    json=http_request.json,
                )
            )
        )

    def start_asyncio_loop(self) -> None:
        """
        This function start new event loop in new thread.
        """
        try:
            threading.Thread(target=MetricsHTTPSink.start_async_loop, args=(self,)).start()
            self.event_loop_on = True
        except Exception:
            pass

    def configure_sink(
        self, authorizer=None, no_auth=False, api_url="", project_id=""
    ):  # pylint: disable=arguments-differ
        """
        Used to match the SinkBase.
        """
        self.api_url = api_url

        if not no_auth:
            self.auth_needed = False
            self.authorizer = authorizer
            self.access_token = self.authorizer.bearer_access_token
            if not does_project_exist(
                self.authorizer.bearer_access_token, self.api_url, project_id
            ):
                raise ProjectDoesNotExistException()
        else:
            self.access_token = ""

    def join(self):  # pylint: disable=arguments-differ
        """
        This function waits for all the tasks to be done.
        """
        self.joined = True
        while not self.done:  # waits for the asyncio loop to exit
            time.sleep(WAIT_FOR_DONE_SLEEP)
