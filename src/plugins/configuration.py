#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#
# configuration.py
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



class Plugin_conf(object):
    """Set configuration values"""
    def __init__(self, io, conf):
        """io - InOut instance
        conf - configuration module
        """
        self.conf = conf
        self.io = io

    def __call__(self, *ignore):
        self.io.put(self.__doc__)

    def complete(self, text):
        """Complete args"""
        method = text.split()[1]
        if not method in ['show', 'set']:
            return []
        if text.endswith(" "):
            return self.get_conf_args()
        else:
            last = text.split()[-1]
            return [c for c in self.get_conf_args() if c.startswith(last)]

    def get_conf_args(self):
        return [c for c in dir(self.conf) if not c.startswith("_") and \
                type(getattr(self.conf, c)) == type("string")]

    def do_show(self, conf_name=None, *ingore):
        """Show configuration value"""
        if not conf_name:
            for key in self.get_conf_args():
                self.io.put(" #{blue} %s #{NONE}%s" % \
                        (key.ljust(30, "."), getattr(self.conf, key)))
            return True
        if conf_name in dir(self.conf):
            self.io.put("  #{BLUE}%s  :  #{none}%s" % \
                    (conf_name, getattr(self.conf, conf_name)) )
            return True
        else:
            self.io.put("#{RED}Nothing to show.#{NONE}")
            return False

    def do_set(self, name, *values):
        """Set settings option:

        #{BOLD}conf set  <name>  <value>#{NONE}
        """
        if len(values) < 1:
            self.io.put(self.do_set.__doc__)
            return False
        setattr(self.conf, name, " ".join(values))
        self.do_show(name)
        
