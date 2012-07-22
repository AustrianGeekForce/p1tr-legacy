"""
Calculates at keeps track of how nice a user is to his bot and his
surroundings.
"""

import hashlib
from math import sqrt
from random import randint
from time import time

from lib.plugin import Plugin

class SympathyPlugin(Plugin):
    
    
    def __init__(self):
        Plugin.__init__(self, 'sympathy')
        self._set_summary(_('Calculates P1tr\'s sympathy towards a user'))
        self._add_command('sympathy', '[<nick>]', _('Shows sympathy statistics \
towards the indicated nick (or towards you, if no nick is indicated).'))
        self._add_command('snack', None, _('Gives your bot a well deserved \
snack.'))
        self._add_command('dispraise', None, _('Use only if bot was bad to \
you.'))
        self._add_command('hi', None, _('Greet P1tr.'))
        self.mind = self._load_resource('mind')
        # Structure of self.mind dictionary:
        # {'server': {
        #     'nick': {
        #         'calls': {'callers_nick': float, },
        #         'sympathy': float,
        #         'actions': int, }, 
        #     '_known_channels: [],
        #     '_vips': [], },
        # }
        self.badwords = (_('sucker'), _('asshole'), _('idiot'), _('scum'))
    
    def sympathy(self, msg):
        """Displays the most important sympathy data of a user."""
        server = msg.bot.factory.connection.server
        if msg.params:
            user = msg.params.split()[0]
        else:
            user = msg.user.name
        if not server in self.mind.keys():
            self.mind[server] = {'_known_channels': [], '_vips': [], }
        if user in self.mind[server].keys():
            return _('Sympathy for %s: %.2f' % (user,
                self.mind[server][user]['sympathy']))
        else:
            self._influence(msg.user, server, 2)
            if user == msg.user.name:
                text = _('I have ignored you so far.')
            else:
            	text = _('I have ignored %s so far.' % user)
            return msg.prefix + text
    
    def snack(self, msg):
        """Increases P1tr's sympathy against snack-giver. """
        server = msg.bot.factory.connection.server
        if self._influence(msg.user, server, 1):
            return _('Thank you, %s :)' % msg.user.name)
        else:
            return msg.prefix + _('That didn\'t really taste good...')
    
    def dispraise(self, msg):
        """Decrease P1tr's sympathy against dispraise-giver."""
        self._influence(msg.user, msg.bot.factory.connection.server, -1)
        return msg.prefix + _('Probably you\'re right, %s *grml*' % msg.user.name)
    
    def hi(self, msg):
        """When invoked, sympathy of invoker is influenced."""
        server = msg.bot.factory.connection.server
        params = msg.params.split()
        if len(params) > 1 and msg.params.split()[0] in self.badwords:
            self._influence(msg.user, server, -2)
        else:
            self._influence(msg.user, server, 0.5)
            return _('Hi, %s :)' % msg.user.name)
    
    def user_joined(self, bot, user, chan):
        """Greets a user when coming in and if he is VIP."""
        if bot.factory.connection.server in self.mind and \
        user in self.mind[bot.factory.connection.server]['_vips']:
            bot.msg(chan, _('Hi, %s :)' % user))
    
    def _listen_(self, msg):
        """
        Listens for certain events which influence sympathy + reaction on
        certain events like return from afk.
        """
        message = msg.msg.split()
        server = msg.bot.factory.connection.server
        nick = msg.user.name
        if (message[0] == 're' and
            self.mind[server][nick]['sympathy'] > 10):
            return _('Welcome back, %s.' % nick)
        elif (message[0] == 'brb' and
            self.mind[server][nick]['sympathy'] < -10):
            return _('Hopefully not.')
        elif message == 'wb, ' + msg.bot.nickname:
            self._influence(msg.user, server, 1.2)
            return _('Thank you, %s ;)' % msg.user.name)
        # Spam protection: reset every hour
        if not time() % 3600:
            for server in self.mind:
                for nick in self.mind[server]:
                    self.mind[server][nick]['actions'] = 0
            self.sync()
    
    def _influence(self, user, server, factor):
        """
        Modifies P1tr's sympathy for user by a value calculated with the help
        of factor. First argument has to be an object of the User class
        (e.g. msg.user).
        """
        if not server in self.mind.keys():
            self.mind[server] = {'_known_channels': [], '_vips': [], }
        if not user.name in self.mind[server].keys():
            self.mind[server][user.name] = {'calls': {},
                                    'sympathy': self._prejudice(user),
                                    'actions': 0, }
        
        # Spam protection: if user has done more actions than 8 in the last
        # hour actions don't count until reset, which happens every hour.
        if not self.mind[server][user.name]['actions'] > 8:
            sign = 1
            if factor < 0:
                factor = factor * -1
                sign = -1
            modification = (sqrt(randint(1, 20) * 0.5 * factor) - 1.49) * sign
            self.mind[server][user.name]['sympathy'] = \
                    self.mind[server][user.name]['sympathy'] + modification
            sympathy = self.mind[server][user.name]['sympathy']
            
            if sympathy >= 42 and not user in self.mind[server]['_vips']:
                self.mind[server]['_vips'].append(user)
            elif sympathy < 42 and user.name in self.mind[server]['_vips']:
                del self.mind[server]['_vips']
            
            # Spam protection: Increase action count
            self.mind[server][user.name]['actions'] += 1
            
            self.mind.sync()
            
            if modification >= 0:
                return True
            else:
                return False
        else:
            return False
    
    def _prejudice(self, user):
        """
        Calculates the prejudice P1tr has against a user, using his nick and
        his hostmask. First argument has to be an object of the User class
        (e.g. msg.user).
        """
        usermod = int(hashlib.md5(user.name).hexdigest(), 16)
        maskmod = int(hashlib.md5(user.hostmask).hexdigest(), 16)
        if usermod >= maskmod:
            sign = 1
        else:
            sign = -1
        return sign * (usermod + maskmod)/(20e37)
