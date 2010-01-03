# -*- coding: utf-8 -*-

import functools

from core import errors


registered_plugins = {}

PLUGIN_CMD_TOKEN = '_plugin_command_name'


class MetaPlugin(type):

    # ignore plugins with followed names
    IGNORE_PLUGINS = set(['Plugin', ])

    def __new__(cls, name, bases, dct):
        klass = type.__new__(cls, name, bases, dct)
        # create plugin instance and register
        if not name in MetaPlugin.IGNORE_PLUGINS \
                and name not in registered_plugins:
            registered_plugins[name.lower()] = klass()
        return klass


class Plugin(object):

    __metaclass__ = MetaPlugin

    class BadUsage(errors.BadUsage):
        "Raised when plugin command was called with bad arguments"
        pass

    def handle_command(self, *args):
        if not args:
            return self()
        command = args[0]
        params = args[1:]
        handler = self.get_all_commands()[command]
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
                raise Plugin.BadUsage(func.__doc__)
        setattr(wrapper, PLUGIN_CMD_TOKEN, cmd_name)
        return wrapper
    return decorator
