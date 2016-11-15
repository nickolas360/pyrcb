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

.. _changelog-1.12.1:

1.12.1
------

* Fixed an issue where exceptions in background threads would sometimes not be
  printed.

.. _changelog-1.12.0:

1.12.0
------

* Added :meth:`IRCBot.start_thread`, which starts a function on a separate
  thread. This should be used instead of :meth:`~IRCBot.listen_async`.
* Deprecated :meth:`IRCBot.listen_async`. Instead of running the bot in the
  background, start threads with :meth:`~IRCBot.start_thread` and call
  :meth:`~IRCBot.listen` on the main thread.
* Fixed possible errors when closing sockets.
