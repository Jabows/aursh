#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#
#  colorize.py
#
#  Copyright (C) 2008 by Piotr Husiatyński <phusiatynski@gmail.com>
# 
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301,
#  USA.
#


import re


class Colorize(object):
    def __init__(self, colors_dict={}):
        self.colors = ColorsTemplate(colors_dict)
        self.rx = re.compile("|".join(map(re.escape, self.colors.keys())))

    def colorize(self, message):
        def change(match):
            return self.colors[match.group(0)]
        return self.rx.sub(change, message)

    def __call__(self, message):
        return self.colorize(message)


class ColorsTemplate(dict):
    def __init__(self, colors={}, mono=False):
        self.template = "#{%s}"
        self.mono = mono
        # colors escape symbols
        self._colors = {
                "none"          : "\033[0m",
                "NONE"          : "\033[0m",
                "bold"          : "\033[1m",
                "BOLD"          : "\033[1m",
                "red"           : "\033[0;31m",
                "RED"           : "\033[1;31m",
                "black"         : "\033[0;30m",
                "BLACK"         : "\033[1;30m",
                "green"         : "\033[0;32m",
                "GREEN"         : "\033[1;32m",
                "brown"         : "\033[0;33m",
                "BROWN"         : "\033[1;33m",
                "blue"          : "\033[0;34m",
                "BLUE"          : "\033[1;34m",
                "magenta"       : "\033[0;35m",
                "MAGENTA"       : "\033[1;35m",
                "cyan"          : "\033[0;36m",
                "CYAN"          : "\033[1;36m",
                "gray"          : "\033[0;37m",
                "GRAY"          : "\033[1;37m",
                "darkgray"      : "\033[0;30m",
                "DARKGRAY"      : "\033[1;30m",
                "lightred"      : "\033[0;31m",
                "LIGHTRED"      : "\033[1;31m",
                "lightgreen"    : "\033[0;32m",
                "LIGHTGREEN"    : "\033[1;32m",
                "yellow"        : "\033[0;33m",
                "YELLOW"        : "\033[1;33m",
                "lightblue"     : "\033[0;34m",
                "LIGHTBLUE"     : "\033[1;34m",
                "lightmagenta"  : "\033[0;35m",
                "LIGHTMAGENTA"  : "\033[1;35m",
                "lightcyan"     : "\033[0;36m",
                "LIGHTCYAN"     : "\033[1;36m",
                "white"         : "\033[0;37m",
                "WHITE"         : "\033[1;37m",
                "_BLACK"        : "\033[0;40m",
                "_RED"          : "\033[0;41m",
                "_GREEN"        : "\033[0;42m",
                "_BLUE"         : "\033[0;44m",
            }
        self._colors.update(colors)

    def __getitem__(self, key):
        # better key checking
        if self.mono:
            return ""
        key = key[2:-1]
        return self._colors[key]

    def keys(self):
        return [self.template % c for c in self._colors.keys()]



if __name__ == "__main__":
    ct = ColorsTemplate()
    for c in ct._colors:
        print ct._colors['NONE'], ct._colors[c], c ,
