# -*- coding: utf-8 -*-


import os

from core import errors
from core.plugin import Plugin
from core.conf import configuration


class DisallowRoot(Plugin):
    """Simple plugin to forbidden using aursh under root account"""

    def __init__(self):
        try:
            forbid_root = configuration.FORBID_ROOT
        except errors.UnknownSetting:
            forbid_root = True
        if os.getuid() == 0 and forbid_root:
            raise errors.Forbidden(
                    'Running aursh using root account is forbidden')

