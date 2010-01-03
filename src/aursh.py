#!/usr/bin/env python
# -*- coding: utf-8 -*-

from core.conf import configuration
from ui.cli import ConsoleInterface
from plugins import import_all_plugins
from core.plugin import load_plugin_commands_aliases

def main():
    import_all_plugins()
    load_plugin_commands_aliases()
    application = ConsoleInterface(configuration)
    application.run()

if __name__ == '__main__':
    main()
