# -*- coding: utf-8 -*-


from core import errors
from core.plugin import Plugin, plugin_command



class Help(Plugin):
    "Show help about other plugins and commands"

    @plugin_command('help')
    def help(self, *args):
        "Show help for given plugin or command"
        if len(args) == 1:
            # TODO - print plugin help
            return
        if len(args) == 2:
            # TODO - print plugin handler help
            return
        raise errors.BadUsage('Too much arguments')
