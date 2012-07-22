"""
I take memos from users for other users and deliver them as soon as the
recipient shows up somewhere I am too.
"""

import datetime
import lib.core
from lib.helpers import time_ago_in_words
from lib.plugin import Plugin

class MemoPlugin(Plugin):
    
    def __init__(self):
        Plugin.__init__(self, 'memo')
        self._set_summary(_('Saves and delivers memos to a given user'))
        self._add_command('memo', '<recipient> <message>', _('Delivers \
message to recipient as soon as he shows up somewhere I am (join or \
new private message)'))
        self._add_command('burn_memos', '<recipient>', _('Clear all memos \
from storage. If recipient is given, only memos to him are being \
deleted.'))
        self.mailbag = self._load_resource('mailbag')
        # self.mailbag dictionary structure:
        # {'recipient': [('sender', 'send_time', 'message'), ], }
    
    def _listen_(self, msg):
        """Watch if a user, who has notes, says something."""
        self._print_memos_if_exist(msg.user.name, msg.chan, msg.bot)
    
    def user_joined(self, bot, user, chan):
        """Watch if a user, who has notes, joins the channel."""
        self._print_memos_if_exist(user, chan, bot)
    
    def _print_memos_if_exist(self, user, chan, bot):
        """
        Takes IRCBot instance and user name (string), and writes all available
        notes for the user to the channel, if they exist.
        """
        luser = user.lower()
        if luser in self.mailbag.keys():
            for memo in self.mailbag[luser]:
                delta = datetime.datetime.now() - memo[1]
                bot.msg(chan, _('%s: %s left a memo for you %s ago: %s' %
                        (user, memo[0], time_ago_in_words(delta), memo[2])))
                # Delete the memo after showing it.
                index = self.mailbag[luser].index(memo)
                del self.mailbag[luser][index]
            # When no memos left, delete entire entry for user
            if not self.mailbag[luser]:
                del self.mailbag[luser]
            self.mailbag.sync()
    
    def memo(self, msg):
        """Saves a memo. You can't send memos to yourself or the bot."""
        params = msg.params.split()
        if len(params) > 1:
            recipient = params[0].lower()
            if recipient == msg.user.name.lower():
                return _('Stupid kid, sending yourself a memo...')
            elif recipient == msg.bot.nickname.lower():
                return _('I need no memos, I am perfect.')
            else:
                tuple = (msg.user.name, datetime.datetime.now(),
                          ' '.join(params[1:]))
                try:
                    self.mailbag[recipient].append(tuple)
                except (KeyError, AttributeError):
                    self.mailbag[recipient] = [tuple, ]
                self.mailbag.sync()
                return _('Am delieverink.')
        else:
            return _('It seems you forgot something, did you?')
    
    def burn_memos(self, msg):
        """Deletes all memos or the memos of a given recipient only."""
        level = 15
        if self.require_level(msg.user, level):
            if msg.params.lower() in self.mailbag.keys():
                self.mailbag[msg.params.lower()] = []
            else:
                self.mailbag.clear()
            self.mailbag.sync()
            return _('How evil... Memos have been burnt.')
        else:
            return _('Learn how to use matches and come back.')
