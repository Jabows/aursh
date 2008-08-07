#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#
#  io.py
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


import sys
import tty
import termios

import colorize


class InOut(object):
    def __init__(self, stdout=None, stdin=None):
        """Set Input and Output"""
        if not stdout:
            self.stdout = sys.stdout
        else:
            self.stdout = stdout
        if not stdin:
            self.stdin = sys.stdin
        else:
            self.stdin = stdin
        self.colorize = colorize.Colorize()

    def put(self, message, newline=True):
        """Write to output"""
        msg_out = message
        # colorize only stdout
        msg_out = self.colorize(message)
        if newline:
            msg_out = msg_out + " \n"
        self.stdout.write(msg_out)

    def newline(self):
        self.stdout.write("\n")

    def getch(self, message=None, newline=False):
        if message:
            self.put(message, newline)
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(sys.stdin.fileno())
            gotchar = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return gotchar
        

    def get(self, message=None, newline=False):
        """Read from input"""
        if message:
            self.put(message, newline)
        return self.stdin.readline()

    def ask(self, question, good='y', bad='n', newline=False):
        """Ask question and return True or False."""
        # get default answer
        if good.isupper():
            default = True
            bad = bad.lower()
            answer = "[#{BOLD}%s#{NONE}/%s] " % (good, bad)
        else:
            default = False
            bad = bad.upper()
            good = good.lower()
            answer = "[%s/#{BOLD}%s#{NONE}] " % (good, bad)
        # print the question
        self.put(question + answer, newline)
        # get the answer
        #ans = self.stdin.readline().strip().lower()
        ans = self.getch().lower()
        self.put(newline=True)
        if ans == good.lower():
            return True
        elif ans == bad.lower():
            return False
        # return default value
        return default
