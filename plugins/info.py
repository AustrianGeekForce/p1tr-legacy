"""
Displays various information about the bot and its environment. Warning! this
plugin is quite useless. Don't use it unless you think it's cool, you have a
use for it, or you have too much resources.
"""
 
import datetime
import os
import sys
 
from lib.helpers import time_ago_in_words
from lib.plugin import Plugin
 
class InfoPlugin(Plugin):
 
    def __init__(self):
        Plugin.__init__(self, 'info')
        if os.name == 'posix':
            self.operating_system = 'posix'
            self.topics = ('os', 'python', 'resources', 'running_for',
                            'signal_char', 'twisted', 'uptime', 'version')
        elif os.name == 'nt':
            self.operating_system = 'windows nt'
            self.topics = ('os', 'python', 'running_for', 'signal_char',
                            'twisted', 'version')
        else:
            self.topics = ()
        self.launched_at = datetime.datetime.now()
        self._set_summary(_('Displays various information about P1tr and its \
environment'))
        self._add_command(_('info'), '<topic>', _('Specify in topic what \
kind of information you want to see. See help info topics.'))
        self._add_help_topic('topics', _('Available info topics: %s' %
                                                    ', '.join(self.topics)))
 
    def info(self, msg):
        """Calls the appropriate function."""
        if len(msg.params) == 0:
            return _('Available info topics: %s' % ', '.join(self.topics))
        topic = msg.params.split()[0]
        if topic in self.topics:
            if topic in ('signal_char', ):
                # Enter all topics in the tuple above which need msg as an
                # argument.
                return getattr(self, topic)(msg)
            else:
                return getattr(self, topic)()
        else:
            return _('Sorry, I can not give you information about %s.' % topic)
 
    def os(self):
        """
        Returns a piece of information about the operating system P1tr is
        running on.
        """
        if self.operating_system == 'windows nt':
            return 'windows nt'
        else:
            if os.path.exists('/etc/lsb-release'):
                additional_info = self._egrep_first_match('/etc/lsb-release',
                                   'DISTRIB_DESCRIPTION="')[:-1] + ', '
            else:
                additional_info = ''
            output = self._get_output('uname -a').split()
            return additional_info + ' '.join(output[:3])
 
    def python(self):
        """Returns version of used Python version."""
        return _('Python version: ' + sys.version.split()[0])
 
    def resources(self):
        """Returns CPU/RAM usage in % and the amounts of RAM used in MB."""
        output = self._get_output('ps mem -C "python2.5 ./bot.py" -o pcpu,size,pmem')
        # Creates a list with such contents:
        # [('cpu-consumption%', 'mem-cons-in-kB', 'mem-consumption%'), ]
        vals = [(item.split()[0], item.split()[1], item.split()[2])
            for item in output.split('\n')[:-1]  if '.' in item.split()[2]][0]
        # The following is an ugly solution, but it just won't work with
        # string formatting.
        return _('I use %.1f%% of this computer\'s CPU and %.2fMB (%.1f%%) of \
its memory.') % (float(vals[0]), float(vals[1]) / 1024, float(vals[2]))
 
    def running_for(self):
        """
        Returns, how long the last plugin load is ago (normally this equals 
        the P1tr uptime.
        """
        delta = datetime.datetime.now() - self.launched_at
        return _('I am up and running for %s.' % time_ago_in_words(delta))
 
    def signal_char(self, msg):
        """Returns P1tr's signal char."""
        return _('My signal char is "%s".' %
                                msg.bot.factory.connection.signal_char)
 
    def twisted(self):
        """Returns version of the Twisted package P1tr is using."""
        # To save resources, only import when function is called.
        from twisted import __version__
        return _('Twisted version: ' + __version__)
 
    def uptime(self):
        """Returns the system's uptime information."""
        if self.operating_system == 'posix':
            output = self._get_output('uptime').split()
            if not len(output) < 9:
                return ' '.join(output)[:-1]
        elif self.operating_system == 'nt':
            output = self._get_output('net stats server')
            return _('Uptime: ' + output)
 
    def version(self):
        """Returns P1tr version."""
        # This has been hardcoded with reason.
        return '0.1beta'
 
    def _egrep_first_match(self, file, start):
        for line in open(file).readlines():
            if line.startswith(start):
                return line.strip('\n')[len(start):]
