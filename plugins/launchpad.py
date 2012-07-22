"""
Plugin that provides some Launchpad related features which are useful
for developers who use that platform to manage their project(s).

If you don't want the plugin to parse all messages searching for "LP #nnn",
write the following line into your configuration file (in section "global).
To enable or disable this with temporary effect, on the run, use the lp_listen
command.

  X-Launchpad-Passive = True

In the case you want it to parse messages, but additionally you want it to
recognize "bug #nnn" (without "LP") as a bug number, write the following
line into your configuration file (in section "global"), instead:

  X-Launchpad-Exclusive = True

"""

import re
import time
import urllib2

from lib.plugin import Plugin
from lib.logger import log
from lib.config import configuration, xdata_bool, Storage

class LaunchpadPlugin(Plugin):
    
    def __init__(self):
        
        Plugin.__init__(self, 'launchpad')
        self._set_summary(_('Plugin that provides some Launchpad related \
features'))
        self._add_command('lp', '<bug number>', _('displays information about \
the given bug.'))
        self._add_command('lp_listen', None, _('active/deactivate listening \
for Launchpad bugs.'))
        
        if xdata_bool(configuration, self.name, 'exclusive'):
            bugrule_str = r'\b(?:[bB][uU][gG]|[lL][pP]):?\s+?#?([0-9]+)\b'
        else:
            bugrule_str = r'\b(?:[lL][pP]):?\s+(?:[bB][uU][gG]\s+)?#?([0-9]+)\b'
        self.bugrule = re.compile(bugrule_str)
        self.bugurlrule = re.compile(r'\bhttps?://(?:bugs.)?(?:edge.)?' +\
            r'launchpad.net/[a-zA-Z0-9\-+~/]+/([0-9]+)\b')
        
        if xdata_bool(configuration, self.name, 'passive'):
            self._listen = False
        else:
            self._listen = True
        
        # Loop protection
        # Format: {'channel_name': [(timestamp, bugid), (timestamp, bugid)]}
        self._lastbugs = {}
    
    def lp(self, msg):
        
        words = [word.replace(',', '') for word in msg.params.split()
            if word.replace(',', '').isdigit()]
        bugstr = ', '.join(['LP %d' % int(bug) for bug in words])
        self._bug_info(msg, bugstr, msg.reply_to)
    
    def lp_listen(self, msg):
        
        if not self.require_level(msg.user, 15):
            return msg.prefix + _('Who are you to give me orders?')
        
        if self._listen:
            self._listen = False
            return msg.prefix + _('I won\'t annoy you with \
unwanted bug information, promised.')
        else:
            self._listen = True
            return msg.prefix + _('Okay, I\'m listening ;).')
    
    def _listen_(self, msg):
        if self._listen and msg.user.name != msg.bot.nickname and \
        msg.keyword != 'lp':
            self._bug_info(msg.bot, msg.msg, msg.reply_to)
            self._bug_url_info(msg.bot, msg.msg, msg.reply_to)
    
    def user_action(self, bot, user, channel, data):
        if self._listen:
            if channel == bot.nickname:
                channel = user.split('!')[0]
            self._bug_info(bot, data, channel)
            self._bug_url_info(bot, data, channel)
    
    def _get_bug_info(self, bugnumber, bot, channel, quiet=False):
        """Retrieves information about a bug and returns the bug object.
        If the bug doesn't exist, an error message is send."""
        
        try:
            bugtext = urllib2.urlopen('https://launchpad.net/bugs/%d/+text' % \
                bugnumber).readlines()
        except urllib2.HTTPError:
            if not quiet:
                bot.msg(channel, _('Bug #%d doesn\'t exist.') % bugnumber)
            return None
        else:
            data = Storage()
            values = ('title', 'task', 'status', 'importance')
            for line in bugtext:
                for value in values:
                    if line.startswith(value) and not hasattr(data, value):
                        setattr(data, value, line.split(':', 1)[-1].strip())
            if len(data) != len(values):
                if not quiet:
                    bot.msg(channel, _('Bug #%d is private.') % bugnumber)
                return None
            return _('Launchpad bug #%d in %s: "%s" (%s, %s).') % \
                (bugnumber, data.task, data.title, data.status, data.importance)
    
    def _is_duplicated(self, channel, bugnumber):
        if not channel in self._lastbugs:
            self._lastbugs[channel] = {}
        lim = time.time() - 120 # only repeat bug information every two minutes
                                # the main reason for this is to avoid madness
                                # when two bots are in the channel
        if bugnumber not in self._lastbugs[channel] or \
        self._lastbugs[channel][bugnumber] < lim:
            self._lastbugs[channel][bugnumber] = time.time()
            return False
        return True
    
    def _bug_info(self, bot, string, channel):
        """Parses a line looking for bug numbers, and sends information about
        them."""
        for bugnumber in set(self.bugrule.findall(string)):
            direct_request = string.lower().startswith(bot.nickname.lower()) \
                and string[len(bot.nickname):][0] in (' ', ',', ':')
            if self._is_duplicated(channel, bugnumber) and not direct_request:
                continue
            bug = self._get_bug_info(int(bugnumber), bot, channel)
            if bug:
                bot.msg(channel, bug + ' https://launchpad.net/bugs/%d' % \
                    int(bugnumber))
    
    def _bug_url_info(self, bot, data, channel):
        """Parses a line looking for bug URLs, and sends information about
        them."""
        for bugnumber in set(self.bugurlrule.findall(data)):
            if not 'bugs' in data:
                continue
            if self._is_duplicated(channel, bugnumber):
                continue
            bug = self._get_bug_info(int(bugnumber), bot, channel)
            if bug:
                bot.msg(channel, bug)
