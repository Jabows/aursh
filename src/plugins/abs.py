import string
import os
import sys
import re
import shutil

# NEVER import like that, it just WON'T work
# (it won't load other modules)
# from basicabs import BasicABS
import basicabs

class Plugin_abs(basicabs.BasicABS):
    """Do some stuff with ABS. Search, compile, install. 
    """
    def __init__(self, io, conf):
        # TODO [ 18:07 - 17.03.2008 ] 
        basicabs.BasicABS.__init__(self, io, conf)
        self.io = io
        self.conf = conf

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

    def do_edit(self, pkgname, *ignore):
        if not self.edit_file(pkgname):
            self.io.put("No PKGBUILD found.")

    def do_copy(self, pkgname, *ignore):
        """Copy files from ABS to users build directory"""
        self.copy(self.abs_search(pkgname))

    def do_compile(self, pkgname, *ignore):
        """Run conf.compile_cmd in given path"""
        if not self.makepkg(pkgname):
            self.copy(self.abs_search(pkgname))
            return self.makepkg(pkgname)

    def do_install(self, pkgname, *ignore):
        """Install package from conf.build_path + pkgname."""
        if not self.install(pkgname):
            self.io.put(" #{BOLD}No package found. You have to compile it first.#{NONE}")

