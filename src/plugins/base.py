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
    
    def create_builddir(self):
        """Creates conf.build_dir and returns True if doesn't exist,
        else returns False and do nothing
        """
        if not os.path.isdir(self.conf.build_dir):
            os.mkdir(self.conf.build_dir)
            return True
        return False

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

    def do_copy(self, path_from, path_to=None, *ignore):
        """Copy given dir do conf.build_dir"""
        if not path_to:
            path_to = self.conf.build_dir
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
                    (self.conf.build_dir, pkgname))
            return False
        os.system("cd %s && %s" % (dir, self.conf.compile_cmd))
        return True

    def do_install(self, pkgname, *ignore):
        """Install package if exist and return True. Return False if not."""
        dir = self.check_compilepath(pkgname)
        if not dir:
            self.io.put("Path #{blue}%s/#{BOLD}%s#{NONE} does not exist." % \
                    (self.conf.build_dir, pkgname))
            return False
        # list all pkg.tar.gz files
        pkglist = []
        for file in os.listdir(dir):
            if file.endswith("pkg.tar.gz"):
                pkglist.append(file)
        # If more that one *.pkg.tar.gz file found
        if len(pkglist) == 0:
            self.io.put("Make package first.")
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

