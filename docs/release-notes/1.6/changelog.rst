.. Copyright (C) 2015 nickolas360 <contact@nickolas360.com>

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

Changelog
=========

.. note::

   A list of backwards-incompatible changes is available in the document
   :doc:`transitioning`. If you're updating a bot which uses an older version
   of pyrcb, you should follow that guide.

.. _changelog-1.6.2:

1.6.2
-----

* Fixed an issue where part messages would always be set to `None`.

.. _changelog-1.6.1:

1.6.1
-----

* Fixed an issue where `IRCBot.nickname` wouldn't update after changing
  nicknames.

.. _changelog-1.6.0:

1.6.0
-----

Backwards-incompatible changes
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If you're updating a bot which uses an older version of pyrcb, follow
:doc:`transitioning` instead.

* Renamed ``IrcBot`` to `IRCBot`.
* Replaced ``target`` parameter with ``channel`` in :meth:`~IRCBot.on_message`
  and :meth:`~IRCBot.on_notice`.
* Removed ``is_self`` parameter from events.
* Added ``message`` parameter to :meth:`~IRCBot.on_kick`.
* Removed ``is_alive()``.
* Changed :meth:`~IRCBot.send_raw` parameters to an IRC command and a list of
  arguments to the command.
* Renamed ``on_other()`` to :meth:`~IRCBot.on_raw`.
* :meth:`~IRCBot.on_raw` is now called for every IRC message, not just ones
  without a specific event.
* Removed ``async_events`` parameter from :meth:`~IRCBot.listen` and
  :meth:`~IRCBot.listen_async`.


Other API changes
~~~~~~~~~~~~~~~~~

* Added `IStr`, a case-insensitive string class.
* Added `IDefaultDict`, a case-insensitive dictionary class.
* Made all ``nickname``, ``channel``, and ``target`` parameters in events
  case-insensitive. See `IStr` for more information.
* Added `IRCBot.nicklist`, a case-insensitive dictionary which stores lists of
  users in channels.
* Made `IRCBot.channels` case-insensitive.
* Made `IRCBot.nickname` case-insensitive.
* Added a ``timeout`` parameter to :meth:`~IRCBot.wait`.
* Added a ``realname`` parameter to :meth:`~IRCBot.register`.
* When given a list of CA certificates, :meth:`~IRCBot.connect` now verifies
  the server's hostname as well as its certificate.

Internal changes
~~~~~~~~~~~~~~~~

* Renamed some private methods.
* Renamed some private buffers.
* Methods now call :meth:`~IRCBot.send_raw` instead of ``writeline()``.
* Socket errors are now handled more gracefully.
* Made ``parse()`` a static method.
* Added ``format()``, which formats IRC messages.
* :meth:`~IRCBot.register` now waits for ``RPL_WELCOME`` instead of ``MODE``.
