#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#
# proxy.py
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
import urllib2


class Plugin_proxy(object):
    """Do some stuff with proxy"""
    def __init__(self, io, conf):
        """io - InOut instance
        conf - configuration module
        """
        self.conf = conf
        self.proxy = self.conf.proxy
        self.io = io
        self.set_proxy()

    def __call__(self):
        self.do_show()

    def set_proxy(self):
        """Set the proxy"""
        # TODO [ 11:21 - 02.04.2008 ] 
        # too tricky way of setting proxy...
        opener = urllib.FancyURLopener(self.conf.proxy)
        urllib.urlopen = opener.open
        urllib.urlretrieve = opener.retrieve

    def do_show(self, proxy_type=None, *ingore):
        """Show proxy"""
        if proxy_type:
            if not proxy_type in self.proxy:
                self.io.put("No proxy set")
                return False
            else:
                self.io.put("#{GREEN}%s#{NONE} : %s" % \
                        (proxy_type.rjust(6), self.proxy[proxy_type]))
                return True
        else:
            for key in self.proxy:
                self.io.put("#{GREEN}%s#{NONE} : %s" % \
                        (key.rjust(6), self.proxy[key]))
        return True

    def do_set(self, proxy_type, proxy_addr, *ignore):
        """Set proxy for current session. 
        set  <proxy type>  <proxy addr>
        set http http://some.proxy.com:8080
        """
        self.proxy[proxy_type] = proxy_addr
        self.set_proxy()
        return True

    def do_drop(self, *ignore):
        """Drop all proxy settings for current session"""
        self.proxy = {}
