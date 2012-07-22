"""
Plug-in to display a random fortune, if you want from one of the specific
fortune topics.
"""

import os.path
import subprocess

from lib.plugin import Plugin
from lib.logger import log

class UnixPlugin(Plugin):
    
    def __init__(self):
        
        Plugin.__init__(self, 'unix')
        self._set_summary(_('Plugin to access some popular UNIX applications'))
        self._add_command('fortune', '[<type>]', _('displays a random \
fortune. See "help fortune types".'))
        self._add_command('ddate', None, _('displays the current date in the \
the discordian calendar.'))
        self._add_help_topic('fortune_types', _('Available fortune types: \
fortunes, literature, riddles; default: all.'))
        
        self.wtf_path = '/usr/share/games/bsdgames/'
        self.wtf_parseable = True
        wtf_enabled = True
        
        if not os.path.isfile(os.path.join(self.wtf_path, 'acronyms')):
            self.wtf_parseable = False
            if self._get_output('wtf', False, False):
                log('i', 'Falling back to system\'s wtf.')
            else:
                wtf_enabled = False
                log('w', 'Couldn\'t find wtf installation; command disabled.')
        
        if wtf_enabled:
            self._add_command('wtf', '<acronym> [<type>]', 'tells you what \
<acronym> means.')
    
    def fortune(self, msg):
        
        for type in ['fortunes', 'literature', 'riddles']:
            if msg.params == type:
                mode = type
            else:
                mode = ''
        fortune = self._get_output('fortune -s %s ' % mode)
        if fortune == '':
            return _('I predict you will install fortune to make this ' +
                     'plug-in work.')
        else:
            # The following line replaces \t and \n with space
            fortune = ' '.join(' '.join(fortune.split('\t')).split('\n'))
            return fortune
    
    def wtf(self, msg):
        
        params = msg.params.split()
        
        if params and self.wtf_parseable:
            return self._get_wtf(params, msg.user.name)
        elif params:
            command = 'wtf ' + params[0]
            if len(params) > 1:
                command += ' -t ' + params[1]
            return self._get_stdout(command).strip('\n')
    
    def _get_wtf(self, params, username):
        
        file = os.path.join(self.wtf_path, 'acronyms')
        
        if len(params) > 1:
            file += '.' + params[1]
            if not os.path.isfile(file):
                return username + ': ' + _('Sorry, this type does not exist.')
        
        for line in open(file).xreadlines():
            if line.startswith(params[0].upper() + '\t'):
                return line.replace('\t', ': ').strip('\n')
        
        return username + ': ' + _('Sorry, I don\'t know what that means.')
    
    def ddate(self, msg):
        try:
            return '. '.join(self._get_output('ddate').split('\n'))
        except:
            msg.bot.msg(msg.reply_to, _('There seems to be something wrong with %s. See my \
logfiles for more information.' % 'ddate'))
            raise
