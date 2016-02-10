#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
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
from mocks import mock_event, MockSocket, MockSSLContext
from mocks import MockClock, MockEvent, MockDelaySocket
from pyrcb import IRCBot, IDefaultDict, IStr, ustr
from unittest import TestCase
from collections import Counter
import pyrcb
import unittest
import errno
import inspect
import socket
import ssl
import sys
import threading
import warnings

try:
    from unittest import mock
except ImportError:
    import mock


class BaseTest(TestCase):
    def setUp(self):
        # Patched classes will return the same instance every
        # time so the instances can be inspected.
        self.patch("socket.socket", new=MockSocket.get_mock_class())
        self.patch("ssl.SSLContext", new=MockSSLContext.get_mock_class())
        self.patch("ssl.match_hostname", spec=ssl.match_hostname)

    def patch(self, *args, **kwargs):
        patch_obj = mock.patch(*args, **kwargs)
        patch_obj.start()
        self.addCleanup(patch_obj.stop)

    # Loads data into the bot's socket to be returned later by recv().
    def from_server(self, *lines):
        self.bot.socket.from_server(
            "".join(line + "\r\n" for line in lines).encode("utf8"))

    # Clears data sent by the bot.
    def clear_sent(self):
        self.bot.socket.clear_data()

    # Causes the bot to handle the specified line, calling all events.
    def handle_line(self, line):
        self.bot._handle(line)

    def register_bot(self, nickname):
        self.from_server(":server 001 {0} :Welcome".format(nickname))
        self.bot.register(nickname)
        self.clear_sent()

    # Not all versions of mock have assertCountEqual().
    def assertCountEqual(self, first, second):
        if hasattr(super(BaseTest, self), "assertCountEqual"):
            return super(BaseTest, self).assertCountEqual(first, second)
        self.assertEqual(Counter(first), Counter(second))

    def assertCountEqualIStr(self, first, second):
        self.assertCountEqual(map(IStr, first), map(IStr, second))

    def assertCalled(self, *args, **kwargs):
        func, args = args[0], args[1:]
        self.assertIsNone(func.assert_called_with(*args, **kwargs))

    def assertCalledOnce(self, *args, **kwargs):
        func, args = args[0], args[1:]
        self.assertIsNone(func.assert_called_once_with(*args, **kwargs))

    def assertAnyCall(self, *args, **kwargs):
        func, args = args[0], args[1:]
        self.assertIsNone(func.assert_any_call(*args, **kwargs))

    def assertEventCalled(self, *args, **kwargs):
        event, args = args[0], args[1:]
        self.assertCalledOnce(event, *args, **kwargs)
        self.assertTrue(getattr(event, "event_called", False))

    # Asserts that the bot sent the specified lines of text.
    def assertSent(self, *lines):
        data = "".join(line + "\r\n" for line in lines).encode("utf8")
        self.assertEqual(self.bot.socket.get_data(), data)

    # Asserts that the bot is in the specified channels.
    def assertInChannels(self, *channels):
        for channel in channels:
            self.assertIn(channel, self.bot.channels)

    # Asserts that the bot is not in the specified channels.
    def assertNotInChannels(self, *channels):
        for channel in channels:
            self.assertNotIn(channel, self.bot.channels)

    # Asserts that a nickname is in a channel's nicklist.
    def assertInNicklist(self, nickname, channel):
        self.assertIn(nickname, self.bot.nicklist[channel])

    # Asserts that a nickname is not in a channel's nicklist.
    def assertNotInNicklist(self, nickname, channel):
        self.assertNotIn(nickname, self.bot.nicklist[channel])


