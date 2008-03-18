import string
import os
import sys
import re
import shutil


class BasicABS(object):
    """Basic ABS operations."""
    def __init__(self, io, conf):
        """io - InOut instance
        conf - configuration module
        """
        self.conf = conf
        self.io = io

    def abs_search(self, pkgname):
        """Search in ABS. Returns path or None."""
        for root, dirs, files in os.walk(self.conf.abs_path):
            for dir in dirs:
                if dir == pkgname:
                    return os.path.join(root, dir)
        return None

    def compilepath(self, pkgname):
        """Return pakgname path (don't have to exist)."""
        return os.path.join(self.conf.build_dir, pkgname)

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

    def copy(self, path_from, path_to=None):
        """Copy `path` do conf.build_dir"""
        if not path_to:
            path_to = self.conf.build_dir
            dir, pkgname = os.path.split(path_from)
            path_to = os.path.join(path_to, pkgname)
        if os.path.isdir(path_to):
            if self.io.ask("#{GREEN}Directory exist. Delete it? #{NONE}"):
                shutil.rmtree(path_to)
            else:
                self.io.put("#{RED}Nothing to do.#{NONE}")
                return False
        shutil.copytree(path_from, path_to)
        return True


class Plugin_abs(BasicABS):
    """Do some stuff with ABS. Search, compile, install. 
    """
    def __init__(self, io, conf):
        # TODO [ 18:07 - 17.03.2008 ] 
        BasicABS.__init__(self, io, conf)
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

    def do_copy(self, pkgname, *ignore):
        """Copy files from ABS to users build directory"""
        dir = self.abs_search(pkgname)
        if dir:
            self.copy(dir)
        else:
            self.io.put("No PKGBUILD found.")

    def do_install(self, pkgname, *ignore):
        """Copy files from ABS to use build directory, 
        create package, install it.
        """
        dir = self.compilepath(pkgname)
        if not os.path.isdir(dir):
            absdir = self.abs_search(pkgname)
            if absdir:
                self.copy(absdir)
            else:
                self.io.put("No PKGBUILD found.")
                return None
        if not self.check_pkgbuild(pkgname):
            self.io.put("No PKGBUILD found. Files could not copy correctly from ABS")
            return None
        # makepkg
        os.system("cd %s && %s" % \
                (dir, self.conf.compile_cmd))
        # install
        pkglist = []
        for file in os.listdir(dir):
            if file.endswith("pkg.tar.gz"):
                pkglist.append(file)
        if len(pkglist) == 0:
            self.io.put("Package #{BOLD}%s#{NONE} not found." % pkgname)
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


