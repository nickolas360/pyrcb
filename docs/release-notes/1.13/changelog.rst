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

.. _changelog-1.13.0:

1.13.0
------

* Users' voice and channel operator statuses are now properly tracked.
* `IRCBot.nicklist` now maps channel names to `IDefaultDict` instances, where
  each of those dictionaries maps nicknames to `VoiceOpInfo` objects.
* Added `VoiceOpInfo`, a subclass of `IStr` that stores a user's voice and
  channel operator status.
* Renamed `Nickname` to `UserHostInfo`. `Nickname` is now a deprecated alias of
  `UserHostInfo`.
* Added `ISet`, a case-insensitive `set` class.
* Fixed minor documentation errors.
