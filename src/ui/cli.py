# -*- coding: utf-8 -*-

import sys
import traceback

from core.plugin import registered_plugins
from core.conf import configuration
from core import errors


class ConsoleInterface(object):
    def __init__(self, conf):
        self.conf = conf

    def run(self):
        try:
            command = sys.argv[1]
        except IndexError:
            raise errors.BadUsage('TODO - type more')
        arguments = sys.argv[2:]
        handler = registered_plugins.get(command, None)
        if handler is None:
            raise errors.UnknownCommand('TODO - say what?!')
        try:
            handler.handle_command(*arguments)
        except errors.AurshError as e:
            if configuration.DEBUG:
                traceback.print_tb(sys.exc_info()[2])
                raise e
            err_message = '\n'.join(e.args)
            print '%s: %s' % (type(e).__name__, err_message)
        except KeyboardInterrupt:
            pass
