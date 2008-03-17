import string
import os
import os.path
import sys
import re
import shutil

from basicabs import BasicABS


class Plugin_abs(BasicABS):
    """Do some stuff with ABS. Search, compile, install. 
    Everything that you need to be happy..
    """
    def __init__(self, io, conf):
        self.io = io
        self.conf = conf
        # TODO [ 18:07 - 17.03.2008 ] 
        BasicABS.__init__(self, io, conf)

    def do_search(self, pkgname, *ignore):
        """Find PKGBUILDs in ABS file tree and show them."""
        for root, dirs, files in os.walk(self.conf.abs_path):
            for d in dirs:
                if pkgname in d:
                    try:
                        name = str(d)
                        ver = ""
                        for line in open(os.path.join(root, d, "PKGBUILD"), "r"):
                            if line.startswith("pkgver"):
                                ver = line.split("=")[1][:-1]
                        self.io.put(" #{BLUE}%s #{WHITE} %s #{NONE} %s" % \
                                (name.ljust(32), ver.ljust(10), root))
                    except IOError:
                        pass

    def do_copy(self, pkgname, *ignore):
        """Copy files from ABS to users build directory"""
        self.copy(self.aursearch(pkgname))

    def do_compile(self, pkgname, *ignore):
        """Run conf.compile_cmd in given path"""
        if not self.makepkg(pkgname):
            dir = self.check_compilepath(pkgname)
            if not dir:
                self.io.put("Can't find PKGBUILD.")
                return False
            else:
                self.makepkg(pkgname)
        return True

    def do_install(self, pkgname, *ignore):
        """Install package from conf.build_path + pkgname."""
        dir = self.compilepath(pkgname)
        if not dir:
            self.do_compile(pkgname)
        self.install(pkgname)


    # alias
    do_edit = BasicABS.edit
