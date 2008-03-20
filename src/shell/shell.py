#!/usr/bin/env python
# -*- coding: UTF-8 -*-

#  Copyright (C) 17.03.2008 Piotr Husiatyński
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
 
"""
Shell class is simple shell framework. 

To use it, write some plugins that Shell would be able to use.
"""

import cmd
import string
import sys
import os
import readline

import conf
from io import InOut

__version__ = "0.1"


class Shell(cmd.Cmd):
    """Interactive shell framework.
    To use it, write some modules, becouse by default it's very poor shell.
    """
    def __init__(self):
        cmd.Cmd.__init__(self)
        self.conf = conf
        # use this instead of plain `print`
        self.io = InOut()
        self.io.colorize.colors.mono = not self.conf.use_colors
        # load as plugins all class that name stasts with class_prefix
        self.class_prefix = "Plugin_"
        # use all methods that name stasts with method_prefix
        self.method_prefix = "do_"
        self.prompt = self.io.colorize(self.conf.shell_prompt)
        self.intro = self.io.colorize(self.conf.shell_intro)
        # load plugins
        self.commands = self.load_plugins(self.conf.plugins_path)
        # load history
        self.load_history(self.conf.history_file, self.conf.history_length)
        # create build_dir if doesn't exist
        if not os.path.isdir(self.conf.build_dir):
            os.mkdir(self.conf.build_dir)
    
    def load_history(self, hfile, hlength):
        """load history, create empty file if history doesn't exist"""
        if not os.path.isfile(hfile):
            open(hfile, "w").close()
        readline.read_history_file(hfile)
        readline.set_history_length(hlength)

    def load_plugins(self, modules_path):
        """Load all commands modules from modules_path direcotory."""
        command_modules = []
        # adding plugins path to sys.path
        if modules_path not in sys.path:
            sys.path.append(modules_path)
        # importing all modules from modules_path
        for module_name in os.listdir(modules_path):
            module_path = os.path.abspath(
                    string.join(modules_path, module_name))
            (module_name, module_extension) = os.path.splitext(module_name)
            # if it shouldn't be loaded
            if os.path.islink(module_path) or  \
                    module_path == __file__ or \
                    module_extension != ".py":
                        continue
            for key in sys.modules.keys():
                if key == module_name:
                    del sys.modules[key]
            module = __import__(module_name)
            command_modules.append({"obj": module_name, "name": module,})
        # search for class in each module
        module_objs = {}
        for module in command_modules:
            for obj in dir(module["name"]):
                if obj.startswith(self.class_prefix):
                    try:
                        # create instance for each class
                        module_objs[obj[len(self.class_prefix):]] = \
                            getattr(module['name'], obj)(self.io, self.conf)
                    except TypeError:
                        pass
        return module_objs

    def precmd(self, cmd):
        """check if alias exists and if so, replace command"""
        for alias in self.conf.alias:
            # command should start with alias, but:
            # - next char should be white space, or
            # - there's no next char
            if cmd.startswith(alias) and \
                    (len(cmd) <= len(alias) or cmd[len(alias)] == " "):
                cmd = cmd.replace(alias, self.conf.alias[alias], 1)
        return cmd

    def do_shell(self, cmd):
        """System shell command, for commads which starts with !"""
        os.system(cmd)

    def emptyline(self):
        pass

    def run_command(self, cmd):
        if self.conf.cmd_separator in cmd:
            # multicommand
            for c in cmd.split(self.conf.cmd_separator):
                c = c.strip()
                self.io.put("#{GREEN}:::: running : #{green} %s #{NONE}" % c)
                self.run_single_command(c)
        else:
            # single command
            self.run_single_command(cmd)

    def run_single_command(self, cmd):
        # cmd[0] should be class name
        # cmd[1] should be method name (or arugmet if class is callable)
        # cmd[1] can be empty
        # cmd[2:] should be method argumments, can be empty
        cmd = cmd.split()
        # operations for single command with no arguments
        if len(cmd) == 1:
            # if there's no such command (or plugin class)
            if not cmd[0] in self.commands:
                self.io.put("%s : command not found." % cmd[0])
            else:
                self.io.put("%s : bad usege. Try to run help." % cmd[0])
        # if command was called with arguments
        elif len(cmd) > 1:
            # no such command
            if not cmd[0] in self.commands:
                self.io.put("%s : command not found." % cmd[0])
                return None
            cmd[1] = self.method_prefix + cmd[1]
            # if method named arg[1] exist in class arg[0], try to run it
            if cmd[1] in dir(self.commands[cmd[0]]):
                try:
                    getattr(self.commands[cmd[0]], cmd[1])(*cmd[2:])
                except TypeError:
                    self.io.put("#{BOLD}%s #{NONE}: bad usage" % \
                            cmd[1][len(self.method_prefix):])
            else:
                # try tu run __call__() method
                try:
                    cmd[1] = cmd[1][len(self.method_prefix):]
                    getattr(self.commands[cmd[0]], "__call__")(*cmd)
                except (TypeError, AttributeError):
                    self.io.put("  %s  : #{RED}bad usage#{NONE}" % cmd[0])

    def default(self, cmd, *ignore):
        """Run commands.

        cmd = (<class>, [method], [arg1], [arg2], ...)
        """
        self.run_command(cmd)

    def completenames(self, text, *ignored):
        """Complete commands"""
        dotext = self.method_prefix + text
        # local methods
        local_cmd_list = \
                [a[3:] + " " for a in self.get_names() if a.startswith(dotext)]
        # + all metrods from modules
        module_cmd_list = \
                [a + " " for a in self.commands.keys() if a.startswith(text)]
        # + all aliases
        aliases_cmd_list = \
                [a + " " for a in self.conf.alias.keys() if a.startswith(text)]
        return local_cmd_list + module_cmd_list + aliases_cmd_list

    def completedefault(self, text, line, begidx, endidx):
        """Complete commands argument"""
        dotext = self.method_prefix + text
        line = line.split()
        # if only commands was given
        if len(line) == 1:
            cmds = [a[3:] + " " for a in dir(self.commands[line[0]]) \
                    if a.startswith(dotext)]
        elif len(line) == 2:
            cmds = [a[3:] + " " for a in dir(self.commands[line[0]]) \
                    if a.startswith(dotext)]
        # else don't complete (or should I?)
        else:
            cmds = []
        return cmds

    def get_help(self, arg):
        """Return __doc__ or None if doesn't exist"""
        arg = arg.split()
        if len(arg) == 1:
            # first - search in build-in methods
            method = self.method_prefix + arg[0]
            if method in dir(self):
                doc = getattr(self, method).__doc__
                if doc:
                    return doc.replace(' ' * 4, '')
            elif arg[0] in self.commands and self.commands[arg[0]].__doc__:
                    return self.commands[arg[0]].__doc__.replace(' ' * 4, '')
        elif len(arg) == 2:
            method = self.method_prefix + arg[1]
            if arg[0] in self.commands and \
                    method in dir(self.commands[arg[0]]):
                doc = getattr(self.commands[arg[0]], method).__doc__
                if doc:
                    return doc.replace(' ' * 4, '')
        return None

    def do_help(self, arg):
        """Show help for commands
        Usage: help <command> [<argument>]
        """
        if not arg:
            self.io.put("Usage: help <command> [<argument>]")
        else:
            doc = self.get_help(arg)
            if doc:
                self.io.put("#{BOLD}%s#{NONE}" % doc)
            else:
                self.io.put("No help found.")

    def do_history(self, hnumb=None, *ignored):
        """Show the history"""
        # TODO 
        # better history listing 
        # print history
        if not hnumb:
            for n in range(1, self.conf.history_length):
                cmd = readline.get_history_item(n)
                if not cmd:
                    break
                self.io.put("%6d  %s" % (n, cmd))
        # for history range 12-22 or -22 or 22- 
        else:
            try:
                if "-" in hnumb:
                    if hnumb[-1] == "-" or hnumb[0] == "-":
                        start = int(hnumb.replace("-", " "))
                        end = self.conf.history_length
                    else:
                        start, end = hnumb.split("-")
                        start = int(start)
                        end = int(end) + 1
                    for n in range(start, end):
                        cmd = readline.get_history_item(n)
                        if not cmd:
                            break
                        self.io.put("%6d  %s" % (n, cmd))
                else:
                    hnumb = int(hnumb)
                    self.io.put(readline.get_history_item(hnumb))
            except ValueError:
                self.io.put("""#{RED}Bad value. #{NONE}
#{BOLD}Usage: history <number or range>#{NONE}
    history  11-20      from 11 to 20
    history  22-        from 22 fo the end of history file
    history  -22        same as 22-""")

    def do_clear(self, *ignored):
        # TODO [ 21:13 - 16.03.2008 ] 
        os.system('clear')

    def do_quit(self, *ignored):
        """Quit from shell"""
        if conf.history_length:
            readline.write_history_file(conf.history_file)
        self.io.put('#{BLUE}quit..#{NONE}')
        sys.exit(1)
    
    # function aliases
    do_EOF = do_quit
    do_exit = do_quit


    
