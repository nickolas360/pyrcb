# TimeBot - An example IRC bot
# Written in 2015 by nickolas360 (https://github.com/nickolas360)
#
# To the extent possible under law, the author(s) have dedicated all copyright
# and related and neighboring rights to this software to the public domain
# worldwide. This software is distributed without any warranty.
#
# You should have received a copy of the CC0 Public Domain Dedication along
# with this software. If not, see
# <http://creativecommons.org/publicdomain/zero/1.0/>.

from __future__ import print_function
from pyrcb import IrcBot
from datetime import datetime


class TimeBot(IrcBot):
    # Called when someone says something in a channel or a private query.
    def on_message(self, message, nickname, target, is_query):
        # If someone says !time, state the time.
        if message.lower() == "!time":
            self.send(target, str(datetime.utcnow()))


def main():
    bot = TimeBot(debug_print=True)
    bot.connect("irc.freenode.net", 6667)
    bot.register("timebot")
    bot.join("##timebot-test")

    # Blocking; will return when connection is lost.
    bot.listen_async()
    print("Disconnected from server.")

if __name__ == "__main__":
    main()
