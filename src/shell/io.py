import sys
import colorize

class InOut(object):
    def __init__(self, stdout=None, stdin=None):
        """Set Input and Output"""
        if not stdout:
            self.stdout = sys.stdout
        else:
            self.stdout = stdout
        if not stdin:
            self.stdin = sys.stdin
        else:
            self.stdin = stdin
        self.colorize = colorize.Colorize()

    def put(self, message, newline=True):
        """Write to output"""
        msg_out = message
        # colorize only stdout
        msg_out = self.colorize(message)
        if newline:
            msg_out = msg_out + " \n"
        self.stdout.write(msg_out)

    def get(self, message=None, newline=False):
        """Read from input"""
        if message:
            self.put(message, newline)
        return self.stdin.readline()

    def ask(self, question, good='y', bad='n', newline=False):
        """Ask question and return True or False"""
        answer = '[#{BOLD}%s#{none}/%s]' % (good.capitalize(), bad.lower())
        q = "%s %s " % (question, answer)
        self.put(q, newline)
        a = self.stdin.readline().strip()
        a = a.lower()
        if a == good.lower():
            return True
        elif a == bad.lower():
            return False
        elif not a:
            self.put("Type #{BOLD}%s#{NONE} or #{BOLD}%s#{NONE}" % \
                    (good, bad))
            return self.ask(question, good, bad, newline)

