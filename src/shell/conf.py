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
    "h"         : "history",
    "info"      : "help",
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

# arguments template
# example: abs search something; abs install {{1}} 
# for runnging abs search somethins and then abs install something
arg_list_template = "{{arg}}"

# AUR url
aur_url = "http://aur.archlinux.com"

# ABS path
abs_path = "/var/abs"

# shell prompt
shell_prompt = " #{BLUE}[ #{NONE}aurshell #{BLUE}] #{NONE}"

# hello message
shell_intro = """
            #{BOLD} Welcome to #{BLUE} aurshell #{NONE}

    Press #{BOLD}<TAB>#{NONE} twice, to list all commands.
      Press #{BOLD}Ctrl + d#{NONE} of type #{BOLD}quit#{NONE} to quit.
"""
