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
    """Do some stuff with Pacnet. 
    More about Pacnet: http://pacnet.karbownicki.com/en
    """
    def __init__(self, io, conf):
        self.io = io
        self.conf = conf
        self.pkg_list = []
        self.url_json = 'http://pacnet.karbownicki.com/api/json'

    def get_json(self, url):
        """Returns converted JSON object from given url"""
        try:
            json_text = urllib.urlopen(url).read()
        except IOError:
            self.io.put("#{RED}Can't download JSON object.#{NONE}")
            return False
        return json.loads(json_text)

    def do_allpackages(self, *ignore):
        """List #{RED}ALL#{NONE} packages from Pacnet database."""
        url = 'http://pacnet.karbownicki.com/api/json/packages/'
        for pkg in self.get_json(url):
            pkg['name'] = pkg['name'].ljust(40)
            pkg['version'] = pkg['version'].ljust(12)
            self.io.put(
                    "#{WHITE}%(name)s %(version)s #{BLUE} %(category)s" % pkg)
        return True

    def do_info(self, package, *ignore):
        """Show more info about package."""
        url = 'http://pacnet.karbownicki.com/api/json/package/' + package
        pkglist = self.get_json(url)
        if not pkglist: 
            return False
        for desc in pkglist:
            self.io.put("""#{BLUE} Name      #{NONE}  : #{WHITE}%(name)s
#{NONE} Category    : #{NONE}%(category)s 
#{NONE} Version     : #{NONE}%(version)s
#{NONE} Description : #{NONE}%(description)s
            """ %  desc)
        return True

    def do_allcategories(self, *ignore):
        """List all categories."""
        url = 'http://pacnet.karbownicki.com/api/json/categories'
        for c in self.get_json(url):
            self.io.put(c['name'])
        return True

    def do_listcategory(self, category, *ignore):
        """List all packages from given category."""
        url = 'http://pacnet.karbownicki.com/api/json/category/' + category
        pkglist = self.get_json(url)
        if not pkglist:
            return False
        for pkg in pkglist:
            pkg['name'] = pkg['name'].ljust(22)
            self.io.put(
                    "#{BLUE}%(name)s #{WHITE}%(version)s\n#{NONE}  %(description)s" % pkg)
        return True

    def do_search(self, *pkgnames):
        """Search package in Pacnet database."""
        if not pkgnames :
            return False
        for pkgname in pkgnames:
            url = 'http://pacnet.karbownicki.com/api/json/search/' + pkgname
            for pkg in self.get_json(url):
                self.io.put("""#{BLUE}%(category)s#{NONE}/#{WHITE}%(name)s
  #{NONE}%(description)s""" % pkg)
        return True

