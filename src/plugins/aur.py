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



class Plugin_aur(object):
    """Do some stuff with AUR. Search and download files."""
    def __init__(self, io, conf):
        self.io = io
        self.conf = conf

    def __call__(self, *ignore):
        self.io.put("#{RED}TODO#{NONE}\nNothing more...")
    
    def do_search(self, pkgname, *ignorepkg):
        """Search package in AUR"""
        self.io.put("#{BOLD}TODO#{NONE}")

    def do_download(self, pkgname, *ignorepkg):
        """Download files from AUR"""
        self.io.put("#{BOLD}TODO#{NONE}")

    def do_install(self, pkgname, *ignorepkg):
        """Download and install package from AUR"""
        self.io.put("#{BOLD}TODO ?#{NONE}")
