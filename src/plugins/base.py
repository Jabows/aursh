#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#
# base.py
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



import shutil
import os
import sys
import re


class Plugin_base(object):
    """Basic ABS operations."""
    def __init__(self, io, conf):
        """io - InOut instance
        conf - configuration module
        """
        self.conf = conf
        self.io = io

    def do_builddir(self, bdir=None, *ignore):
        """Set build dir, or just show it"""
        if bdir:
            if not os.path.isdir(bdir):
                if self.io.ask("#{GREEN}Create directory? #{NONE}"):
                    os.mkdir(bdir)
                else:
                    bdir = self.conf.build_dir
            self.conf.build_dir = bdir
        self.io.put("#{GREEN}Build directory: #{NONE}" + self.conf.build_dir)
        return True

    def create_builddir(self):
        """Creates conf.build_dir and returns True if doesn't exist,
        else returns False and do nothing
        """
        if not os.path.isdir(os.path.expanduser(self.conf.build_dir)):
            os.mkdir(os.path.expanduser(self.conf.build_dir))
            return True
        return False

    def compilepath(self, pkgname):
        """Return pakgname path (don't have to exist)."""
        return os.path.join(os.path.expanduser(self.conf.build_dir), pkgname)

    def check_compilepath(self, pkgname):
        """Return path to pakgname in builddir or None if doesn't exit"""
        dir = self.compilepath(pkgname)
        if not os.path.isdir(dir):
            return None
        return dir

    def check_pkgbuild(self, pkgname):
        """Bla bla bla"""
        pkgfile = os.path.join(self.compilepath(pkgname), "PKGBUILD")
        if not os.path.isfile(pkgfile):
            return None
        return self.compilepath(pkgname)

    def do_copy(self, path_from, path_to=None, *ignore):
        """Copy given dir do conf.build_dir"""
        if not path_to:
            path_to = os.path.expanduser(self.conf.build_dir)
            dir, pkgname = os.path.split(path_from)
            path_to = os.path.join(path_to, pkgname)
        if not os.path.isdir(path_from):
            self.io.put("#{GREEN}%s #{NONE} does not exist." % path_from)
            return False
        elif os.path.isdir(path_to):
            if self.io.ask("#{GREEN}Directory exist. Delete it? #{NONE}"):
                shutil.rmtree(path_to)
            else:
                self.io.put("#{RED}Nothing to do.#{NONE}")
                return False
        shutil.copytree(path_from, path_to)
        return True

    def do_makepkg(self, pkgname, *ignore):
        """Compile package"""
        dir = self.check_pkgbuild(pkgname)
        if not dir:
            self.io.put("Path  #{BOLD}%s/%s#{NONE}  does not exist." % \
                    (os.path.expanduser(self.conf.build_dir), pkgname))
            return False
        os.system("cd %s && %s" % (dir, self.conf.compile_cmd))
        return True

    def do_install(self, pkgname, *ignore):
        """Install package if exist and return True. Return False if not."""
        # if PKGDEST in /etc/makepkg.conf is set, this should be
        # also set in user configuration file and return True.
        # By default it's None
        if self.conf.makepkg_pkgdest:
            dir = self.conf.makepkg_pkgdest
        else:
            dir = self.check_compilepath(pkgname)
        if not dir:
            self.io.put("Path #{blue}%s/#{BOLD}%s#{NONE} does not exist." % \
                    (os.path.expanduser(self.conf.build_dir), pkgname))
            return False
        # list all pkg.tar.gz files
        pkglist = []
        for file in os.listdir(dir):
            if file.endswith("pkg.tar.gz"):
                pkglist.append(file)
        # If more that one *.pkg.tar.gz file found
        if len(pkglist) == 0:
            self.io.put("#{RED}! #{WHITE}No package Found.#{NONE}")
            return False
        elif len(pkglist) == 1:
            pkgfile = pkglist[0]
        else:
            self.io.put("#{BLUE}More than one package found. Please choose one:#{NONE}\n")
            for n, pkg in enumerate(pkglist):
                self.io.put("#{GREEN}  %2d . . .#{WHITE} %s#{NONE}" % (n, pkg))
            i = self.io.get("\n#{BLUE}Enter number, or press Enter to abort : #{NONE}")
            try:
                i = int(i)
            except ValueError:
                return True
            if i > len(pkglist) - 1 or i < 0:
                self.io.put("#{RED}Bad value #{WHITE}- out of range.#{NONE}")
                return True
            pkgfile = pkglist[i]
        os.system("cd %s && %s %s" % (dir, self.conf.install_cmd, pkgfile))
        return True

    def do_validate(self, pkgname, *ignore):
        """Validate PKGBUILD. Edit it if not correct"""
        # arch=
        pkg_file_path = os.path.join(self.compilepath(pkgname), "PKGBUILD")
        if not os.path.isfile(pkg_file_path):
            self.io.put("#{RED}%s #{NONE}: No local PKGBUILD found" % pkgname)
            return False
        validator = (
                [re.compile(r'^arch=(.*)'),  "No arch=() info"],
                )
        for line in open(pkg_file_path, "r"):
            for v in validator:
                if v[0].match(line):
                    # set second value to None (no info)
                    v[1] = None
        run_edit = False
        for v in validator:
            if v[1]:
                run_edit = True
                self.io.put("#{YELLOW}VALIDATE ERROR: #{NONE}%s#{NONE}" % v[1])
        if run_edit:
            self.io.get()
            self.do_edit(pkgname)
        return True

    def do_edit(self, pkgname, file="PKGBUILD", *ignore):
        """Edit file with conf.edior.
        File should be in conf.build_dir/pkgname and by default, it's PKGBUILD.
        """
        efile = os.path.join(self.compilepath(pkgname), file)
        if not os.path.isfile(efile):
            self.io.put("#{BOLD}%s#{RED} does not exist.#{NONE}" % efile)
            filepath = os.path.split(efile)[0]
            try:
                for n, f in enumerate(os.listdir(filepath)):
                    self.io.put("   #{WHITE}%2d #{GREEN} %s #{NONE}" % (n, f))
            except OSError:
                # no such directory
                pass
            return False
        os.system("%s %s" % (self.conf.editor, efile))
        return efile

    def do_ask_edit(self, pkgname, file='PKGBUILD', *ignore):
        'Ask if edit file'
        if self.io.ask('Want to edit %s?' % file):
            self.do_edit(pkgname, file)
        return True

    def do_remove_pkgfiles(self, pkgname, *ignore):
        """Remove all files from build directory"""
        pkgpath = os.path.join(os.path.expanduser(self.conf.build_dir), pkgname)
        if not os.path.isdir(pkgpath):
            self.io.put("#{RED}! #{WHITE}Directory does not exist.#{NONE}")
            return False
        self.io.put("#{BLUE}Removing: #{NONE}%s" % pkgpath)
        shutil.rmtree(pkgpath)

    def do_check_depends(self, pkgname, filename='PKGBUILD', *ignore):
        '''Check if all required packages are installed
        Returns None is not or list of required packages.
        '''
        pkginfo_file_path = os.path.join(
                os.path.expanduser(self.conf.build_dir), pkgname, filename)
        if not os.path.isfile(pkginfo_file_path):
            self.io.put('#{RED}%s #{red}file not found.#{NONE}' % filename)
            return False
        pkginfo = open(pkginfo_file_path).read()
        import re
        pkg = re.findall(re.compile(r'depends=\((?P<pkglist>.+?)\)', re.DOTALL),
                pkginfo)
        # remove ', " and >=anything
        pkg = re.compile(r'(\'|\"|\>\=.[^\s]*)').sub('', pkg[0])
        pkglist = pkg.split()
        if not pkglist:
            return None
        for installedpkg in os.popen('pacman -Q'):
            if installedpkg.split()[0] in pkglist:
                pkglist.remove(installedpkg.split()[0])
        if pkglist:
            self.io.put('#{BLUE}Missing packages: #{NONE}%s' %
                    ','.join(pkglist))
        return pkglist
