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


class Plugin_pacman(object):
    """Pipe to pacman"""
    def __init__(self, io, conf):
        self.io = io
        self.conf = conf
        self.pacman_cmd = "pacman"

    def __call__(self, *args):
        """Pipe to pacman"""
        os.system("%s %s" % (self.pacman_cmd, " ".join(args)))

