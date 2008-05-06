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
        self.url_json = "http://aur.archlinux.org/rpc.php"
        self.url_id = "http://aur.archlinux.org/packages.php?ID="


    def complete(self, text):
        """Complete package name"""
        if text.endswith(" "):
            return self.pkg_list
        text = text.split()
        # TODO [ 16:55 - 02.04.2008 ]
        # fix '-' in name completition bug
        if len(text[-1]) < 3:
            return [name for name in self.pkg_list if name.startswith(text[-1])]
        else:
            pkg_list = self.search_with_json("search", text[-1])
            return [p['Name'] for p in pkg_list]

    def do_show_pkgbuild(self, pkgname, *ignore):
        """Connect to AUR and print PKGBUILD"""
        url = self.url_files + pkgname + "/" + pkgname + "/PKGBUILD"
        try:
            pkgbuild = urllib.urlopen(url)
        except IOError:
            self.io.put("#{RED}PROXY error?#{NONE}")
            return False
        for number, line in enumerate(pkgbuild):
            if line.startswith("<?xml version="):
                self.io.put("No PKGBUILD found")
                return False
            # show line number
            self.io.put("#{_BLUE}#{WHITE}  %2d #{NONE} " % (number + 1),
                    newline=False)
            if line.startswith("#"):
                self.io.put("#{GRAY}%s" % line, newline=False)
            elif "=" in line:
                l, r = line.split("=", 1)
                self.io.put("#{blue}%s#{NONE}=%s" % (l, r),
                        newline=False)
            else:
                self.io.put("#{gray}%s#{none}" % line, newline=False)
        return True

    def search_with_json(self, stype, *args):
        """Returns converted JSON object from given url"""
        url_args = "&arg=" + "&arg=".join(args)
        url_type = "?type=" + stype
        url = self.url_json + url_type + url_args
        try:
            json_obj = urllib.urlopen(url).read()
        except IOError:
            self.io.put("#{RED}PROXY error?#{NONE}")
            return False
        result = json.loads(json_obj)
        if result['type'] == "error":
            #self.io.put("#{BOLD}AUR :#{NONE} %s" % result['results'])
            return None
        return result['results']

    def do_search(self, *pkgnames):
        """Search package in AUR"""
        if not pkgnames:
            return False
        result = self.search_with_json("search", *pkgnames)
        if not result:
            return False
        else:
            for numb, pkg in enumerate(result):
                # add package name to memmory
                self.pkg_list.append(pkg['Name'])
                # mark searched word
                if self.conf.aur_mark_searchword:
                    pkg['Name'] = pkg['Name'].replace(
                            pkgnames[0], "#{%s}%s#{NONE}" % \
                                (self.conf.aur_mark_searchword, pkgnames[0]))
                self.io.put(" #{BLUE}%3d#{NONE}  %s" % (numb+1, pkg['Name']))
        return True

    def single_pkg_info(self, pkgname, *ignore):
        """Show more info about package"""
        result = self.search_with_json("info", pkgname)
        if not result:
            return False
        else:
            self.io.put("#{BLUE}%s#{blue} : %s#{NONE}" % \
                    ("Name".rjust(18), result["Name"]))
            for key in result:
                if not key in ["ID", "Name", "URLPath"] and result[key]:
                    self.io.put("#{GREEN}%s#{NONE} : %s" % \
                            (key.rjust(18), result[key]))
            self.io.put("       #{GREEN}Link to AUR#{NONE} : %s" % \
                    self.url_id + result['ID'])
        return True

    def do_info(self, *pkgnames):
        """Like `search`, but show more info"""
        pkgs = self.search_with_json("search", *pkgnames)
        if not pkgs:
            return False
        pkgs_len = len(pkgs)
        show_numb = 6
        if pkgs_len > show_numb:
            self.io.put("#{YELLOW}%d packages found, but I'll show only %d.#{NONE}" %\
                (pkgs_len, show_numb))
            pkgs = pkgs[:show_numb]
        for pkg in pkgs:
            self.single_pkg_info(pkg['Name'])
            self.io.put("")
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

    def do_upgrade(self, *ignore):
        for pkg in os.popen("pacman -Qm"):
            pkg_name, pkg_ver = pkg.split()
            aur_list = self.search_with_json('info', pkg_name)
            try:
                aur_pkg_ver = aur_list['Version']
                if aur_pkg_ver and pkg_ver != aur_pkg_ver:
                    self.io.put('%s %s - #{blue}%s#{NONE}' % \
                            (pkg_name.ljust(20), pkg_ver.rjust(14), aur_pkg_ver))
            except (TypeError, KeyError):
                pass



