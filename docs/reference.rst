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

.. module:: pyrcb

Reference
=========

IRCBot
------

.. autoclass:: IRCBot

Methods
~~~~~~~

.. automethod:: IRCBot.connect
.. automethod:: IRCBot.password
.. automethod:: IRCBot.register
.. automethod:: IRCBot.join
.. automethod:: IRCBot.part
.. automethod:: IRCBot.quit
.. automethod:: IRCBot.send
.. automethod:: IRCBot.send_notice
.. automethod:: IRCBot.nick
.. automethod:: IRCBot.names
.. automethod:: IRCBot.send_raw
.. automethod:: IRCBot.listen
.. automethod:: IRCBot.listen_async
.. automethod:: IRCBot.wait

Events
~~~~~~

.. note::

   All ``nickname``, ``channel``, and ``target`` parameters in events are
   case-insensitive strings (type `IStr`). This means that equality comparisons
   with those parameters are case-insensitive, so you don't have to call
   :meth:`~str.lower` on them first. (The attributes `~IRCBot.nickname`,
   `~IRCBot.channels`, and `~IRCBot.names` are also case-insensitive.)

   Case-insensitive strings abide by `IRC case rules`_, which state that
   ``{}|^`` are lowercase equivalents of ``[]\~``. See `IStr` for more info.

   .. _IRC case rules: https://tools.ietf.org/html/rfc2812#section-2.2

.. automethod:: IRCBot.on_join
.. automethod:: IRCBot.on_part
.. automethod:: IRCBot.on_quit
.. automethod:: IRCBot.on_kick
.. automethod:: IRCBot.on_message
.. automethod:: IRCBot.on_notice
.. automethod:: IRCBot.on_nick
.. automethod:: IRCBot.on_names
.. automethod:: IRCBot.on_raw

Attributes
~~~~~~~~~~

.. attribute:: IRCBot.hostname

   The hostname of the IRC server this bot is connected to.

   :type: :class:`str`

.. attribute:: IRCBot.port

    The port of the IRC server this bot is connected to.

    :type: :class:`int`

.. attribute:: IRCBot.alive

    Whether or not this bot is connected to an IRC server.

    For infinite loops, use ``while IRCBot.alive`` instead of ``while True``,
    so the loop stops when the bot loses connection. Use :meth:`IRCBot.wait()`
    instead of :func:`time.sleep` as well.

    :type: :class:`bool`

.. attribute:: IRCBot.is_registered

    Whether or not this bot has registered with the IRC server.

    :type: :class:`bool`

.. attribute:: IRCBot.nickname

    The nickname of this bot (case-insensitive).

    :type: :class:`IStr`

.. attribute:: IRCBot.channels

    A list of channels this bot is in (case-insensitive). Channels are of type
    :class:`IStr`.

    :type: :class:`list`

.. attribute:: IRCBot.nicklist

    A dictionary which maps channel names to lists of the nicknames of users in
    those channels.

    For example::

        >>> IRCBot.nicklist["#channel-name"]
        ["nickname0", "nickname1", "nickname2"]

    Keys are case-insensitive, as are the nicknames retrieved from the a
    dictionary lookup. If there is no list of nicknames for a particular
    channel, a dictionary lookup will return an empty list instead of producing
    an error.

    :type: :class:`IDefaultDict`

IStr
----

.. autoclass:: IStr()


IDefaultDict
------------

.. autoclass:: IDefaultDict
   :show-inheritance:
