# Copyright (C) 2015 nickolas360 (https://github.com/nickolas360)
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
import socket
import threading


class IrcBot(object):
    def __init__(self, debug_print=False):
        self._buffer = ""
        self.socket = socket.socket()
        self.hostname = None
        self.port = None

        self.debug_print = debug_print
        self.is_registered = False
        self.nickname = None
        self.channels = []
        self.alive = False

    def connect(self, hostname, port):
        self._cleanup()
        self.hostname = hostname
        self.port = port
        self.socket.connect((hostname, port))
        self.alive = True

    def register(self, nickname):
        self.nickname = nickname
        self._writeline("USER {0} 8 * :{0}".format(nickname))
        self._writeline("NICK {0}".format(nickname))
        while not self.is_registered:
            line = self._readline()
            if line is None:
                return
            self._handle(line)

    def join(self, channel):
        self.channels.append(channel.lower())
        self._writeline("JOIN {0}".format(channel))

    def part(self, channel):
        if channel.lower() in self.channels:
            self._writeline("PART {0}".format(channel))
            self.channels.remove(channel.lower())

    def quit(self):
        try:
            self._writeline("QUIT")
            self.socket.shutdown(socket.SHUT_RDWR)
        except socket.error:
            pass
        self.socket.close()
        self.alive = False

    def send(self, target, message):
        self._writeline("PRIVMSG {0} :{1}".format(target, message))

    def send_notice(self, target, message):
        self._writeline("NOTICE {0} :{1}".format(target, message))

    def send_raw(self, message):
        self._writeline(message)

    def listen(self):
        while True:
            try:
                line = self._readline()
            except socket.error:
                self.quit()
                return
            if line is None:
                return
            self._handle(line)

    def listen_async(self, callback=None):
        def target():
            self.listen()
            if callback:
                callback()
        t = threading.Thread(target=target)
        t.daemon = True
        t.start()

    def is_alive(self):
        return self.alive

    def on_join(self, nickname, channel):
        # To be overridden
        pass

    def on_part(self, nickname, channel):
        # To be overridden
        pass

    def on_quit(self, nickname):
        # To be overridden
        pass

    def on_kick(self, nickname, channel, target, is_self):
        # To be overridden
        pass

    def on_message(self, message, nickname, target, is_query):
        # To be overridden
        pass

    def on_notice(self, message, nickname, target, is_query):
        # To be overridden
        pass

    def on_other(self, message):
        # To be overridden
        pass

    def _handle(self, message):
        split = message.split(" ", 4)
        if len(split) < 2:
            return
        if split[0].upper() == "PING":
            self._writeline("PONG {0}".format(split[1]))
            return

        nick = split[0].split("!")[0].split("@")[0][1:]
        cmd = split[1].upper()
        if cmd == "MODE":
            self.is_registered = True
        elif cmd == "JOIN":
            self.on_join(nick, split[2])
        elif cmd == "PART":
            self.on_part(nick, split[2])
        elif cmd == "QUIT":
            self.on_quit(nick)
        elif cmd == "KICK":
            is_self = split[3].lower() == self.nickname.lower()
            self.on_kick(nick, split[2], split[3], is_self)
        elif cmd == "PRIVMSG" or cmd == "NOTICE":
            msg = " ".join(split[3:])[1:]
            target = nick if is_query else split[2]
            is_query = split[2].lower() == self.nickname.lower()
            event = self.on_message if cmd == "PRIVMSG" else self.on_notice
            event(msg, nick, target, is_query)
        else:
            self.on_other(message)

    def _readline(self):
        while "\r\n" not in self._buffer:
            data = self.socket.recv(1024)
            if len(data) == 0:
                self._cleanup()
                return
            self._buffer += data.decode("utf8", "ignore")

        line, self._buffer = self._buffer.split("\r\n", 1)
        if self.debug_print:
            print(line)
        return line

    def _writeline(self, data):
        self.socket.sendall((data + "\r\n").encode("utf8", "ignore"))
        if self.debug_print:
            print(">>> " + data)

    def _cleanup(self):
        self._buffer = ""
        self.is_registered = False
        self.channels = []
