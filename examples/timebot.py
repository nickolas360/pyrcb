#!/usr/bin/env python3
# To the extent possible under law, the author(s) have dedicated all
# copyright and neighboring rights to this software to the public domain
# worldwide. This software is distributed without any warranty. See
# <http://creativecommons.org/publicdomain/zero/1.0/> for a copy of the
# CC0 Public Domain Dedication.

from __future__ import print_function
from pyrcb import IRCBot
from datetime import datetime


class TimeBot(IRCBot):
    def on_message(self, message, nickname, channel, is_query):
        # Say the time when someone says "!time".
        if message.lower() == "!time":
            time = str(datetime.utcnow())
            if is_query:
                self.send(nickname, time)
            else:
                self.send(channel, nickname + ": " + time)


def main():
    bot = TimeBot(debug_print=True)
    bot.connect("<ip-or-hostname>", 6667)
    bot.register("timebot")
    bot.join("#timebot")

    # Blocking; will return when disconnected.
    bot.listen()
    print("Disconnected from server.")

if __name__ == "__main__":
    main()


# Example IRC log:
# [#timebot] timebot has joined #timebot
# [#timebot] <user1234> !time
# [#timebot] <timebot> user1234: 2015-11-02 04:41:25.227800
#
# In a private query:
# [query] <user1234> !time
# [query] <timebot> 2015-11-02 05:28:17.395795
