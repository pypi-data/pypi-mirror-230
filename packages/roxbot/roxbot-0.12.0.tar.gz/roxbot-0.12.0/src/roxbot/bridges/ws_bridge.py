#!/usr/bin/env python3
"""
Simple websocket bridge for interfacing with ui etc.

Copyright (c) 2023 ROX Automation - Jev Kuznetsov

**Protocol definition**

`(dest, data)`
* `dest` is a string, topic to post on
* `data` is a json serializable object

** how it works **

* sending: `WS_Bridge.send(dest, data)` to send data to topic on all connected clients
* receiving: add callbacks with `WS_Bridge.register_callback(dest, fcn)`. On incomng data the bridge will execute `fcn(data)`
* forwarding log messages: `WS_Brige.add_log_handler(log)` to forward log messages to `/log` topic


"""

import asyncio
import json
import logging
from logging.handlers import QueueHandler
from typing import List, Optional, Set, Union, Dict

import websockets

from roxbot.topics import Topics

from .base import Bridge

DEFAULT_PORT = 9095

Q_LENGTH = 50

log = logging.getLogger()

# set websockets logging level to info
logging.getLogger("websockets").setLevel(logging.INFO)


class WS_Bridge(Bridge):
    """websocket bridge for interfacing with ui etc."""

    def __init__(self, listen_on: str = "0.0.0.0", port: int = DEFAULT_PORT):
        super().__init__()
        self._log = logging.getLogger("ws_bridge")

        self._host = listen_on
        self._port = port
        self._log_topic = Topics.log

        self._connections: Set = set()  # all current connections
        self._tasks: List = []  # keep running tasks to avoid garbage collection

        self._out_q: asyncio.Queue = asyncio.Queue(Q_LENGTH)

        # logging queue
        self._log_q: asyncio.Queue = asyncio.Queue(Q_LENGTH)
        self._log_handler: Optional[QueueHandler] = None

    async def _handle_connection(self, websocket):
        """pass this to websockets.serve"""
        self._log.debug("Established connection")

        self._connections.add(websocket)
        self._tasks.append(asyncio.create_task(self._receive_handler(websocket)))

        try:
            await websocket.wait_closed()
        finally:
            self._connections.remove(websocket)

    async def _handle_logging(self):
        """handle logging messages"""
        formatter = logging.Formatter(
            fmt="%(asctime)s [%(name)s] %(levelname)s %(message)s", datefmt="%H:%M:%S"
        )

        while True:
            item = await self._log_q.get()
            msg = formatter.format(item)
            self.send(self._log_topic, msg)
            self._log_q.task_done()

    async def _receive_handler(self, websocket):
        """handle incoming messages"""
        async for message in websocket:
            self._log.debug("<%s", message)
            try:
                d = json.loads(message)
                assert isinstance(d, list), f"Expected list, got {type(d)}"
                assert len(d) == 2, f"Expected list of length 2, got {len(d)}"

                topic = d[0]
                assert topic in self._callbacks, f"No callback for topic {topic}"

                data = d[1]

                # run callback
                self._log.info("Received topic=%s data=%s", topic, data)
                self._callbacks[topic](data)

            except json.JSONDecodeError:
                self._log.warning("Could not parse %s", message)
            except AssertionError as e:
                self._log.warning("%s", e)
            except Exception as e:  # pylint: disable=broad-except
                # print exception traceback
                self._log.exception(e)

    async def _send_messages(self):
        """send queque items to clients"""

        while True:
            msg = await self._out_q.get()

            if self._connections:
                self._log.debug(">%s", msg)
                websockets.broadcast(self._connections, msg)  # type: ignore # pylint: disable=no-member
            else:
                self._log.debug("Dropped %s", msg)

            self._log.debug("queue length = %s", self._out_q.qsize())
            self._out_q.task_done()

    def send(self, topic: Union[str, Dict], data):
        """send data to topic"""
        self._log.debug("Sending topic=%s data=%s", topic, data)
        msg = json.dumps((topic, data))

        self._out_q.put_nowait(msg)

    def add_log_handler(self, logger: logging.Logger, level: int = logging.INFO):
        """add log handler to logger, this wil forward all logs to the client via the bridge"""
        self._log_handler = QueueHandler(self._log_q)  # type: ignore
        self._log_handler.setLevel(level)
        logger.addHandler(self._log_handler)

    async def serve(self):
        """start bridge server"""

        await websockets.serve(self._handle_connection, self._host, self._port)  # type: ignore # pylint: disable=no-member
        self._tasks.append(asyncio.create_task(self._send_messages()))
        self._tasks.append(asyncio.create_task(self._handle_logging()))

    def stop(self):
        """stop bridge server"""
        for task in self._tasks:
            task.cancel()


async def echo(host="localhost", port=DEFAULT_PORT):
    """echo all data received on port"""

    async with websockets.connect(f"ws://{host}:{port}") as websocket:  # type: ignore # pylint: disable=no-member
        async for message in websocket:
            print(message)