class TestCommands(BaseTest):
    def setUp(self):
        super(TestCommands, self).setUp()
        self.bot = IRCBot(delay=False)
        self.bot.connect("example.com", 6667)
        self.register_bot("self")

    def test_password(self):
        self.bot.password("test-password")
        self.assertSent("PASS :test-password")

    def test_join(self):
        self.bot.join("#test-channel")
        self.assertSent("JOIN :#test-channel")

    def test_part(self):
        self.bot.part("#test")
        self.assertSent("PART :#test")
        self.bot.part("#test", "Part message")
        self.assertSent("PART #test :Part message")

    def test_quit(self):
        self.bot.quit()
        self.assertSent("QUIT")

    def test_quit_message(self):
        self.bot.quit("Quit message")
        self.assertSent("QUIT :Quit message")

    def test_send(self):
        self.bot.send("test-target", "Test message")
        self.assertSent("PRIVMSG test-target :Test message")

    def test_send_notice(self):
        self.bot.send_notice("test-target", "Test notice")
        self.assertSent("NOTICE test-target :Test notice")

    def test_send_split(self):
        message = " ".join(["test§"] * 100)

        # Should split on whitespace to avoid breaking words.
        self.bot.send("testnick", message)
        self.assertSent(
            "PRIVMSG testnick :" + " ".join(["test§"] * 58),
            "PRIVMSG testnick :" + " ".join(["test§"] * 42),
        )

        # Should break words.
        self.bot.send("testnick", message, nobreak=False)
        self.assertSent(
            "PRIVMSG testnick :" + " ".join(["test§"] * 58) + " test",
            "PRIVMSG testnick :" + "§ " + " ".join(["test§"] * 41),
        )

        # The nickname alone pushes the message over 512 bytes,
        # so the message should be sent without any splitting.
        self.bot.send("a" * 1000, "Test message")
        self.assertSent("PRIVMSG " + "a" * 1000 + " :Test message")

    def test_nick(self):
        self.bot.nick("new-test-nickname")
        self.assertSent("NICK :new-test-nickname")

    def test_names(self):
        self.bot.names("#test-channel")
        self.assertSent("NAMES :#test-channel")
        self.bot.names("")
        self.assertSent()

    def test_send_raw(self):
        self.bot.send_raw("TESTCOMMAND")
        self.assertSent("TESTCOMMAND")
        self.bot.send_raw("TESTCOMMAND", ["arg1", "arg2", "arg with spaces"])
        self.assertSent("TESTCOMMAND arg1 arg2 :arg with spaces")


