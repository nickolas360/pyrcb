.. Copyright (C) 2016 nickolas360 <contact@nickolas360.com>

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

.. _changelog-1.8.0:

1.8.0
-----

* Added :meth:`IRCBot.register_event`, which allows event handlers to be
  registered for custom IRC commands.
* Added configurable attributes for message delaying. See :ref:`delay-options`.
* Fixed an issue with managing nicklists.
* Improved socket error handling.
* When using :meth:`~IRCBot.listen_async`, the callback will now be called
  before any calls to :meth:`~IRCBot.wait` return.
