#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#
# pacnet.py
#
# Copyright (C) 2008 by Piotr Husiatyński <phusiatynski@gmail.com>
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301,
# USA.

import urllib
import os

try:
    import simplejson as json
except ImportError:
    import sys
    sys.exit("To use pacnet plugin, install simplejson library.")


class Plugin_pacnet(object):
    """Do some stuff with AUR. Search and download files."""
    def __init__(self, io, conf):
        self.io = io
        self.conf = conf
        self.pkg_list = []
        self.url_json = 'http://pacnet.karbownicki.com/pl/szukaj/json/?search='

    def search_with_json(self, pkg_name):
        """Returns converted JSON object from given url"""
        url = self.url_json + pkg_name
        try:
            json_obj = urllib.urlopen(url).read()
        except IOError:
            self.io.put("#{RED}Can't download JSON object.#{NONE}")
            return False
        return json.loads(json_obj)

    def do_search(self, *pkgnames):
        """Search package in AUR"""
        if not pkgnames :
            return False
        result = []
        for pkg in pkgnames:
            if len(pkg) < 3:
                self.io.put('Name #{BOLD}%s#{NONE} is too short.' % pkg)
            else:
                x = self.search_with_json(pkg)
                result.extend(x)
        if not result:
            return False
        for pkg in result:
            if pkg:
                self.io.put("#{BLUE}%(category)s#{NONE}/#{WHITE}%(name)s#{NONE}\n  %(desc)s" % pkg)
        return True

    # alias
    __call__ = do_search