class TestEvents(BaseTest):
    def setUp(self):
        super(TestEvents, self).setUp()
        self.bot = IRCBot(delay=False)
        self.bot.connect("example.com", 6667)
        self.register_bot("self")
        self.bot.add_nickname("self", ["#test1", "#test2"])
        self.bot.add_nickname("user1", ["#test1", "#test2"])
        self.bot.add_nickname("user2", ["#test1", "#test2"])

    def test_on_ping(self):
        self.handle_line("PING :test")
        self.assertSent("PONG :test")

    def test_on_join(self):
        @mock_event(self.bot, "on_join")
        def on_join(nickname, channel):
            self.assertInNicklist(nickname, channel)
        self.handle_line(":newuser JOIN #test2")
        self.assertEventCalled(on_join, "newuser", "#test2")

    def test_on_join_self(self):
        @mock_event(self.bot, "on_join")
        def on_join(nickname, channel):
            self.assertInChannels(channel)
            self.assertInNicklist(nickname, channel)
        self.handle_line(":self JOIN #newchannel")
        self.assertEventCalled(on_join, "self", "#newchannel")

    def test_on_part(self):
        @mock_event(self.bot, "on_part")
        def on_part(nickname, channel, message):
            self.assertNotInNicklist(nickname, channel)
        self.handle_line(":user2 PART #test1 :Part message")
        self.assertEventCalled(on_part, "user2", "#test1", "Part message")

    def test_on_part_self(self):
        @mock_event(self.bot, "on_part")
        def on_part(nickname, channel, message):
            self.assertNotInChannels(channel)
        self.handle_line(":self PART #test1")
        self.assertEventCalled(on_part, "self", "#test1", None)

    def test_on_quit(self):
        @mock_event(self.bot, "on_quit")
        def on_quit(nickname, message, channels):
            self.assertEqual([nickname, message], ["user2", "Quit message"])
            self.assertCountEqualIStr(channels, ["#test1", "#test2"])
        self.handle_line(":user2 QUIT :Quit message")
        self.assertEqual(on_quit.call_count, 1)

    def test_on_quit_self(self):
        @mock_event(self.bot, "on_quit")
        def on_quit(nickname, message, channels):
            self.assertEqual([nickname, message], ["self", "Quit message"])
            self.assertCountEqualIStr(channels, ["#test1", "#test2"])
            self.assertNotInChannels("#test1", "#test2")
        self.handle_line(":self QUIT :Quit message")
        self.assertEqual(on_quit.call_count, 1)

    def test_on_kick(self):
        @mock_event(self.bot, "on_kick")
        def on_kick(nickname, channel, target, message):
            self.assertNotIn(target, channel)
            self.assertInNicklist(nickname, channel)
        self.handle_line(":user2 KICK #test1 user1 :Message")
        self.assertEventCalled(on_kick, "user2", "#test1", "user1", "Message")

    def test_on_kick_self(self):
        @mock_event(self.bot, "on_kick")
        def on_kick(nickname, channel, target, message):
            self.assertNotInChannels(channel)
        self.handle_line(":user2 KICK #test1 self")
        self.assertEventCalled(on_kick, "user2", "#test1", "self", None)

    def test_on_message(self):
        @mock_event(self.bot, "on_message")
        def on_message(message, nickname, channel, is_query):
            pass
        self.handle_line(":user2 PRIVMSG #test1 :Message")
        self.assertEventCalled(on_message, "Message", "user2", "#test1", False)

    def test_on_message_query(self):
        @mock_event(self.bot, "on_message")
        def on_message(message, nickname, channel, is_query):
            pass
        self.handle_line(":user2 PRIVMSG self :Query")
        self.assertEventCalled(on_message, "Query", "user2", None, True)

    def test_on_notice(self):
        @mock_event(self.bot, "on_notice")
        def on_notice(message, nickname, channel, is_query):
            pass
        self.handle_line(":user2 NOTICE #test1 :Notice")
        self.assertEventCalled(on_notice, "Notice", "user2", "#test1", False)

    def test_on_notice_query(self):
        @mock_event(self.bot, "on_notice")
        def on_notice(message, nickname, channel, is_query):
            pass
        self.handle_line(":user2 NOTICE self :Query")
        self.assertEventCalled(on_notice, "Query", "user2", None, True)

    def test_on_nick(self):
        @mock_event(self.bot, "on_nick")
        def on_nick(nickname, new_nickname):
            self.assertNotInNicklist(nickname, "#test2")
            self.assertInNicklist(new_nickname, "#test2")
        self.handle_line(":user1 NICK :user1-new")
        self.assertEventCalled(on_nick, "user1", "user1-new")

    def test_on_nick_self(self):
        @mock_event(self.bot, "on_nick")
        def on_nick(nickname, new_nickname):
            self.assertNotInNicklist(nickname, "#test2")
            self.assertInNicklist(new_nickname, "#test2")
            self.assertEqual(self.bot.nickname, new_nickname)
        self.handle_line(":self NICK :self-new")
        self.assertEventCalled(on_nick, "self", "self-new")

    def test_on_names(self):
        @mock_event(self.bot, "on_names")
        def on_names(channel, names):
            self.assertCountEqualIStr(self.bot.nicklist[channel], names)
            self.assertCountEqualIStr(names, ["a", "b", "self"])
        self.handle_line(":server 353 self = #test1 :@a +b self")
        self.handle_line(":server 366 self #test1 :End of names")
        self.assertEqual(on_names.call_count, 1)

    def test_on_names_empty(self):
        @mock_event(self.bot, "on_names")
        def on_names(channel, names):
            pass
        self.handle_line(":server 366 self #test1 :End of names")
        self.assertEventCalled(on_names, "#test1", [])

    def test_on_raw(self):
        @mock_event(self.bot, "on_raw")
        def on_raw(nickname, command, args):
            pass
        self.handle_line(":nick COMMAND arg1 arg2 :arg with spaces")
        self.assertEventCalled(
            on_raw, "nick", "COMMAND", ["arg1", "arg2", "arg with spaces"])

    def test_register_event(self):
        # Can't use mocks because IRCBot._handle() looks up the function
        # signatures of event handlers.
        def handler1(nickname, arg1, arg2):
            handler1.call_args = [nickname, arg1, arg2]

        def handler2(self, nickname, arg1, arg2, arg3):
            handler2.call_args = [nickname, arg1, arg2, arg3]

        bound = handler2.__get__(self.bot)
        self.bot.register_event(handler1, "CUSTOMCMD")
        self.bot.register_event(bound, "CUSTOMCMD")
        self.handle_line(":nick CUSTOMCMD a1 :a2")
        self.assertEqual(handler1.call_args, ["nick", "a1", "a2"])
        self.assertEqual(handler2.call_args, ["nick", "a1", "a2", None])

    def test_register_event_no_signature(self):
        if hasattr(inspect, "signature"):
            with mock.patch.object(inspect, "signature"):
                del inspect.signature
                with warnings.catch_warnings(record=True):
                    self.test_register_event()


