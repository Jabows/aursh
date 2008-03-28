import signal
import sys
import os

from shell import shell
import conf

def signal_handler(sig, frame):
    pass

if __name__ == '__main__':
    #signal.signal(signal.SIGINT, signal_handler)
    try:
        aursh = shell.Shell(conf)
        aursh.cmdloop()
    except KeyboardInterrupt:
        # TODO [ 23:18 - 15.03.2008 ] 
        # C^c shouldn't quit shell
        pass
    
