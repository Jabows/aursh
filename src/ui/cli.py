# -*- coding: utf-8 -*-

import sys
import traceback

from core.plugin import AliasPlugin, registered_plugins
from core.conf import configuration
from core import errors
from core.tools import format_docstring
from core.io import IO
from core import logger


_log = logger.get('cli')



class ConsoleInterface(object):
    def __init__(self, conf):
        self.io = IO()
        self.conf = conf

    def run(self):
        try:
            command = sys.argv[1]
        except IndexError:
            self.print_help()
            return
        arguments = sys.argv[2:]
        handler = registered_plugins.get(command, None)
        if handler is None:
            self.unknown_command(command)
            return
        try:
            handler.handle_command(*arguments)
        except errors.QuitSilently:
            return
        except errors.AurshError as e:
            err_message = '\n'.join(e.args)
            self.io.error('%s\n%s' % \
                    (type(e).__name__, err_message))
            if configuration.DEBUG:
                self.io.put('')
                traceback.print_tb(sys.exc_info()[2])
                raise e
        except KeyboardInterrupt:
            pass
        except Exception as e:
            _log.exception('Uhandled exception')
            self.io.error('Unhandled error occures.\n'
                    'Traceback was written in %s.log file' % _log.name)

    def print_help(self):
        "Show help message - info about all plugins"
        for (name, plugin) in registered_plugins.iteritems():
            if isinstance(plugin, AliasPlugin):
                continue
            help_msg = format_docstring(plugin, 18)
            self.io.put('%15s - %s' % (name, help_msg))

    def unknown_command(self, command):
        "Show error message"
        self.io.put('Unknown command: %s' % command)
