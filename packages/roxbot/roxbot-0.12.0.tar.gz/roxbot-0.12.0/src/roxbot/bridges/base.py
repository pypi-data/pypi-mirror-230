#!/usr/bin/env python3
"""
 base classes for roxbot.
 Provides interface definitions for bridges, drivers etc.

 Copyright (c) 2023 ROX Automation - Jev Kuznetsov
"""
from typing import Callable, Dict
from abc import ABC, abstractmethod


class Bridge(ABC):
    """base class for creating websocket bridges"""

    def __init__(self) -> None:
        self._callbacks: Dict = {}  # receive data callbacks

    @abstractmethod
    def send(self, topic: str, data):
        """send data to topic

        Args:
            topic (str): topic to post on
            data (any): json serializable data payload
        """

    def register_callback(self, topic: str, fcn: Callable):
        """add callback to topic."""
        assert (
            topic not in self._callbacks
        ), f"topic {topic} already has a callback registered"

        self._callbacks[topic] = fcn

    def remove_callback(self, topic: str):
        """remove topic callback"""
        del self._callbacks[topic]

    @abstractmethod
    async def serve(self):
        """start serving, implement required tasks here"""
