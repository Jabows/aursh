# -*- coding: utf-8 -*-


import sys



class IO(object):
    """I/O wrapper"""

    def __init__(self, stdin=None, stdout=None, stderr=None):
        self.stdin = stdin or sys.stdin
        self.stdout = stdout or sys.stdout
        self.stderr = stderr or sys.stderr

    def put(self, message, newline=True):
        "Print message without formatting"
        self.stdout.write(message.encode('utf-8'))
        if newline:
            self.stdout.write('\n')

    def info(self, message, newline=True):
        pass

    def warning(self, message, newline=True):
        pass

    def error(self, message, newline=True):
        pass

    def read_char(self):
        pass
