# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

#!/usr/bin/env python
# -*- coding: utf-8 -*-

try: # compatibility with Python 3+
    _range = xrange
except NameError:
    _range = range

try:
    from cStringIO import StringIO
    _StringIO = StringIO
except (ImportError, NameError): #python3.x
    from io import StringIO
    _StringIO = StringIO

try:
    from itertools import izip
    _izip = izip
except ImportError:  #python3.x
    _izip = zip

try:
    _str = basestring
except NameError:
    _str = str
