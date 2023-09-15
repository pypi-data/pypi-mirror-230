import logging
import pickle
import time

import pytest
import zmq
from zmq.error import Again
from zmq.error import ContextTerminated
from zmq.error import InterruptedSystemCall
from zmq.error import ZMQError

from egse.command import ClientServerCommand
from egse.command import CommandExecution
from egse.proxy import Proxy

LOGGER = logging.getLogger(__name__)


class ReturnCommandString(ClientServerCommand):
    def execute(self, cmd_string):
        return f'{self.__class__.__name__}({self._name}) executing "{cmd_string}"'


class MySocket:
    def __init__(self, type_):
        self._state = "closed"
        self._last_send_obj = None
        self.closed = True
        LOGGER.info(f"Initialise MySocket of type {type_}")

    def connect(self, endpoint):
        self._state = "connected"
        self.closed = False
        LOGGER.info(f"MySocket.connect('{endpoint}')")

    def send(self, obj):
        LOGGER.info(f"MySocket.send({type(obj)})")
        self._last_send_obj = pickle.loads(obj)

    def recv(self):
        LOGGER.info("MySocket.recv()")
        if isinstance(self._last_send_obj, CommandExecution):
            if self._last_send_obj.get_name() == "Ping":
                return pickle.dumps("Pong")
            if self._last_send_obj.get_name() == "send_commands":
                return pickle.dumps(
                    {"return_cmd_str": ReturnCommandString(name="print", cmd="return_cmd_str")}
                )
        if isinstance(self._last_send_obj, str):
            if self._last_send_obj == "Ping":
                return pickle.dumps("Pong")
            if self._last_send_obj == "send_commands":
                return pickle.dumps(
                    {"return_cmd_str": ReturnCommandString(name="print", cmd="return_cmd_str")}
                )
        return pickle.dumps("anything")

    def setsockopt(self, name, value):
        LOGGER.info(f"MySocket.setsockopt({name}, {value})")

    def close(self):
        self._state = "closed"
        self.closed = True
        LOGGER.info("MySocket.close()")


class MyPoller:
    def __init__(self):
        self._registered = {}

    def register(self, socket, type_):
        LOGGER.info(f"MyPoller.register({socket}, {type_})")
        self._registered[socket] = True

    def unregister(self, socket):
        del self._registered[socket]

    def poll(self, timeout):
        LOGGER.info(f"MyPoller.poll({timeout})")
        return self._registered


def return_my_socket():
    return MySocket


def test_proxy_constructor(monkeypatch):

    monkeypatch.setattr(zmq.Context, "socket", MySocket)
    monkeypatch.setattr(zmq, "Poller", MyPoller)

    proxy = Proxy(endpoint="fake endpoint")

    assert proxy.is_cs_connected()


def test_connect(monkeypatch):
    def connect_raises_isc_exc(self, endpoint):
        # This returns the following:
        # zmq.error.InterruptedSystemCall: Interrupted system call:
        # This call should have been retried. Please report this to pyzmq.
        raise InterruptedSystemCall()

    def connect_raises_again_exc(self, endpoint):
        # The message here is: zmq.error.Again: Resource temporarily unavailable
        raise Again()

    def connect_raises_ctx_term(self, endpoint):
        # The message here is: zmq.error.ContextTerminated: Context was terminated
        raise ContextTerminated()

    def connect_raises_zmq_error(self, endpoint):
        # The message here is: zmq.error.ZMQError: Undefined error: 0
        raise ZMQError()

    monkeypatch.setattr(zmq.Context, "socket", MySocket)
    monkeypatch.setattr(zmq, "Poller", MyPoller)

    for f, exc in [
        (connect_raises_isc_exc, InterruptedSystemCall),
        (connect_raises_again_exc, Again),
        (connect_raises_ctx_term, ContextTerminated),
        (connect_raises_zmq_error, ZMQError),
    ]:
        monkeypatch.setattr(MySocket, "connect", f)
        with pytest.raises(exc):
            proxy = Proxy(endpoint="fake endpoint")
            assert proxy.is_cs_connected()


def test_simulate_timeout(monkeypatch):
    def poll_returns_empty_dict(self, timeout):
        time.sleep(timeout / 1000)
        return {}

    monkeypatch.setattr(zmq.Context, "socket", MySocket)
    monkeypatch.setattr(zmq, "Poller", MyPoller)

    proxy = Proxy(endpoint="fake endpoint")
    assert proxy.is_cs_connected()

    # now fake the timeout

    monkeypatch.setattr(MyPoller, "poll", poll_returns_empty_dict)

    # this ping() will send a 'Ping' and then  have a timeout and retry until
    # the number of retries are exhausted and the proxy shall be disconnected
    # on return

    proxy.ping()

    assert not proxy.is_cs_connected()

    # this is the only way to remove the monkey patched 'poll' method

    monkeypatch.undo()

    monkeypatch.setattr(zmq.Context, "socket", MySocket)
    monkeypatch.setattr(zmq, "Poller", MyPoller)

    proxy.reconnect_cs()
    assert proxy.is_cs_connected()


@pytest.mark.skip("I'm working on this test.")
def test_dry_run(monkeypatch):

    monkeypatch.setattr(zmq.Context, "socket", MySocket)
    monkeypatch.setattr(zmq, "Poller", MyPoller)

    proxy = Proxy(endpoint="fake endpoint")

    assert proxy.is_cs_connected()

    assert proxy.get_commands() == []

    class HexapodCommand(ClientServerCommand):
        pass

    my_cmd = HexapodCommand(name="MyCommand", cmd="my_cmd {} {}")

    proxy._commands = [my_cmd]
    proxy._add_commands()

    assert proxy.get_commands() == []


def test_context_manager(monkeypatch):

    monkeypatch.setattr(zmq.Context, "socket", MySocket)
    monkeypatch.setattr(zmq, "Poller", MyPoller)

    with Proxy(endpoint="fake endpoint") as proxy:
        assert proxy.is_cs_connected()
        assert proxy.ping()

    # is_cs_connected() does a ping() which does a reconnect_cs()
    # so, this should be True with the Mocker class.

    assert proxy.is_cs_connected()
