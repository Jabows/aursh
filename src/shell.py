#!/usr/bin/env python
# -*- coding: UTF-8 -*-

"""
Aur Shell is simple shell framework. 

To use it, write some plugins that Aur Shell would use.
"""

import cmd
import string
import sys
import os
import os.path
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
        # use this instead of plain `print`
        self.io = InOut()
        self.conf = conf
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
                        # check if it's method
                        x = getattr(module['name'], obj)(self.io, conf)
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

    def default(self, cmd=None):
        """Run commands.

        cmd = (<class>, [method], [arg1], [arg2], ...)
        """
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
                    # show __doc__ if exist
                    doc = getattr(self.commands[cmd[0]], cmd[1])
                    if doc.__doc__:
                        self.io.put(doc.__doc__)
                    else:
                        self.io.put("%s : bad usage" %
                                cmd[1][len(self.method_prefix):])
            else:
                # try tu run __call__() method
                try:
                    cmd[1] = cmd[1][len(self.method_prefix):]
                    getattr(self.commands[cmd[0]], "__call__")(*cmd)
                except (TypeError, AttributeError):
                    self.io.put("  %s  : #{RED}bad usage#{NONE}" % cmd[0])

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

    def do_help(self, arg):
        """Show help for commands
        Usage: help <command> [<argument>]
        """
        arg = arg.split()
        if not arg:
            self.io.put("Usage: help <command> [<argument>]")
        elif len(arg) == 1:
            # first - build-in methods
            if self.method_prefix + arg[0] in dir(self):
                doc = getattr(self, self.method_prefix + arg[0]).__doc__
                if doc:
                    self.io.put(doc)
            # modules help
            else:
                try:
                    # try to run help() method
                    self.io.put(getattr(self.commands[arg[0]], "help")())
                except AttributeError:
                    # try to show __doc__
                    if self.commands[arg[0]].__doc__:
                        self.io.put(self.commands[arg[0]].__doc__)
                    else:
                        self.io.put("No help found.")
                except KeyError:
                    self.io.put("No help found.")

        elif len(arg) == 2:
            try:
                if arg[0] in self.commands:
                    arg[1] = self.method_prefix + arg[1]
                    doc = getattr(self.commands[arg[0]], arg[1]).__doc__
                    if doc:
                        self.io.put(doc)
                    else:
                        raise AttributeError
            except AttributeError:
                self.io.put("#{BOLD} %s #{NONE}: no help found" % arg[1][3:])
        else:
            self.io.put(self.do_help.__doc__)

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
    history 11-20  -> from 11 to 20
    history 22-     -> from 22 fo the end of history file
    history -22     -> same as 22-""")

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


    

