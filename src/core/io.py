# -*- coding: utf-8 -*-


import sys
import tty
import termios

from core.conf import configuration


class IO(object):
    """I/O wrapper"""

    use_colors = configuration.USE_COLORS

    def __init__(self, stdin=None, stdout=None, stderr=None):
        self.stdin = stdin or sys.stdin
        self.stdout = stdout or sys.stdout
        self.stderr = stderr or sys.stderr

    def put(self, message='', newline=True):
        "Print message without formatting"
        self.stdout.write(message.encode('utf-8'))
        if newline:
            self.stdout.write('\n')

    def info(self, message, newline=True):
        prefix = '==>'
        if self.use_colors:
            message = '\033[1;32m%s\033[0m %s' % (prefix, message)
        self.put(message, newline)

    def warning(self, message, newline=True):
        prefix = '==> WARNING:'
        if self.use_colors:
            message = '\033[1;33m%s\033[0m %s' % (prefix, message)
        self.put(message, newline)

    def error(self, message, newline=True):
        prefix = '==> ERROR:'
        if self.use_colors:
            message = '\033[1;31m%s\033[0m %s' % (prefix, message)
        self.put(message, newline)

    def read_char(self, stdin=None):
        "Read single character from stdin"
        stdin = stdin or self.stdin
        fd = stdin.fileno()
        default_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(stdin.fileno())
            gotchar = stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, default_settings)
        return gotchar
