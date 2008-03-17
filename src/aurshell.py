import signal
import shell


def signal_handler(sig, frame):
    pass

if __name__ == '__main__':
    #signal.signal(signal.SIGINT, signal_handler)
    try:
        aursh = shell.Shell()
        aursh.cmdloop()
    except KeyboardInterrupt:
        # TODO [ 23:18 - 15.03.2008 ] 
        # C^c shouldn't quit shell
        pass
    
