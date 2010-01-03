# -*- coding: utf-8 -*-

import sys

from core.plugin import registered_plugins
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
        handler.handle_command(*arguments)
