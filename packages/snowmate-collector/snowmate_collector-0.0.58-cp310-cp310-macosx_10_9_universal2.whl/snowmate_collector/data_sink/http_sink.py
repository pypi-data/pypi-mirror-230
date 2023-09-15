import asyncio
import json
import threading
import time
from dataclasses import dataclass
from typing import List

import aiohttp
from snowmate_common.messages_data.messages import MainMessage, QueueMessage, TestCase
from snowmate_common.sender import Destinations, create_message
from snowmate_common.utils.projects import does_project_exist

from snowmate_collector.data_sink.sink_base import SinkBase
from snowmate_collector.exceptions import ProjectDoesNotExistException

MAX_DATA_SIZE = 100 * 1024
AUTHORIZATION = "Authorization"
SLEEP_NO_MESSAGES_TIME = 0.1
ENQUEUE_ROUTE = "enqueue"
WAIT_FOR_DONE_SLEEP = 1
MESSAGE_GROUP_KEY = "MessageGroupId"
MESSAGE_BODY_KEY = "MessageBody"
GROUP_ID = "1"
MESSAGE_DEDUPLICATION_ID_KEY = "MessageDeduplicationId"
BEARER_HEADER = "Bearer"


@dataclass
class Request:
    url: str
    headers: dict
    data: str
    method: str


class HTTPSink(SinkBase):
    """
    Data sink that sends the data to the Snowmate server via http.
    """

    def __init__(
        self,
    ) -> None:
        self.authorizer = None
        self.access_token = ""
        self.client_id = None
        self.secret_key = None
        self.requests_queue = []
        self.event_loop_on = False
        self.joined = False
        self.done = False
        self.api_url = None
        self.auth_needed = True
        super().__init__()

    def start_async_loop(self) -> None:
        """
        This function starts asyncio loop.
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

    def create_asyncio_task(
        self,
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
                session.request(
                    method=http_request.method,
                    url=http_request.url,
                    headers=http_request.headers,
                    data=http_request.data,
                )
            )
        )

    def export_data(self, msg: TestCase):
        """
        This function prints a given message.
        :param msg: message to print.
        :type msg: TestCase
        """
        if not self.event_loop_on:
            self.start_asyncio_loop()

        queue_msg = QueueMessage(test_case=msg)
        main_msg = MainMessage(access_token=self.access_token, queue_message=queue_msg)
        try:
            self.add_request_to_queue(main_msg)
        except Exception:
            pass

    def add_request_to_queue(self, msg: MainMessage) -> None:
        """
        This function adds request to the processing queue.
        :param msg: request payload.
        :type msg: MainMessage.
        """
        method, url, headers, payload = create_message(
            self.api_url, Destinations.BASELINE, msg
        )
        self.requests_queue.append(
            Request(url=url, data=json.dumps(payload), headers=headers, method=method)
        )

    def start_asyncio_loop(self) -> None:
        """
        This function start new event loop in new thread.
        """
        try:
            threading.Thread(target=HTTPSink.start_async_loop, args=(self,)).start()
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
