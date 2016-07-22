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
from mocks import mock_event, get_mock_create_connection, MockSocket
from mocks import MockSSLContext, MockClock, MockEvent, MockDelaySocket
from pyrcb import IRCBot, IDefaultDict, IStr, ISet, ustr
from pyrcb import UserHostInfo, VoiceOpInfo
from unittest import TestCase
import pyrcb
import unittest
import errno
import inspect
import socket
import ssl
import sys
import threading
import traceback
import warnings

try:
    from unittest import mock
except ImportError:
    import mock


class BaseTest(TestCase):
    def patch(self, *args, **kwargs):
        patch_obj = mock.patch(*args, **kwargs)
        patch_obj.start()
        self.addCleanup(patch_obj.stop)

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


class BaseBotTest(BaseTest):
    def setUp(self):
        # Patched classes will return the same instance every
        # time so the instances can be inspected.
        self.mock_socket = MockSocket()
        self.patch("ssl.SSLContext", new=MockSSLContext.get_mock_class())
        self.patch("ssl.match_hostname", spec=ssl.match_hostname)
        self.patch("socket.create_connection", spec=socket.create_connection,
                   side_effect=get_mock_create_connection(self.mock_socket))

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


class TestCommands(BaseBotTest):
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


class TestEvents(BaseBotTest):
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
            nickname = self.bot.nicklist[channel][nickname]
            self.assertEqual(nickname.is_voiced, False)
            self.assertEqual(nickname.is_op, False)
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
            self.assertEqual(channels, {"#test1", "#test2"})
        self.handle_line(":user2 QUIT :Quit message")
        self.assertEqual(on_quit.call_count, 1)

    def test_on_quit_self(self):
        @mock_event(self.bot, "on_quit")
        def on_quit(nickname, message, channels):
            self.assertEqual([nickname, message], ["self", "Quit message"])
            self.assertEqual(channels, {"#test1", "#test2"})
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
            self.assertEqual(list(self.bot.nicklist[channel].values()), names)
            self.assertEqual(names, ["a", "user1", "self"])

            # name -> (is_voiced, is_op)
            correct = IDefaultDict(None, {
                "a": (False, True),
                "user1": (True, False),
                "self": (False, False),
            })

            nicklist = self.bot.nicklist[channel]
            for name in names:
                self.assertEqual(name.is_voiced, correct[name][0])
                self.assertEqual(name.is_op, correct[name][1])
                self.assertEqual(name.is_voiced, nicklist[name].is_voiced)
                self.assertEqual(name.is_op, nicklist[name].is_op)

        self.handle_line(":server 353 self = #test1 :@a +user1 self")
        self.handle_line(":server 366 self #test1 :End of names")
        self.assertEqual(on_names.call_count, 1)

    def test_on_names_empty(self):
        @mock_event(self.bot, "on_names")
        def on_names(channel, names):
            pass
        self.handle_line(":server 366 self #test1 :End of names")
        self.assertEventCalled(on_names, "#test1", ISet())

    def test_on_raw(self):
        @mock_event(self.bot, "on_raw")
        def on_raw(nickname, command, args):
            pass
        self.handle_line(":nick COMMAND arg1 arg2 :arg with spaces")
        self.assertEventCalled(
            on_raw, "nick", "COMMAND", ["arg1", "arg2", "arg with spaces"])

    def test_on_mode(self):
        self.handle_line(":sender MODE self +i")
        self.handle_line(":sender MODE #test1 +ov user2 user1")
        user1 = self.bot.nicklist["#test1"]["user1"]
        user2 = self.bot.nicklist["#test1"]["user2"]
        self.assertEqual((user1.is_voiced, user1.is_op), (True, False))
        self.assertEqual((user2.is_voiced, user2.is_op), (False, True))
        self.assertFalse(self.bot.nicklist["#test2"]["user1"].is_voiced)

        self.handle_line(":sender MODE #test1 -v+v user1 user2")
        user1 = self.bot.nicklist["#test1"]["user1"]
        user2 = self.bot.nicklist["#test1"]["user2"]
        self.assertEqual((user1.is_voiced, user1.is_op), (False, False))
        self.assertEqual((user2.is_voiced, user2.is_op), (True, True))

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