class TestConnect(BaseTest):
    def setUp(self):
        super(TestConnect, self).setUp()
        self.bot = IRCBot(delay=False)

    def test_connect(self):
        self.bot.connect("example.com", 6667)
        self.assertEqual(self.bot.hostname, "example.com")
        self.assertEqual(self.bot.port, 6667)
        self.bot.socket.connect.assert_called_once_with(("example.com", 6667))

    def test_connect_ssl(self):
        self.bot.connect("example.com", 6697, use_ssl=True)
        context = ssl.SSLContext()
        peercert = self.bot.socket.getpeercert()
        load_default_certs = getattr(
            context, "load_default_certs", context.set_default_verify_paths)
        self.assertCalledOnce(context.wrap_socket, socket.socket())
        self.assertCalledOnce(load_default_certs)
        self.assertCalledOnce(ssl.match_hostname, peercert, "example.com")

    def test_connect_ssl_ca_certs(self):
        self.bot.connect("example.com", 6697, use_ssl=True, ca_certs="/test")
        context = ssl.SSLContext()
        self.assertCalledOnce(context.load_verify_locations, cafile="/test")

    def test_register(self):
        self.from_server(":server 001 test-nickname :Welcome")
        self.bot.register("test-nickname")
        self.assertSent(
            "USER test-nickname 8 * :test-nickname",
            "NICK :test-nickname")

    def test_register_realname(self):
        self.from_server(":server 001 test-nickname :Welcome")
        self.bot.register("test-nickname", "test-realname")
        self.assertSent(
            "USER test-nickname 8 * :test-realname",
            "NICK :test-nickname")

    def test_register_nickname_in_use(self):
        self.from_server(":server 433 * test-nickname :Nickname in use")
        with self.assertRaises(ValueError):
            self.bot.register("test-nickname")

    def test_register_connection_lost(self):
        self.from_server()
        with self.assertRaises(IOError):
            self.bot.register("test-nickname")

    def test_reuse(self):
        self.bot.connect("example.com", 6667)
        self.register_bot("test")
        self.assertTrue(self.bot.is_registered)

        self.bot.quit()
        self.bot.connect("example.org", 6667)
        self.assertFalse(self.bot.is_registered)


