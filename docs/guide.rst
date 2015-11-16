.. Copyright (C) 2015 nickolas360 (https://github.com/nickolas360)

.. This file is part of pyrcb-docs, documentation for pyrcb.

.. pyrcb-docs is free software: you can redistribute it and/or modify
   it under the terms of the GNU Lesser General Public License as
   published by the Free Software Foundation, either version 3 of the
   License, or (at your option) any later version.

.. pyrcb-docs is distributed in the hope that it will be useful,
   but WITHOUT ANY WARRANTY; without even the implied warranty of
   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
   GNU Lesser General Public License for more details.

.. You should have received a copy of the GNU Lesser General Public License
   along with pyrcb-docs.  If not, see <http://www.gnu.org/licenses/>.

.. currentmodule:: pyrcb

Guide
=====

.. note::

   pyrcb bots are subclasses of `IRCBot`. They handle events by overriding
   methods such as :meth:`~IRCBot.on_message` and :meth:`~IRCBot.on_join`, and
   they send messages and commands by calling methods such as
   :meth:`~IRCBot.send` and :meth:`~IRCBot.join`.

   All ``nickname``, ``channel``, and ``target`` parameters in events are
   case-insensitive strings (type `IStr`). This means that equality comparisons
   with those parameters are case-insensitive, so you don't have to call
   :meth:`~str.lower` on them first. (The attributes `~IRCBot.nickname`,
   `~IRCBot.channels`, and `~IRCBot.names` are also case-insensitive.)

   Case-insensitive strings abide by `IRC case rules`_, which state that
   ``{}|^`` are lowercase equivalents of ``[]\~``. See `IStr` for more info.

   .. _IRC case rules: https://tools.ietf.org/html/rfc2812#section-2.2

If you haven't installed pyrcb yet, read :doc:`installation` first.

Begin by importing `IRCBot` from ``pyrcb``::

   from pyrcb import IRCBot

pyrcb bots are classes which inherit `IRCBot`:

.. code-block:: python

   class MyBot(IRCBot):

pyrcb bots respond to actions by overriding events. Let's override
:meth:`~IRCBot.on_message` to handle messages:

.. code-block:: python

   class MyBot(IRCBot):
       def on_message(self, message, nickname, channel, is_query):

When this bot receives a message in a channel or private query,
:meth:`~IRCBot.on_message` will be called. Let's have the bot repeat whatever
someone says::

   class MyBot(IRCBot):
       def on_message(self, message, nickname, channel, is_query):
           if is_query:
               self.send(nickname, "You said: " + message)
           else:
               self.send(channel, nickname + " said: " + message)

``is_query`` is whether or not the message is in a private query. ``channel``
is the channel the message is in. If in a private query, this is `None`.
``nickname`` is the nickname of the user who sent the message.
:meth:`~IRCBot.send` sends a message to a channel or user.

To run our bot, let's create a main method and create an instance::

   def main():
       bot = MyBot()

We'll call :meth:`~IRCBot.connect` to connect to an IRC server, and
:meth:`~IRCBot.register` to register with the server. Calling these two methods
is required. ::

   bot.connect("<ip-or-hostname>", 6667)
   bot.register("mybot")

Then we'll call :meth:`~IRCBot.join` to join a channel::

   bot.join("#mybot")

Finally, we have to call :meth:`~IRCBot.listen`, which reads data from the
server and calls the appropriate events. This method will block until
connection to the server is lost. ::

   bot.listen()

All that's left is to call the main method::

   if __name__ == "__main__":
       main()

Our finished bot now looks like::

   from pyrcb import IRCBot

   class MyBot(IRCBot):
       def on_message(self, message, nickname, channel, is_query):
           if is_query:
               self.send(nickname, "You said: " + message)
           else:
               self.send(channel, nickname + " said: " + message)

   def main():
       bot = MyBot()
       bot.connect("<ip-or-hostname>", 6667)
       bot.register("mybot")
       bot.join("#mybot")
       bot.listen()

   if __name__ == "__main__":
       main()

If we run our bot, it will work like this in channels::

   [#mybot] mybot has joined #mybot
   [#mybot] <user1234> Test message
   [#mybot] <mybot> user1234 said: Test message

And it will work like this in private queries::

   [query] <user1234> Test message
   [query] <mybot> You said: Test message

:doc:`reference` includes a complete list of all the methods and events you can use in pyrcb bots. Take a look at the `examples`_ as well.

.. _examples: https://github.com/nickolas360/pyrcb/tree/master/examples/
