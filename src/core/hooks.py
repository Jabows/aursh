# -*- coding: utf-8 -*-


import os
import subprocess

from core import logger
from core.conf import configuration

_log = logger.get('hooks')



class Hook(object):
    """Hook scripts wrapper
    """

    def __init__(self, name):
        self.name = name

    def _get_handler(self):
        path = os.path.join(configuration.HOOKS_DIRECTORY, self.name)
        if not os.access(path, os.X_OK):
            _log.debug('hook handler not found %s', path) 
            return None
        return path

    def __call__(self, *args):
        handler = self._get_handler()
        if not handler:
            return None
        cmd = [handler, ]
        cmd.extend(args)
        _log.debug('calling hook: %s', cmd)
        return subprocess.call(cmd)
