"""I contain evreything concerning P1tr's IRC channel logging."""

import os
import sys
from time import strftime

class Log:
    """
    I'm a log file. You can write to me and close me. Me and my brothers
    get created at join.
    """
    def __init__(self, server, channel):
        self.channel = channel
        self.server = server
        self.filename = '%s_%s.log' % (self.server, self.channel)
        self.logfile = open(os.path.join('log', self.filename), 'a')
    
    def write(self, line):
        """Give me a line! I'll write it straight down, together with a nice
        timestamp."""
        self.logfile.write('[%s] %s\n' % (strftime('%Y/%m/%d %H:%M:%S'),
                                        line))
        self.logfile.flush()
    
    def close(self):
        """I'm close() and my boring job is to close log files."""
        self.logfile.close()
    
class ErrorLog:
    """
    Error log for collecting information about problems which occur while
    running P1tr. level specifies the lowest kind of error which is shown
    inside the console and must be one of those: n, f, e, w, i, where n stands
    for nothing and i for everything.
    Default loglevel is f.
    """
    def __init__(self, level='f'):
        self.kinds = ['i', 'w', 'e', 'f', 'n']
        if level in self.kinds:
            self.level = level
        else:
            print 'Invalid level.'
            self.level = 'f'
        self.logfile = open(os.path.join('log', 'error.log'), 'a')
    
    def write(self, error, message=None):
        if len(error) > 1 and message is None:
            sys.stdout.write(error)
            self.logfile.write(error)
        else:
            if not error in self.kinds[:-1]:
                error = 'i'
            err_str = ['INFO', 'WARNING', 'ERROR', 'FATAL', 'NOTHING']
            line = '[%s] %s: %s\n' % (strftime('%H:%M:%S'),
                                      err_str[self.kinds.index(error)], message)
            if self.kinds.index(error) >= self.kinds.index(self.level):
                sys.stdout.write(line)
            if error in self.kinds[:-1]:
                self.logfile.write(line)
                self.logfile.flush()

def log(error, message):
    """
    Write arguments to sys.stderr, which has been overridden by an ErrorLog
    object. If not it is done here.
    """
    try:
        sys.stderr.write(error, message)
    except TypeError:
        sys.stderr = ErrorLog('i')
        sys.stderr.write(error, message)
