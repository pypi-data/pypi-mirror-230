import logging
from enum import IntEnum
from typing import Any

from egse.decorators import dynamic_interface

LOGGER = logging.getLogger(__name__)

class EVENT_ID(IntEnum):
    ALL = 0
    SETUP = 1

class Event:
    def __init__(self, event_id: int, context: Any):
        self.id = event_id
        self.context = context
    def __repr__(self):
        return f"Event({self.id}, {self.context})"


class EventInterface:
    @dynamic_interface
    def handle_event(self, event: Event):
        ...

class Listeners:
    def __init__(self):
        self._listeners: dict[str, dict] = {}

    def __len__(self):
        return len(self._listeners)

    def add_listener(self, listener: dict):
        """
        The argument is a dictionary with the following expected content:

         * name (str): the name of the process
         * proxy (str): the proxy class

        Args:
            listener: a dictionary with properties of the listener

        Raises:
            ValueError if the listener already exists.
        """
        try:
            listener_name = listener["name"]
        except KeyError as exc:
            raise ValueError(f"Expected 'name' key in listener argument {listener}.") from exc

        if listener_name in self._listeners:
            raise ValueError(f"Process {listener_name} is already registered as a listener.")

        self._listeners[listener_name] = listener

    def remove_listener(self, listener: dict):
        try:
            listener_name = listener["name"]
        except KeyError as exc:
            raise ValueError(f"Expected 'name' key in listener argument {listener}.") from exc

        try:
            del self._listeners[listener_name]
        except KeyError as exc:
            raise ValueError(f"Process {listener_name} cannot be removed, not registered.") from exc

    def notify_listeners(self, event: Event):
        for name, listener in self._listeners.items():
            proxy = listener['proxy']
            LOGGER.info(f"Notifying process {name} of {event.context or {}} on {event.id=}")
            with proxy() as pobj:
                rc = pobj.handle_event(event)
            LOGGER.info(f"{rc=}")
