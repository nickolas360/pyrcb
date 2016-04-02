# Copyright (C) 2016 nickolas360 <contact@nickolas360.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from __future__ import print_function
from __future__ import unicode_literals
import pyrcb
import socket
import ssl
import threading

try:
    from queue import Queue
except ImportError:
    from Queue import Queue

try:
    from unittest import mock
except ImportError:
    import mock


# Wraps an IRCBot event in a mock.
def mock_event(bot=None, event_name=None):
    def decorator(func):
        def wrapped(*args, **kwargs):
            func(*args, **kwargs)
            result.event_called = True
        result = mock.Mock(spec=wrapped, wraps=wrapped)
        if bot and event_name:
            setattr(bot, event_name, result)
        return result
    return decorator


# Returns a mock of socket.create_connection().
def get_mock_create_connection(instance=None):
    if instance is None:
        instance = MockSocket()

    def result(address, *args):
        instance.connect(address)
        return instance
    return result


class BaseMock(mock.NonCallableMock):
    # Override in subclasses.
    spec = None

    def __init__(self, spec=None, **kwargs):
        spec = spec or self.spec
        super(BaseMock, self).__init__(spec=spec, **kwargs)

    def wrap_mock(self, *names):
        for name in names:
            method = getattr(self, name)
            mock_method = mock.Mock(spec=method, side_effect=method)
            setattr(self, name, mock_method)

    @classmethod
    def get_mock_class(cls, instance=None, spec=None):
        spec = spec or cls.spec
        instance = instance or cls(spec=spec)
        mock_cls = mock.Mock(spec=spec, return_value=instance)
        return mock_cls


class MockSocket(BaseMock):
    _socket = socket.socket
    spec = _socket

    def __init__(self, **kwargs):
        super(MockSocket, self).__init__(**kwargs)
        self.wrap_mock("connect", "recv", "sendall", "shutdown")
        self.data = b""
        self.recv_data = Queue()
        self.recv_buffer = b""
        self.alive = False

    # Gets data that was passed to send() or sendall().
    def get_data(self):
        data = self.data
        self.clear_data()
        return data

    # Clears data that was passed to send() or sendall().
    def clear_data(self):
        self.data = b""

    # Loads data (a byte string) to be returned by recv().
    def from_server(self, data):
        self.recv_data.put(data)

    def connect(self, address):
        self.alive = True

    # Returns pre-loaded data.
    def recv(self, length, *args):
        if not (self.alive or self.recv_buffer) and self.recv_data.empty():
            return b""
        data = self.recv_buffer or self.recv_data.get()
        if not data:
            self.alive = False
            return b""
        data, self.recv_buffer = data[:length], data[length:]
        return data

    def send(self, data):
        self.data += data
        return len(data)

    def sendall(self, data):
        self.data += data

    def shutdown(self, mode):
        self.alive = False


class MockSSLContext(BaseMock):
    _SSLContext = ssl.SSLContext
    _SSLSocket = ssl.SSLSocket
    spec = _SSLContext

    def __init__(self, **kwargs):
        super(MockSSLContext, self).__init__(**kwargs)
        self.wrap_mock("wrap_socket")

    def wrap_socket(self, sock, *args, **kwargs):
        return MockSocket(spec=self._SSLSocket)


class MockClock(BaseMock):
    _best_clock = pyrcb.best_clock
    spec = _best_clock

    def __init__(self, **kwargs):
        super(MockClock, self).__init__(**kwargs)
        self.time = 0

    def __call__(self):
        return self.time


class MockEvent(BaseMock):
    # Event object needs to be instantiated because threading.Event
    # is a function, not a class, in Python 2.
    _Event = type(threading.Event())
    spec = _Event

    def __init__(self, clock, bot, **kwargs):
        super(MockEvent, self).__init__(**kwargs)
        self.wrap_mock("wait")
        self.clock = clock
        self.bot = bot
        self.times = []

    # Increases the time of the associated MockClock instead of sleeping.
    def wait(self, timeout=None):
        if timeout:
            self.clock.time += timeout
            return
        # Set alive to false so IRCBot.delay_loop() stops.
        self.bot.alive = False


# Like MockSocket, but also stores when messages were
# received (using the time reported by a MockClock).
class MockDelaySocket(MockSocket):
    def __init__(self, clock, **kwargs):
        super(MockDelaySocket, self).__init__(**kwargs)
        self.clock = clock
        self.received_messages = []

    def sendall(self, data):
        super(MockDelaySocket, self).sendall(data)
        self.received_messages.append((data, self.clock.time))

    def clear_data(self):
        super(MockDelaySocket, self).clear_data()
        self.received_messages = []
