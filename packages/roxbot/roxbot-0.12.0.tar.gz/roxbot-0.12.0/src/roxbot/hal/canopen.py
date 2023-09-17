#!/usr/bin/env python3
"""
 HAL for  CAONpen devices. Work in progress.

 Copyright (c) 2023 ROX Automation - Jev Kuznetsov
"""
import asyncio
from .io import RemoteIO, DigitalIO, InputDirection


class RemoteIO_Mock(RemoteIO):
    """simulated remote IO device with 8 digital inputs"""

    def __init__(self, name: str, bridge=None) -> None:
        super().__init__(name, bridge)

        for _ in range(8):
            self.dio.append(DigitalIO(InputDirection.INPUT))

        self._coros.append(self._simulate_io)

    async def connect(self):
        """connect"""
        self._log.info("connecting to %s", self.name)
        await asyncio.sleep(1)
        self._connected = True
        self._log.info("connected to %s", self.name)

    async def disconnect(self):
        """disconnect"""
        self._log.info("disconnecting from %s", self.name)
        self._connected = False

    async def _simulate_io(self):
        """simulate IO as a binary counter"""
        counter = 0
        while self._connected:
            await asyncio.sleep(1)

            # Update the dio values based on the binary representation of the counter
            for i, dio in enumerate(self.dio):
                dio.value = (counter & (1 << i)) != 0

            # Increment the counter and wrap it if it reaches 256 (for 8 bits)
            counter = (counter + 1) % 256
