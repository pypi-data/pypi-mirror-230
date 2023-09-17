#!/usr/bin/env python3
"""
 rosbridge client for testing interface.

 enable logging to see debug messages
 `pytest --log-cli-level=debug`

 Copyright (c) 2022 ROX Automation - Jev Kuznetsov
"""


import asyncio
import json
import logging
import websockets

from roxbot.bridges.ws_bridge import WS_Bridge

PORT = 9999

# create and start server
bridge = WS_Bridge(port=PORT)
result = -1


# logging
log = logging.getLogger("bridge_test")


async def client():
    async with websockets.connect("ws://localhost:%i" % PORT) as websocket:  # type: ignore # pylint: disable=no-member
        # some invalid requests
        log.info("sending invalid requests")

        ## NOTE: test runs fine with logging enabled (pytest --log-cli-level=debug), but fails with logging disabled
        ##
        # await asyncio.sleep(0.1)
        # resp = await websocket.recv()
        # topic, data = json.loads(resp)
        # assert topic == "/log"

        for msg in [{"a": 1}, (2), [3], [4, 4, 4]]:
            await websocket.send(json.dumps(msg))

        # loopback test bridge -> client
        idx = 42
        bridge.send("loopback", idx)  # send data through bridge to itself.

        resp = await websocket.recv()
        topic, data = json.loads(resp)
        assert topic == "loopback"
        assert data == idx

        for idx in range(11):
            # command test
            await websocket.send(json.dumps(["/tst", idx]))
            # wait a bit
            await asyncio.sleep(0.01)
            assert result == idx


def example_cbk(data):
    global result  # pylint: disable=global-statement
    logging.info("callback called with %s", data)
    result = data


async def run_test():
    bridge.register_callback("/tst", example_cbk)
    bridge.add_log_handler(log, logging.DEBUG)

    await bridge.serve()

    await asyncio.wait_for(client(), timeout=1.0)


# ---------------- test functions


def test_server():
    asyncio.run(run_test())
    assert result == 10