class TestListen(BaseTest):
    def setUp(self):
        super(TestListen, self).setUp()
        self.bot = IRCBot(delay=False)
        self.bot.connect("example.com", 6667)
        self.register_bot("self")

    def test_listen(self):
        @mock_event(self.bot, "on_raw")
        def on_raw(nickname, command, args):
            pass
        self.from_server(":self COMMAND1")
        self.from_server(":self COMMAND2")
        # Make recv() return an empty string, causing listen() to return.
        self.from_server()
        self.bot.listen()

        self.assertEqual(on_raw.call_count, 2)
        self.assertAnyCall(on_raw, "self", "COMMAND1", [])
        self.assertAnyCall(on_raw, "self", "COMMAND2", [])

    def test_listen_async(self):
        @mock_event(self.bot, "on_raw")
        def on_raw(nickname, command, args):
            pass
        self.from_server(":self COMMAND1")
        self.from_server(":self COMMAND2")
        # Make recv() return an empty string, causing listen() to return.
        self.from_server()

        callback = mock.Mock(spec=[])
        self.bot.listen_async(callback)
        self.bot.wait()

        self.assertEqual(on_raw.call_count, 2)
        self.assertAnyCall(on_raw, "self", "COMMAND1", [])
        self.assertAnyCall(on_raw, "self", "COMMAND2", [])
        self.assertCalled(callback)

    def test_socket_error_caught(self):
        error = socket.error(errno.ECONNRESET, "Test exception")
        self.bot.readline = mock.Mock(side_effect=error)
        self.bot.listen()

    def test_other_error_uncaught(self):
        error = socket.error(errno.EPERM, "Test exception")
        self.bot.readline = mock.Mock(side_effect=error)
        with self.assertRaises(socket.error):
            self.bot.listen()


class TestDelay(BaseTest):
    def setUp(self):
        super(TestDelay, self).setUp()
        mock_clock = MockClock()
        self.patch("pyrcb.best_clock", new=mock_clock),

        self.bot = IRCBot(delay=False)
        self.bot.socket = MockDelaySocket(mock_clock)
        self.bot.delay_event = MockEvent(mock_clock, self.bot)

    def test_delay(self):
        self.bot.connect("example.com", 6667)
        self.register_bot("self")
        self.bot.delay = True
        for i in range(30):
            self.bot.send("test", "Message {0}".format(i))

        self.bot.delay_loop()
        self.assertEqual(len(self.bot.socket.received_messages), 30)
        time = 0
        for i, msg_tuple in enumerate(self.bot.socket.received_messages):
            msg = "PRIVMSG test :Message {0}\r\n".format(i).encode("utf8")
            time += min(i * self.bot.delay_multiplier, self.bot.max_delay)
            self.assertEqual(msg_tuple[0], msg)
            self.assertAlmostEqual(msg_tuple[1], time)

    def test_consecutive(self):
        self.bot.connect("example.com", 6667)
        self.register_bot("self")
        self.bot.delay = True
        for i in range(30):
            self.bot.send("test", "Message")

        last_time, consecutive = self.bot.last_sent["test"]
        self.assertEqual(consecutive, 30)

        pyrcb.best_clock.time = last_time + self.bot.consecutive_timeout
        self.bot.send("test", "Message")
        last_time, consecutive = self.bot.last_sent["test"]
        self.assertEqual(consecutive, 1)

    def test_delay_thread(self):
        self.bot.delay = True
        self.patch("threading.Thread")
        self.bot.connect("example.com", 6667)
        self.assertCalled(threading.Thread, target=self.bot.delay_loop)


