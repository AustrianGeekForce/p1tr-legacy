"""
Logger Plug-In, responsible for keeping record of all things appearing in a
channel.
"""

from lib.plugin import Plugin
from lib.logger import Log

class LoggerPlugin(Plugin):
    
    def __init__(self):
        Plugin.__init__(self, 'logger')
        self._set_summary(_('Logging plugin; not intended to interact.'))
        self._add_command('quote')
    
    def _listen_(self, msg):
        try:
            msg.bot.logs[msg.chan.lower()].write('<%s> %s' %
                        (msg.user.name, msg.msg))
        except KeyError:
            # If it produces a key error it means that it comes from a source
            # which has no logfile.
            pass
    
    def user_joined(self, bot, user, chan):
        bot.logs[chan.lower()].write('@ %s joined channel %s' % (user, chan))
        print 'someone joined %s, it is %s' % (chan, user)
    
    def user_kicked(self, bot, chan, kickee, kicker, message):
        bot.logs[chan.lower()].write('@ %s has been kicked from %s by %s (%s)' % 
                                            (kickee, chan, kicker, message))
    
    def user_action(self, bot, user, chan, data):
        bot.logs[chan.lower()].write('* %s %s' % (user.split('!')[0], data))
    
    def topic_updated(self, bot, user, chan, data):
        bot.logs[chan.lower()].write('@ %s set topic "%s"' % (user.split('!')[0], data))
    
    def user_renamed(self, bot, oldname, newname):
        #I commented this out cause it raised an exception
        #chan is not defined in here
        #m-otteneder
        #bot.logs[chan.lower()].write('@ %s is now known as %s' % (oldname, newname))
        pass
    
    def user_quit(self, bot, user, quitmsg):
        for log in bot.logs:
            log.write('@ Quit: %s: %s' % (user, quitmsg))
    
    def user_part(self, bot, user, chan, reason=None):
        bot.logs[chan.lower()].write('@ %s left %s (%s)' % (user, chan, reason))
    
    def mode_changed(self, bot, user, chan, set, modes, args):
        if set:
            set = '+'
        else:
            set = '-'
        # Fallback if args is an empty tuple
        if len(args) < 1:
            args = ('None')
        if chan == bot.nickname:
            pass
        else:
            bot.logs[chan.lower()].write('@ Mode %s %s by %s' % (set + modes,
                                    args[0].split('!')[0], user.split('!')[0]))
        
    
    def bot_kicked(self, bot, chan, kicker, message):
        bot.logs[chan.lower()].write('@ %s has been kicked from %s by %s (%s)' % 
                                        (bot.nickname, chan, kicker, message))
    
    def bot_joined(self, bot, chan):
        bot.logs[chan.lower()] = Log(bot.factory.connection.server, chan)
        bot.logs[chan.lower()].write('@ Joined channel ' + chan)
    
    def bot_part(self, bot, chan, reason):
        bot.logs[chan.lower()].write('@ Left channel %s (%s)' % (chan, reason))
        bot.logs[chan.lower()].close()
        del bot.logs[chan.lower()]
