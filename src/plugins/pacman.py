import os


class Plugin_pacman(object):
    """Pipe to pacman"""
    def __init__(self, io, conf):
        self.io = io
        self.conf = conf
        self.pacman_cmd = "pacman"

    def __call__(self, *args):
        """Pipe to pacman"""
        os.system("%s %s" % (self.pacman_cmd, " ".join(args)))
