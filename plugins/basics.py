"""Plug-in for basic IRC operations."""

import sys
import os
from sets import Set
from twisted.internet import reactor

from lib.plugin import Plugin
from lib.core import User
from lib.logger import log
from lib.helpers import load_language
from lib.plugins import PluginLoader, PluginHandler

class BasicsPlugin(Plugin):
    
    def __init__(self):
        Plugin.__init__(self, 'basics')
        self._set_summary(_('Plugin for basic IRC operations'))
        self._add_command('join', '<channel>', _('makes P1tr join channel'))
        self._add_command('part', '[<channel>]', _('makes P1tr part channel. \
If channel is not given he parts the current one.'))
        self._add_command('quit', None, _('shuts P1tr down.'))
        self._add_command('mode', '<mode> [<nick|mask>]', _('sets channel \
modes to mode; add nick or mask if required for the particular mode.'))
        self._add_command('opme', None, _('gives you op if P1tr is able to \
and you have the appropriate level'))
        self._add_command('lang', '<code>', _('set P1tr\'s language to code. \
Example: lang ca'))
        self._add_command('reload', None, _('reloads all plugins.'))
        self._add_command('restart', None, _('restarts the bot.'))
        self._add_command('ping', None, 'says pong.')
        self._add_command('say', '<channel> <message>', _('lets the bot say \
<message> in <channel>'))
        self._add_command('action', '<channel> <something>', _('lets the bot do \
<something> in <channel>'))
        self._add_command('nick', '<nickname>', _('changes P1tr\'s nick to \
nickname.'))
    
    def join(self, msg):
        level = 29
        if self.require_level(msg.user, level):
            log('i', '%s ordered to join %s.' % (msg.user.name, msg.params))
            msg.bot.join(msg.params)
        else:
            return _('Unauthorized. Level %s required.' % level)
    
    def part(self, msg):
        level = 29
        if self.require_level(msg.user, level):
            if msg.params:
                msg.bot.part(msg.params)
            else:
                msg.bot.part(msg.chan)
        else:
            return _('Unauthorized. Level %s required.' % level)
    
    def quit(self, msg):
        level = 30
        if self.require_level(msg.user, level):
            log('i', 'Shutdown initiated by %s' % msg.user.name)
            User.users.close()
            reactor.stop()
        else:
            return _('Unauthorized. Level %s required.' % level)
    
    def mode(self, msg):
        level = 29
        if self.require_level(msg.user, level):
            params = msg.params.split(' ')
            nick = None
            mask = None
            if len(params) == 2:
                if params[1].find('!') != -1:
                    nick = params[1]
                else:
                    mask = params[1]
            if params[1][0] == '+':
                set = True
            else:
                set = False
            try:
                msg.bot.mode(msg.chan,  set, params[0], None, nick, mask)
            except:
                return _('ERROR: Check your mode syntax and if the bot has \
sufficient rights.')
        else:
            return _('Unauthorized. Level %s required.' % level)
    
    def opme(self, msg):
        """
        This is a convenience function which does what mode +o username 
        does as well.
        """
        level = 20
        if self.require_level(msg.user, level):
            msg.bot.mode(msg.chan, set, 'o', None, msg.user.name,
                         msg.user.hostmask)
            return _('Your wish is my command, master %s' % msg.user.name)
        else:
            return _('You are too minion to get op.')
    
    def lang(self, msg):
        """Resets language, if invoker is authorized."""
        level = 29
        if self.require_level(msg.user, level) and msg.params.split(' '):
            try:
                load_language(msg.params.split(' ')[0])
                return _('Language set to %s' % msg.params)
            except KeyError:
                return _('Invalid language code.')
        else:
            return _('Unauthorized. Level %s required.' % level)
    
    def reload(self, msg):
        """Reloads all plugins for this connection."""
        level = 29
        if self.require_level(msg.user, level):
            log('i', '%s initiated plugin reload...' % msg.user.name)
            msg.bot.msg(msg.reply_to, _('Reloading plugins...'))
            plugs = PluginLoader().load_plugins()
            handler = PluginHandler(plugs)
            del msg.bot.plugins
            msg.bot.plugins = Set(handler.plugins.values())
            del msg.bot.factory.plugin_handler
            msg.bot.factory.plugin_handler = handler
            return _('Done.')
        else:
            return _('Unauthorized. Level %s required.' % level)
    
    def restart(self, msg):
        """Stops and restarts the bot."""
        level = 29
        if self.require_level(msg.user, level):
            msg.bot.msg(msg.reply_to, _('Restarting...'))
            log('w', 'Restart requested by %s.' % msg.user.name)
            reactor.stop()
            os.execl('./bot.py', *sys.argv)
        else:
            return _('Unauthorized. Level %s required.' % level)
    
    def ping(self, msg):
        return msg.prefix + 'Pong!'
    
    def _say_or_action(self, msg):
        if msg.chan != msg.bot.nickname:
            msg.bot.msg(msg.reply_to, msg.prefix + _('Tell me this in a query.'))
            return False
        if not self.require_level(msg.user, 15):
            msg.bot.msg(msg.reply_to, _('Unauthorized. Level %s required.' % 15))
            return False
        params = msg.params.strip()
        args = [x for x in params.split() if x]
        if len(args) < 2:
            return _('Not enough arguments provided.')
        if not args[0].startswith('#') and not self.require_level(msg.user, 20):
            return 'Annoying people is not a good idea.'
        return (args[0], params[params.find(' ')+1:])
    
    def say(self, msg):
        vars = self._say_or_action(msg)
        if vars:
        	msg.bot.msg(vars[0], vars[1])
    
    def action(self, msg):
        vars = self._say_or_action(msg)
        if vars:
        	msg.bot.me(vars[0], vars[1])

    def nick(self, msg):
        level = 25
        if self.require_level(msg.user, level):
            nick = msg.params.split()
            if len(nick) > 0:
                msg.bot.setNick(nick[0])
            else:
                return _('You forgot to tell me my new nickname.')
        else:
            return _('Unauthorized. Level %s required.' % level)
    
    def bot_kicked(self, bot, chan, kicker, message):
        bot.join(chan)
        bot.msg(chan, kicker + _(': I\'m going to kill you!'))
