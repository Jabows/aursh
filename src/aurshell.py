#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#
# aurshell.py
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



import sys
import os

from shell import shell
import conf


def signal_handler(sig, frame):
    pass


if __name__ == '__main__':
    # run in single command mode
    # only if arguments were given
    if len(sys.argv) > 1:
        aurshell = shell.Shell(conf)
        aurshell.default(" ".join(sys.argv[1:]))
        sys.exit()
    else:
    # run shell
        try:
            aursh = shell.Shell(conf)
            aursh.cmdloop()
        except KeyboardInterrupt:
            # TODO [ 23:18 - 15.03.2008 ] 
            # C^c shouldn't quit shell
            pass
    
