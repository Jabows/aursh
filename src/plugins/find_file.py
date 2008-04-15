#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#
# find_file.py
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


from sgmllib import SGMLParser
import os


class GoogleParser(SGMLParser):
    """Google HTML Parser"""
    def reset(self):
        SGMLParser.reset(self)
        self.urls = []

    def start_a(self, attrs):
        """When inside <a> tag"""
        if not 'l' in [v for k, v in attrs if k == 'class']:
            return
        href = [v for k, v in attrs if k == 'href']
        if href:
            self.urls.extend(href)

    def get_links(self):
        """Get and clear link list"""
        urls = self.urls
        self.urls = []
        return urls

class ArchLinuxParser(SGMLParser):
    def reset(self):
        SGMLParser.reset(self)
        self.pkg_list = {'pkgname': '', 'filelist': []}
        self.in_box = False
        self.in_h3 = False

    def start_div(self, attrs):
        if "box" in [v for k, v in attrs if k == 'class']:
            self.in_box = True

    def end_div(self):
        if self.in_box:
            self.in_box = False

    def start_h3(self, attrs):
        if self.in_box:
            self.in_h3 = True

    def end_h3(self):
        if self.in_h3:
            self.in_h3 = False
            
    def handle_data(self, data):
        if self.in_h3:
            self.pkg_list['pkgname'] = data.split(":", 1)[1]
        elif self.in_box:
            self.pkg_list['filelist'].extend(
                    [l.strip() for l in data.split("<br />") if l.strip()]
                    )
    
    def get_pkg_list(self):
        pkg_l = self.pkg_list
        self.pkg_list = {'pkgname': '', 'filelist': []}
        return pkg_l


def page_source(url):
    """Download site"""
    return os.popen("lynx -source '%s' " % url).read()


def get_glink(search_words, site=None, numb=None):
    """generate [google search] link"""
    glink = "http://www.google.com/search?"
    if site:
        glink += "&as_sitesearch=" + site
    try:
        glink += "&as_q=" + search_words
    except TypeError:
        glink += "&as_q=" + "+".join(search_words)
    if numb <= 100 and numb > 0:
        glink += "&num=%d" % numb
    return glink

def google_search(args, site="http://archlinux.org/packages/files/"):
    """Get link list from google"""
    parser = GoogleParser()
    g_url = get_glink(args, site=site, numb=100)
    parser.feed(page_source(g_url))
    return parser.get_links()


def archlinux_files_list(url):
    parser = ArchLinuxParser()
    source = page_source(url)
    parser.feed(source)
    return parser.get_pkg_list()




class Plugin_find(object):
    """TODO"""
    def __init__(self, io, conf):
        self.conf = conf
        self.io = io

    def do_file(self, filename, *ignore):
        if filename.startswith("/"):
            filename = filename[1:]
        g_links = google_search((filename,))
        for link in g_links:
            result = archlinux_files_list(link)
            self.io.put("#{BLUE}%s#{NONE}" % result['pkgname'])
            for file in result['filelist']:
                if filename in file:
                    self.io.put("    %s" % file.replace(
                        filename, "#{red}%s#{NONE}" % filename))

