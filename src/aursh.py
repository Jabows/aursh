#!/usr/bin/env python
# -*- coding: utf-8 -*-

from core.conf import configuration
from ui.cli import ConsoleInterface
from plugins import import_all_plugins

def main():
    import_all_plugins()
    application = ConsoleInterface(configuration)
    application.run()

if __name__ == '__main__':
    main()