class TestMisc(BaseTest):
    def test_format(self):
        self.assertEqual(IRCBot.format("CMD"), "CMD")
        self.assertEqual(IRCBot.format("CMD", ["a:", "b c"]), "CMD a: :b c")
        with self.assertRaises(ValueError):
            IRCBot.format("CMD", ["arg", ""])
        with self.assertRaises(ValueError):
            IRCBot.format("", ["arg"])
        with self.assertRaises(ValueError):
            IRCBot.format("CMD$", ["arg"])
        with self.assertRaises(ValueError):
            IRCBot.format("CMD", "Invalid\nCharacters")
        with self.assertRaises(ValueError):
            IRCBot.format("CMD", [":arg1", "arg2"])
        with self.assertRaises(ValueError):
            IRCBot.format("CMD", ["arg one", "arg two"])

    def test_split_message(self):
        split = IRCBot.split_string("test§ test", 10)
        self.assertEqual(split, ["test§", "test"])
        split = IRCBot.split_string("test§ test", 6)
        self.assertEqual(split, ["test§", "test"])
        split = IRCBot.split_string("test§test", 5)
        self.assertEqual(split, ["test", "§tes", "t"])
        split = IRCBot.split_string("test§§  test", 10)
        self.assertEqual(split, ["test§§ ", "test"])
        with self.assertRaises(ValueError):
            IRCBot.split_string("test", 0)

    def test_safe_message_length(self):
        self.bot = IRCBot()
        self.bot.nickname = "self"
        # :self!<user>@<host> PRIVMSG testnick :<message>\r\n
        # <user> is max 10 bytes, <host> is max 63 bytes
        # 411 bytes left for <message>
        self.assertEqual(self.bot.safe_message_length("testnick"), 411)

    def test_debug_print(self):
        self.bot = IRCBot(debug_print=True)
        self.from_server(":test CMD :arg")
        with mock.patch("pyrcb.print", create=True):
            self.bot.readline()
            self.assertCalled(pyrcb.print, ":test CMD :arg", file=sys.stdout)
            self.bot.writeline("CMD :arg")
            self.assertCalled(pyrcb.print, ">>> CMD :arg", file=sys.stdout)

    def test_close_socket(self):
        self.bot = IRCBot()
        self.bot.close_socket()
        self.assertCalled(self.bot.socket.shutdown, socket.SHUT_RDWR)
        self.assertCalled(self.bot.socket.close)

    def test_close_socket_error_caught(self):
        self.bot = IRCBot()
        error = socket.error(errno.ENOTCONN, "Test message")
        self.bot.socket.shutdown = mock.Mock(side_effect=error)
        self.bot.close_socket()

    def test_close_socket_error_uncaught(self):
        self.bot = IRCBot()
        error = socket.error(errno.EPERM)
        self.bot.socket.close = mock.Mock(side_effect=error)
        with self.assertRaises(socket.error):
            self.bot.close_socket()

    def test_istr(self):
        self.assertEqual(IStr("TEST~"), "Test^")
        self.assertEqual("TEST~", IStr("Test^"))
        self.assertEqual(repr(IStr("Test")), "IStr(" + repr("Test") + ")")

        if sys.version_info.major == 2:
            self.assertEqual("TEST~", IStr(b"Test^"))
            self.assertEqual(b"TEST~", IStr("Test^"))

        self.assertEqual(ustr(IStr("TEST~")), "TEST~")
        self.assertNotEqual(ustr(IStr("TEST~")), "Test^")
        self.assertEqual(IStr("Test^").lower(), "test^")
        self.assertEqual(IStr("Test^").upper(), "TEST~")

    def test_idefaultdict(self):
        d = IDefaultDict(int)
        d["Test^"] = 10
        d["TEST~"] += 5
        self.assertEqual(d["TEST~"], 15)
        self.assertEqual(str(list(d.keys())[0]), "Test^")

    def test_idefaultdict_order(self):
        d = IDefaultDict()
        keys = "qwertyuiopasdfghjklzxcvbnm"
        for key in keys:
            d[key] = 0
        self.assertEqual("".join(list(d.keys())), keys)

    def test_idefaultdict_missing(self):
        d = IDefaultDict()
        with self.assertRaises(KeyError):
            d["test"]

if __name__ == "__main__":
    unittest.main()
