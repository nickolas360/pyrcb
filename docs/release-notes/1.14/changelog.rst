.. Copyright (C) 2016 nickolas360 <contact@nickolas360.com>

.. This file is part of pyrcb-docs, documentation for pyrcb.
   pyrcb-docs is licensed under the following two licenses:

.. 1. The GNU Lesser General Public License as published by the Free
   Software Foundation, either version 3 of the License, or (at your
   option) any later version.

.. 2. The GNU Free Documentation License, Version 1.3 or any later
   version published by the Free Software Foundation; with no
   Invariant Sections, no Front-Cover Texts, and no Back-Cover Texts.

.. pyrcb-docs is distributed in the hope that it will be useful,
   but WITHOUT ANY WARRANTY; without even the implied warranty of
   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
   GNU Lesser General Public License for more details.

.. You should have received a copy of the GNU Lesser General Public
   License and the GNU Free Documentation License along with
   pyrcb-docs.  If not, see <http://www.gnu.org/licenses/>.

.. currentmodule:: pyrcb

Changelog
=========

.. _changelog-1.14.1:

1.14.1
------

* Fixed a bug with ``RPL_ISUPPORT`` message handling that would cause bots to
  crash.

.. _changelog-1.14.0:

1.14.0
------

* `VoiceOpInfo` now supports all prefixes, not just "@" and "+".
* Mode tracking is now more accurate and less prone to errors.
* An error no longer occurs when an event handler takes fewer arguments than
  are available.
* Fixed a bug with the ``kill_bot`` parameter in :meth:`IRCBot.start_thread`
  (setting it to ``False`` would have no effect).
