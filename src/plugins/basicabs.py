import os
import os.path
import sys
import re
import shutil


class BasicABS(object):
    """Basic ABS operations"""
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
    
    def create_builddir(self):
        """Creates conf.build_dir and returns True if doesn't exist,
        else returns False and do nothing
        """
        if not os.path.isdir(self.conf.build_dir):
            os.mkdir(self.conf.build_dir)
            return True
        return False

    def compilepath(self, pkgname):
        """Return path to pakgname in builddir or None if doesn't exit"""
        path = os.path.join(self.conf.build_dir, pkgname)
        if not os.path.isdir(path):
            return None
        return path

    def copy(self, path_from, path_to):
        """Copy `path` do conf.build_dir"""
        if os.path.isdir(path_to):
            if self.io.ask("#{GREEN}Directory exist. Delete it? #{NONE}"):
                shutil.rmtree(path_to)
            else:
                self.io.put("#{RED}Nothing to do.#{NONE}")
                return False
        shutil.copytree(path_from, path_to)
        return True

    def makepkg(self, pkgname):
        """Compile package"""
        path = self.compilepath(pkgname)
        if not path:
            return False
        os.system("cd %s && %s" % (path, self.conf.compile_cmd))
        return True

    def install(self, pkgname):
        """Install `pkgname` package"""
        path = self.compilepath(pkgname)
        if not path:
            return False
        # If more that one *.pkg.tar.gz file found
        # TODO [ 15:33 - 17.03.2008 ] 
        pass

    def edit(self, pkgname, file="PKGBUILD"):
        """Edit `file` with conf.edior.
        `file` should be in conf.build_dir/pkgname
        """
        path = self.compilepath(pkgname)
        if not path:
            return False
        os.system("%s %s" % (self.conf.edior, path))
        return True

