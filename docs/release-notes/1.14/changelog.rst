.. Copyright (C) 2016 nickolas360 <contact@nickolas360.com>

.. This file is part of pyrcb-docs, documentation for pyrcb.

.. pyrcb-docs is licensed under the GNU Lesser General Public License
   as published by the Free Software Foundation, either version 3 of
   the License, or (at your option) any later version.

.. As an additional permission under GNU GPL version 3 section 7, you
   may distribute non-source forms of pyrcb-docs without the copy of
   the GNU GPL normally required by section 4, provided you include a
   URL through which recipients can obtain a copy of the Corresponding
   Source and the GPL at no charge.

.. pyrcb-docs is distributed in the hope that it will be useful,
   but WITHOUT ANY WARRANTY; without even the implied warranty of
   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
   GNU Lesser General Public License for more details.

.. You should have received a copy of the GNU Lesser General Public License
   along with pyrcb-docs.  If not, see <http://www.gnu.org/licenses/>.

.. currentmodule:: pyrcb

Changelog
=========

.. _changelog-1.14.2:

1.14.2
------

* Fixed a bug where :meth:`IRCBot.split_string` would not split properly with
  ``once=True``.

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
