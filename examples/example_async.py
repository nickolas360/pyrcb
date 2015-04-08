# RandomTimeBot - An example IRC bot
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
from time import sleep
import random


class RandomTimeBot(IrcBot):
    # Called when someone says something in a channel or a private query.
    def on_message(self, message, nickname, target, is_query):
        # If someone says !time, state the time.
        if message.lower() == "!time":
            self.send(target, str(datetime.utcnow()))

    # State the time at random intervals.
    def random_loop(self, channel):
        # Use self.is_alive() so the loop stops when the bot loses connection.
        while self.is_alive():
            if random.randint(1, 100) == 1:
                self.send(channel, str(datetime.utcnow()))
            sleep(10)


def main():
    bot = RandomTimeBot(debug_print=True)
    bot.connect("irc.freenode.net", 6667)
    bot.register("timebot")
    bot.join("##timebot-test")

    # Non-blocking.
    bot.listen_async()

    # Blocking; will return when connection is lost.
    bot.random_loop("##timebot-test")
    print("Disconnected from server.")

if __name__ == "__main__":
    main()
