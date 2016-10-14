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

.. _changelog-1.8.1:

1.8.1
-----

* Fixed the behavior of string splitting (used in :meth:`~IRCBot.on_message`,
  :meth:`~IRCBot.on_notice`, and :meth:`~IRCBot.split_string`) when ``nobreak``
  is true: if present, one space character between split strings is removed.
  (Previously, as many spaces as possible were removed, which could result in
  empty messages).

.. _changelog-1.8.0:

1.8.0
-----

* Added :meth:`IRCBot.register_event`, which allows event handlers to be
  registered for custom IRC commands.
* Long messages (PRIVMSGs) and notices are now split to ensure that they aren't
  truncated due to the 512-byte IRC message limit. See
  :meth:`~IRCBot.on_message` and :meth:`~IRCBot.split_string`.
* Added :meth:`IRCBot.split_string`.
* Added :meth:`IRCBot.safe_message_length`.
* Added configurable attributes for message delaying. See :ref:`delay-options`.
* Fixed an issue with sending non-ASCII characters in Python 2.
* Fixed an issue with managing nicklists.
* Fixed an issue where colons were not allowed in any IRC argument except the
  last (they should be forbidden only at the start).
* Improved socket error handling.
* When using :meth:`~IRCBot.listen_async`, the callback will now be called
  before any calls to :meth:`~IRCBot.wait` return.
