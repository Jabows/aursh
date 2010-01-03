# -*- coding: utf-8 -*-

import os
import sys

from core.errors import PluginError


def import_all_plugins():
    "Import every module in current file path"
    modules = []
    plugins_path = os.path.dirname(__file__)
    remove_modules_path = False
    if not plugins_path in sys.path:
        sys.path.append(plugins_path)
        remove_modules_path = True
    for name in os.listdir(plugins_path):
        if name.startswith('_') or not name.endswith('.py'):
            continue
        mod_name, ext = os.path.splitext(name)
        # TODO - catch exception and raise PluginError
        modules.append(__import__(mod_name))
    if remove_modules_path:
        sys.path.remove(plugins_path)
    return modules
