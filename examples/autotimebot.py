# Written in 2015-2016 by nickolas360 <contact@nickolas360.com>
#
# To the extent possible under law, the author(s) have
# dedicated all copyright and related and neighboring
# rights to this software to the public domain worldwide.
# This software is distributed without any warranty.
#
# You should have received a copy of the CC0 Public Domain
# Dedication along with this software. If not, see
# <http://creativecommons.org/publicdomain/zero/1.0/>.

from __future__ import print_function
from pyrcb import IRCBot
from datetime import datetime


class AutoTimeBot(IRCBot):
    def on_message(self, message, nickname, channel, is_query):
        # Say the time when someone says "!time".
        if message.lower() == "!time":
            time = str(datetime.utcnow())
            if is_query:
                self.send(nickname, time)
            else:
                self.send(channel, nickname + ": " + time)

    # Say the time every ten minutes.
    def auto_time_loop(self, channel):
        while self.alive:
            self.wait(10 * 60)
            time = str(datetime.utcnow())
            for channel in self.channels:
                self.send(channel, "(auto) " + time)


def main():
    bot = AutoTimeBot(debug_print=True)
    bot.connect("<ip-or-hostname>", 6667)
    bot.register("timebot")
    bot.join("#timebot")

    # Non-blocking.
    bot.listen_async()

    # Blocking; will return when disconnected.
    bot.auto_time_loop("#timebot")
    print("Disconnected from server.")

if __name__ == "__main__":
    main()


# Example IRC log:
# [#timebot] timebot has joined #timebot
# [#timebot] <user1234> !time
# [#timebot] <timebot> user1234: 2015-11-02 04:41:25.227800
#
# 10 minutes later:
# [#timebot] <timebot> (auto) 2015-11-02 04:51:18.551725
#
# In a private query:
# [query] <user1234> !time
# [query] <timebot> 2015-11-02 05:28:17.395795
