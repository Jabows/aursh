# -*- coding: utf-8 -*-

import functools

from core import errors
from core.conf import configuration
from core.tools import format_docstring
from core.io import IO


registered_plugins = {}

PLUGIN_CMD_TOKEN = '_plugin_command_name'


class MetaPlugin(type):

    # ignore plugins with followed names
    IGNORE_PLUGINS = set(['Plugin', 'AliasPlugin'])

    def __new__(cls, name, bases, dct):
        klass = type.__new__(cls, name, bases, dct)
        # create plugin instance and register
        if not name in MetaPlugin.IGNORE_PLUGINS \
                and name not in registered_plugins:
            registered_plugins[name.lower()] = klass()
        return klass


class Plugin(object):

    __metaclass__ = MetaPlugin

    io = IO()

    class BadUsage(errors.BadUsage):
        "Raised when plugin command was called with bad arguments"
        pass

    def __call__(self):
        plugin_doc = format_docstring(self, 18)
        plugin_name = type(self).__name__.lower()
        self.io.put()
        self.io.put('%15s: %s' % (plugin_name, plugin_doc))
        self.io.put('   ' + '_' * 60)
        self.io.put()
        all_commands = self.get_all_commands()
        for (name, handler) in all_commands.iteritems():
            help_msg = format_docstring(handler, 18)
            self.io.put('%15s - %s' % (name, help_msg))


    def handle_command(self, *args):
        if not args:
            return self()
        command = args[0]
        params = args[1:]
        all_handlers = self.get_all_commands()
        handler = all_handlers.get(command, None)
        if handler is None:
            raise errors.UnknownCommand('Unknown command: %s' % command)
        return handler(*params)

    def get_all_commands(self):
        """Return dict with all command attributes that current plugin
        provides.

        """
        if not hasattr(self, '_get_all_commands'):
            all_commands = {}
            for name in dir(self):
                attr = getattr(self, name)
                cmd_name = getattr(attr, PLUGIN_CMD_TOKEN, None)
                if not cmd_name:
                    continue
                all_commands[cmd_name] = attr
            self._get_all_commands = all_commands
        return self._get_all_commands


class AliasPlugin(Plugin):
    def __init__(self, cmd_path):
        super(AliasPlugin, self).__init__()
        self.cmd_path = cmd_path

    def handle_command(self, *args):
        plugin = registered_plugins[self.cmd_path[0]]
        handler = plugin.get_all_commands()[self.cmd_path[1]]
        params = list(args[2:])
        params.extend(args)
        return handler(*params)


def plugin_command(cmd_name):
    """All objects decorated with this function will be used as application
    commands.
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwds):
            try:
                return func(*args, **kwds)
            except TypeError:
                err = ''
                doc = func.__doc__
                if doc:
                    err = '\n'.join(l.strip() for l in doc.split('\n'))
                raise Plugin.BadUsage(err)
        setattr(wrapper, PLUGIN_CMD_TOKEN, cmd_name)
        return wrapper
    return decorator

def load_plugin_commands_aliases():
    for (alias, path) in configuration.ALIASSES.iteritems():
        registered_plugins[alias] = AliasPlugin(path)