class TestConnect(BaseBotTest):
    def setUp(self):
        super(TestConnect, self).setUp()
        self.bot = IRCBot(delay=False)

    def test_connect(self):
        self.bot.connect("example.com", 6667)
        self.assertEqual(self.bot.hostname, "example.com")
        self.assertEqual(self.bot.port, 6667)
        self.assertTrue(self.bot.alive)
        self.bot.socket.connect.assert_called_once_with(("example.com", 6667))

    def test_connect_ssl(self):
        self.bot.connect("example.com", 6697, use_ssl=True)
        context = ssl.SSLContext()
        peercert = self.bot.socket.getpeercert()
        load_default_certs = getattr(
            context, "load_default_certs", context.set_default_verify_paths)

        self.assertCalledOnce(context.wrap_socket, self.mock_socket)
        self.assertCalledOnce(load_default_certs)
        self.assertCalledOnce(ssl.match_hostname, peercert, "example.com")

    def test_connect_ssl_ca_certs(self):
        self.bot.connect("example.com", 6697, use_ssl=True, ca_certs="/test")
        context = ssl.SSLContext()
        self.assertCalledOnce(context.load_verify_locations, cafile="/test")

    def test_register(self):
        self.bot.connect("example.com", 6667)
        self.from_server(":server 001 test-nickname :Welcome")
        self.bot.register("test-nickname")
        self.assertSent(
            "USER test-nickname 8 * :test-nickname",
            "NICK :test-nickname")

    def test_register_with_realname(self):
        self.bot.connect("example.com", 6667)
        self.from_server(":server 001 test-nickname :Welcome")
        self.bot.register("test-nickname", "test-realname")
        self.assertSent(
            "USER test-nickname 8 * :test-realname",
            "NICK :test-nickname")

    def test_register_with_username(self):
        self.bot.connect("example.com", 6667)
        self.from_server(":server 001 test-nickname :Welcome")
        self.bot.register("test-nickname", "test-realname", "test-username")
        self.assertSent(
            "USER test-username 8 * :test-realname",
            "NICK :test-nickname")

    def test_register_nickname_in_use(self):
        self.bot.connect("example.com", 6667)
        self.from_server(":server 433 * test-nickname :UserHostInfo in use")
        with self.assertRaises(ValueError):
            self.bot.register("test-nickname")

    def test_register_connection_lost(self):
        self.bot.connect("example.com", 6667)
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


class TestListen(BaseBotTest):
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
        with warnings.catch_warnings(record=True):
            self.bot.listen_async(callback)
        self.bot.wait()

        self.assertEqual(on_raw.call_count, 2)
        self.assertAnyCall(on_raw, "self", "COMMAND1", [])
        self.assertAnyCall(on_raw, "self", "COMMAND2", [])
        self.assertCalled(callback)

    def test_listen_async_exception(self):
        @mock_event(self.bot, "on_raw")
        def on_raw(nickname, command, args):
            raise Exception("Test exception")
        self.from_server(":self COMMAND1")
        self.from_server()

        mock_format_exc = mock.Mock(spec=[])
        print_patch = mock.patch.object(pyrcb, "print")
        format_exc_patch = mock.patch.object(
            traceback, "format_exc", mock_format_exc)

        with print_patch, format_exc_patch:
            with warnings.catch_warnings(record=True):
                self.bot.listen_async()
            self.bot.wait()
        self.assertCalled(mock_format_exc)

    def test_socket_error_caught(self):
        error = socket.error(errno.ECONNRESET, "Test exception")
        self.bot.readline = mock.Mock(side_effect=error)
        self.bot.listen()

    def test_other_error_uncaught(self):
        error = socket.error(errno.EPERM, "Test exception")
        self.bot.readline = mock.Mock(side_effect=error)
        with self.assertRaises(socket.error):
            self.bot.listen()


class TestDelay(BaseBotTest):
    def setUp(self):
        super(TestDelay, self).setUp()
        mock_clock = MockClock()
        mock_socket = MockDelaySocket(mock_clock)
        self.patch("pyrcb.best_clock", new=mock_clock)
        self.patch("socket.create_connection", spec=socket.create_connection,
                   new=get_mock_create_connection(mock_socket))

        self.bot = IRCBot(delay=False)
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


class TestCloseSocket(BaseBotTest):
    def setUp(self):
        super(TestCloseSocket, self).setUp()
        self.bot = IRCBot()
        self.bot.connect("example.com", 6667)

    def test_close_socket(self):
        self.bot.close_socket()
        self.assertCalled(self.bot.socket.shutdown, socket.SHUT_RDWR)
        self.assertCalled(self.bot.socket.close)
        self.assertFalse(self.bot.alive)

    def test_close_socket_error_caught(self):
        error = socket.error(errno.ENOTCONN, "Test message")
        self.bot.socket.shutdown = mock.Mock(side_effect=error)
        self.bot.close_socket()

    def test_close_socket_error_uncaught(self):
        error = socket.error(errno.EPERM, "Test message")
        self.bot.socket.shutdown = mock.Mock(side_effect=error)
        with self.assertRaises(socket.error):
            self.bot.close_socket()


