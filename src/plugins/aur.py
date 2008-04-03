#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#
# aur.py
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
    sys.exit("To use AUR plugin, install simplejson library.")

from sgmllib import SGMLParser



class URLLister(SGMLParser):
    def reset(self):
        SGMLParser.reset(self)
        self.urls = []

    def start_a(self, attrs):
        href = [v for k, v in attrs if k=='href']
        if href:
            self.urls.extend(href)


class Plugin_aur(object):
    """Do some stuff with AUR. Search and download files."""
    def __init__(self, io, conf):
        self.io = io
        self.conf = conf
        self.pkg_list = []
        self.url_files = "http://aur.archlinux.org/packages/"
        self.url_info = "http://aur.archlinux.org/rpc.php?type=info&arg="
        self.url_search = "http://aur.archlinux.org/rpc.php?type=search&arg="
        self.url_id = "http://aur.archlinux.org/packages.php?ID="


    def complete(self, text):
        if text.endswith(" "):
            return self.pkg_list
        text = text.split()
        # TODO [ 16:55 - 02.04.2008 ] 
        # fix '-' in name completition bug
        return [name for name in self.pkg_list if name.startswith(text[-1])]

    def search_with_json(self, url):
        """Returns converted JSON object from given url"""
        try:
            json_obj = urllib.urlopen(url).read()
        except IOError:
            self.io.put("#{RED}PROXY error?#{NONE}")
            return False
        result = json.loads(json_obj)
        if result['results'] == u'No results found' or \
                result['results'] == u'No result found':
            return None
        return result['results']


    def do_search(self, pkgname, *ignore):
        """Search package in AUR"""
        result = self.search_with_json(self.url_search + pkgname)
        if not result:
            self.io.put("No package found")
            return False
        else:
            for numb, pkg in enumerate(result):
                # add package name to memmory
                self.pkg_list.append(pkg['Name'])
                self.io.put(" #{BLUE}%3d#{NONE}  %s" % (numb+1, pkg['Name']))
        return True

    def do_info(self, pkgname, *ignore):
        """Show more info about package"""
        result = self.search_with_json(self.url_info + pkgname)
        if not result:
            self.io.put("No such package in AUR")
            return False
        else:
            for key in result:
                if not key in ["ID", "Name"]:
                    self.io.put("#{GREEN}%s#{NONE} : %s" % \
                            (key.rjust(18), result[key]))
            self.io.put("       #{GREEN}Link to AUR#{NONE} : %s" % \
                    self.url_id + result['ID'])
        return True


    def do_download(self, pkgname, *ignore):
        """Download files from AUR"""
        # TODO [ 20:39 - 01.04.2008 ] 
        # download from CVS
        def list_all_links(url):
            """Get all the links from page"""
            try:
                www = urllib.urlopen(url)
            except IOError:
                self.io.put("#{RED}PROXY error?#{NONE}")
                return False
            parser = URLLister()
            parser.feed(www.read())
            parser.close()
            www.close()
            return [url for url in parser.urls]
        url = self.url_files + "/".join((pkgname, pkgname))
        link_list = list_all_links(url)[5:]
        # if no such PKGBUILD in AUR
        if link_list == []:
            self.io.put("No files found.")
            return False
        pkgdir = os.path.join(self.conf.build_dir, pkgname)
        if not os.path.isdir(pkgdir):
            os.mkdir(pkgdir)
        elif not self.io.ask('Files allready exists. Rewrite?'):
            return False
        # info about downloading files
        if len(link_list) == 1:
            self.io.put("#{GREEN}Downloading 1 file:#{NONE}")
        else:
            self.io.put("#{GREEN}Downloading %d files:#{NONE}" % len(link_list))
        # download files
        for numb, filename in enumerate(link_list):
            to_download = '/'.join((url, filename))
            self.io.put("  #{BLUE}%3d#{NONE} |  #{BOLD}%s#{NONE}" % (numb + 1, filename))
            urllib.urlretrieve(to_download, os.path.join(pkgdir, filename))
        return True

    def do_vote(self, pkgname, vote_type=None, *ignore):
        """Vote on PKGBUILD. As argument type + or -"""
        if not vote_type in ["+", "-"]:
            self.io.put("#{RED}Cancel.#{NONE} Vote with + or -")
            return False
        self.io.put("Voting on +\nTODO")
        return True
