#!/usr/bin/python
# -*- coding: utf-8-*-

"""
Configuration file.
"""
import os





alias = {
    "compile"   : "base makepkg",
    "makepkg"   : "base makepkg",
    "install"   : "base install",
    "edit"      : "base edit",
    "copy"      : "base copy",
    "builddir"  : "base builddir",
    "aur install" : "aur info ; aur download ; base makepkg ; base install << ",
    # Pacman-like commands
    "-Ss"       : "aur search",
    "Ss"        : "aur search",
    "-S"        : "aur download ; base makepkg ; base install << ",
    "S"         : "aur download ; base makepkg ; base install << ",
    "-Si"       : "aur info ",
    "Si"        : "aur info ",
    "-Sw"       : "aur download ",
    "Sw"        : "aur download ",
    "Su"        : "aur upgrade",
}


# use color output? [True/False]
use_colors = True

plugins_path = os.path.join(os.getcwd(), "plugins/")

# history file, by default in home dir
history_file = os.path.join(os.path.expanduser("~"), ".aurshell_history")

history_length = 500

# package build path, by default in home dir
build_dir = os.path.join(os.path.expanduser("~"), "aurshell")

# how to install package? DON'T use aurshell as root!
install_cmd = "sudo pacman -U "

# compile command
compile_cmd = "makepkg -f "

editor = 'vim'

# separator for single line commands
cmd_separator = ";"

# send list of arguments to many commands
# abs search {cmd_separator} aur search << vim xorg
# where {cmd_separator} is ; by default
arguments_pipe = "<<"

# paint with given color, or set to '' if don't want to 
# aur_mark_searchword = ''
aur_mark_searchword = 'RED'

# proxy settings
proxy = {
    #"http"  : "http://username:password@proxy.address.com:port" ,
    #"ftp"   : "http://username:password@proxy.address.com:port" ,
    #"git"   : "http://username:password@proxy.address.com:port" ,
    # ?
        }

# ABS path
abs_path = "/var/abs"

# shell prompt
shell_prompt = "#{BOLD} aurshell #{BLUE}# #{NONE}"

# how to download web page (urllib doesn't work with google)
# use lynx, links, w3m or something similar
page_downloader = "lynx -dump "

# hello message
shell_intro = """
                 #{WHITE} Welcome to #{BLUE} aurshell#{WHITE}.#{NONE}

        Press #{BOLD}<TAB>#{NONE} twice, to list all commands.
  Type #{BOLD}help <command>#{NONE} to show help for given command.
       Edit #{BOLD}src/conf.py#{NONE} file to change settings.
          Press #{BOLD}Ctrl + d#{NONE} of type #{BOLD}quit#{NONE} to quit.
"""

