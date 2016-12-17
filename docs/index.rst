.. Copyright (C) 2015-2016 nickolas360 <contact@nickolas360.com>

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

pyrcb
=====

*NOTE: Development has moved to* `pyrcb2`_. *pyrcb is no longer under active
development, except for bug fixes.*

.. _pyrcb2: https://github.com/nickolas360/pyrcb2

**pyrcb** is a simple, self-contained, extendable library for building IRC
bots. It isn't a full implementation of IRC, but rather provides everything
needed to easily create bots.

pyrcb is compatible with Python 2.7 and Python 3.1 or higher. SSL/TLS support
requires at least Python 2.7.9 or Python 3.2 (see :meth:`~IRCBot.connect`).

The current version of pyrcb is **1.14.2**, which was released on 2016-12-11.
See the :doc:`changelog <release-notes/1.14/changelog>` for more information.

Source code for pyrcb (including this documentation) is available at
`<https://github.com/nickolas360/pyrcb>`_.

.. toctree::
   :hidden:
   :maxdepth: 3

   reference
   installation
   guide
   custom-commands
   release-notes/index
   Source code <https://github.com/nickolas360/pyrcb>
   Examples <https://github.com/nickolas360/pyrcb/tree/master/examples>
   License <https://github.com/nickolas360/pyrcb/blob/master/LICENSE>
