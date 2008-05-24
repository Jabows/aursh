#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#
# pacman.py
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



import os

class ColorPacman(object):
    def __init__(self):
        # TODO 
        # better colorize method. use regexp?
        self.colorize = {
                'core': "#{blue}%s#{none}/#{BLUE}%s#{NONE}",
                'extra': "#{yellow}%s#{none}/#{YELLOW}%s#{NONE}",
                'community' : "#{green}%s#{none}/#{GREEN}%s#{NONE}",
                'testing' : "#{magenta}%s#{none}/#{MAGENTA}%s#{NONE}",
                'unstable' : "#{red}%s#{none}/#{RED}%s#{NONE}",
                }

    def color(self, text):
        for key in self.colorize:
            try:
                if text.startswith(key):
                    # change text to color output
                    return self.colorize[key] % tuple(text.split("/", 1))
            except (IndexError):
                pass
        return text

class Plugin_pacman(object):
    """Pipe to pacman"""
    def __init__(self, io, conf):
        self.io = io
        self.conf = conf
        self.pacman_cmd = "pacman"
        self.colorize = ColorPacman()

    def __call__(self, *args):
        """Pipe to pacman"""
        os.system("%s %s" % (self.pacman_cmd, " ".join(args)))

    def do_search(self, *args):
        """Simple -Ss call, but with color output"""
        result = os.popen("pacman -Ss %s" % " ".join(args))
        for line in result:
            line = line.rstrip()
            self.io.put(self.colorize.color(line))
