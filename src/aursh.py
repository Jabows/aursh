#!/usr/bin/env python
# -*- coding: utf-8 -*-

from core.conf import Configuration
from ui.cli import ConsoleInterface
from plugins import import_all_plugins

def main():
    import_all_plugins()
    conf = Configuration()
    application = ConsoleInterface(conf)
    application.run()

if __name__ == '__main__':
    main()
