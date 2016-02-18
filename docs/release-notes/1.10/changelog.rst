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

.. _changelog-1.10.1:

1.10.1
------

* Fixed a bug where sockets would sometimes not be properly cleaned up.

.. _changelog-1.10.0:

1.10.0
------

* Nicknames in `IRCBot.nicklist` and in the ``names`` parameter of
  :meth:`IRCBot.on_names` now have two additional attributes: ``is_voiced`` and
  ``is_op``, which specify whether or not each user is voiced or is a channel
  operator.
