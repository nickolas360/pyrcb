#!/usr/bin/env python3
# To the extent possible under law, the author(s) have dedicated all
# copyright and neighboring rights to this software to the public domain
# worldwide. This software is distributed without any warranty. See
# <http://creativecommons.org/publicdomain/zero/1.0/> for a copy of the
# CC0 Public Domain Dedication.

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

    # Says the time at a specified rate.
    def auto_time_loop(self, interval):
        while self.alive:
            # If the bot loses connection while waiting, return.
            if self.wait(interval):
                return
            time = str(datetime.utcnow())
            for channel in self.channels:
                self.send(channel, "(auto) " + time)


def main():
    bot = AutoTimeBot(debug_print=True)
    bot.connect("<ip-or-hostname>", 6667)
    bot.register("timebot")
    bot.join("#timebot")

    interval = 10 * 60  # 10 minutes
    bot.start_thread(bot.auto_time_loop, args=[interval])
    bot.listen()
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
