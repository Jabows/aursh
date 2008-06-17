#!/usr/bin/python
# -*- coding: utf-8-*-
#
#  conf.py
# 
#  Copyright 2008 Piotr Husiatyński <phusiatynski@gmail.com> 
# 
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#  
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#  
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
#  





"""
Configuration file.
"""
import os
import sys


class ConfFileParser(object):
    """Configuration file parser, similar to those in ConfigParser"""
    def __init__(self, file_dir=None):
        self.configuration = {}
        if file_dir:
            self.read(file_dir)

    def read(self, file_dir):
        """Read/parse configuration file"""
        self.configuration = {}
        # default name for section
        section = 'none'
        for (line_numb, line) in enumerate(open(file_dir, "r")):
            line = line.strip()
            # enter new section
            if line.startswith("[") and line.endswith("]"):
                section = line[1:-1]
                self.configuration[section] = {}
            # comment, empty line
            elif not line or line.startswith("#"):
                continue
            # new option
            else:
                try:
                    name, value = line.split("=", 1)
                    self.configuration[section][name.strip()] = value.strip()
                except (ValueError):
                    print("Configuration file error: %3d : %s" % (line_numb + 1, line))

    def sections(self):
        """Return list of sections"""
        return self.configuration.keys()

    def options(self, section):
        """Return list of options from given section"""
        return self.configuration[section]

    def get(self, section, option):
        """Return value of given option"""
        return self.configuration[section][option]


class Configuration(object):
    alias = { }
    # use color output? [True/False]
    use_colors = "True"
    plugins_path = os.path.join(os.getcwd(), "plugins/")
    # history file, by default in home dir
    history_file = os.path.join(os.path.expanduser("~"), ".aurshell_history")
    history_length = 500
    # package build path, by default in home dir
    build_dir = os.path.join(os.path.expanduser("~"), "aurshell")
    # /etc/makepkg.conf file reader?
    makepkg_pkgdest = None
    # how to install package? DON'T use aurshell as root!
    install_cmd = "sudo pacman -U "
    # compile command
    compile_cmd = "makepkg -f "
    editor = 'vim'
    # separator for single line commands
    cmd_separator = ";"
    # send list of arguments to many commands
    arguments_pipe = "<<"
    # paint with given color, or set to '' if don't want to 
    mark_searchword = 'RED'
    # proxy settings
    proxy = {
        #"http"  : "http://username:password@proxy.address.com:port" ,
        #"ftp"   : "http://username:password@proxy.address.com:port" ,
            }
    # ABS path
    abs_path = "/var/abs"
    # shell prompt
    shell_prompt = "#{BOLD} aurshell #{BLUE}# #{NONE}"
    # how to download web page (urllib doesn't work with google)
    page_downloader = "lynx -dump "
    shell_intro = """
                 #{WHITE} Welcome to #{BLUE} aurshell#{WHITE}.#{NONE}

        Press #{BOLD}<TAB>#{NONE} twice, to list all commands.
  Type #{BOLD}help <command>#{NONE} to show help for given command.
       Edit #{BOLD}src/conf.py#{NONE} file to change settings.
          Press #{BOLD}Ctrl + d#{NONE} of type #{BOLD}quit#{NONE} to quit.
"""

    def __getattr__(self, name):
        if not name in self.__dict__:
            raise AttributeError("%s object has no attribute '%s'" % \
                    (self.__class__.__name__, name))
        return getattr(self, name)

    def __setattr__(self, name, value):
        if not name in dir(self):
            raise AttributeError("%s object has no attribute '%s'" % \
                    (self.__class__.__name__, name))
        #setattr(self, attr_name, value)
        self.__dict__[name] = value

    def __init__(self):
        """load user configuration"""
        conf_file = os.path.expanduser("~/.aurshell")
        if os.path.isfile(conf_file):
            config = ConfFileParser(conf_file)
            if 'base' in config.sections():
                for option in config.options('base'):
                    try:
                       self.__dict__[option] = config.get('base', option)
                    except (AttributeError):
                        print("Bad configuration option : %s" % option)
            if 'alias' in config.sections():
                for option in config.options('alias'):
                    self.alias[option] = config.get('alias', option)

            if 'proxy' in config.sections():
                for option in config.options('proxy'):
                    self.proxy[option] = config.get('proxy', option)


# change module with class object (tricky!)
sys.modules[__name__] = Configuration()
