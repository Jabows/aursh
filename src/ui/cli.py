# -*- coding: utf-8 -*-

import sys
import traceback

from core.plugin import registered_plugins
from core.conf import configuration
from core import errors
from core.io import IO

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
        except errors.AurshError as e:
            err_message = '\n'.join(e.args)
            self.io.error('%s\n%s' % \
                    (type(e).__name__, err_message))
            if configuration.DEBUG:
                traceback.print_tb(sys.exc_info()[2])
                raise e
        except KeyboardInterrupt:
            pass

    def print_help(self):
        self.io.put('TODO')

    def unknown_command(self, command):
        self.io.put('Unknown command: %s' % command)