class TestMisc(BaseBotTest):
    def test_parse(self):
        nick, cmd, args = IRCBot.parse(
            ":nickname!user@host.name COMMAND arg1 arg2 :trailing arg")
        self.assertIs(type(nick), UserHostInfo)
        self.assertIs(type(cmd), IStr)
        for arg in args:
            self.assertIs(type(arg), ustr)
        self.assertEqual(nick, "nickname")
        self.assertEqual(nick.username, "user")
        self.assertEqual(nick.hostname, "host.name")
        self.assertEqual(cmd, "COMMAND")
        self.assertEqual(args, ["arg1", "arg2", "trailing arg"])

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
        self.bot.connect("example.com", 6667)
        self.from_server(":test CMD :arg")
        with mock.patch("pyrcb.print", create=True):
            self.bot.readline()
            self.assertCalled(pyrcb.print, ":test CMD :arg", file=sys.stdout)
            self.bot.writeline("CMD :arg")
            self.assertCalled(pyrcb.print, ">>> CMD :arg", file=sys.stdout)

    def test_start_thread(self):
        self.bot = IRCBot()
        self.bot.connect("example.com", 6667)
        target = mock.Mock(spec=[])
        thread = self.bot.start_thread(
            target, args=["test"], kwargs={"test": "test"})
        thread.join()
        self.assertCalled(target, "test", test="test")
        self.assertTrue(self.bot.alive)

    def test_start_thread_exception(self):
        self.bot = IRCBot()
        self.bot.connect("example.com", 6667)
        target = mock.Mock(spec=[], side_effect=Exception("Test"))

        mock_format_exc = mock.Mock(wraps=traceback.format_exc)
        with mock.patch.object(traceback, "format_exc", mock_format_exc):
            with mock.patch.object(pyrcb, "print"):
                thread = self.bot.start_thread(target, ["test"])
                thread.join()

        self.assertCalled(mock_format_exc)
        self.assertCalled(target, "test")
        self.assertFalse(self.bot.alive)

    def test_start_thread_reconnect(self):
        self.bot = IRCBot()
        self.bot.connect("example.com", 6667)
        target_event = threading.Event()
        target = mock.Mock(wraps=lambda *a, **kw: target_event.wait())
        thread = self.bot.start_thread(
            target, args=["test"], kwargs={"test": "test"})

        self.bot.quit()
        self.bot.connect("example.com", 6667)
        target_event.set()
        thread.join()
        self.assertCalled(target, "test", test="test")
        self.assertTrue(self.bot.alive)


class TestCaseInsensitiveClasses(BaseTest):
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
        with self.assertRaises(TypeError):
            IDefaultDict("test")
        d = IDefaultDict(int, test=20)
        d["Test^"] = 10
        d["TEST~"] += 5
        self.assertEqual(d["Test"], 20)
        self.assertEqual(d["TEST~"], 15)
        self.assertEqual(str(list(d.keys())[1]), "Test^")
        self.assertEqual(d["test2"], 0)

    def test_idefaultdict_order(self):
        d = IDefaultDict(None, [("q", 0), ("w", 0)], e=0)
        keys = "rtyuiopasdfghjklzxcvbnm"
        for key in keys:
            d[key] = 0
        self.assertEqual("".join(list(d.keys())), "qwe" + keys)

    def test_idefaultdict_missing(self):
        d = IDefaultDict()
        with self.assertRaises(KeyError):
            d["test"]

    def test_idefaultdict_other_methods(self):
        d = IDefaultDict(test=10)
        self.assertIn("test", d)
        del d["TEST"]
        self.assertNotIn("test", d)

        d["test"] = 15
        self.assertEqual(d.get("TEST"), 15)
        self.assertEqual(d.get("abc"), None)

        self.assertEqual(d.pop("TEST"), 15)
        self.assertNotIn("test", d)

    def test_iset(self):
        s = ISet(["test1"])
        s.add("Test2")
        s.add("TEST3")
        s -= {"test2"}
        self.assertTrue("TEST1" in s)
        self.assertTrue("test3" in s)
        self.assertFalse("test2" in s)
        self.assertFalse("test1" in s ^ {"Test1"})
        self.assertEqual(s, {"TEST1", "Test3"})

    def test_userhostinfo(self):
        nick = UserHostInfo("Test", username="user", hostname="host")
        self.assertEqual(nick, "TEST")
        self.assertEqual(nick.username, "user")
        self.assertEqual(nick.hostname, "host")

    def test_userhostinfo_missing_args(self):
        with self.assertRaises(TypeError):
            UserHostInfo("Test")
        with self.assertRaises(TypeError):
            UserHostInfo("Test", username="test")
        with self.assertRaises(TypeError):
            UserHostInfo("Test", hostname="test")

    def test_voiceopinfo(self):
        nick = VoiceOpInfo("Test", is_voiced=True, is_op=False)
        self.assertEqual(nick, "TEST")
        self.assertTrue(nick.is_voiced)
        self.assertFalse(nick.is_op)
        nick = VoiceOpInfo("Test", is_voiced=False, is_op=True)
        self.assertFalse(nick.is_voiced)
        self.assertTrue(nick.is_op)

    def test_voiceopinfo_missing_args(self):
        with self.assertRaises(TypeError):
            VoiceOpInfo("Test")
        with self.assertRaises(TypeError):
            VoiceOpInfo("Test", is_voiced=True)
        with self.assertRaises(TypeError):
            VoiceOpInfo("Test", is_op=True)

if __name__ == "__main__":
    unittest.main()
