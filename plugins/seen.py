"""Keeps track of the most recent appearance of the user."""

import datetime

from lib.plugin import Plugin
from lib.core import User
from lib.logger import log
from lib.helpers import time_ago_in_words


class SeenPlugin(Plugin):
    """
    I'm having an eye on all chatters. You can ask me for 
    the last time I saw someone doing something.
    """
    
    now = datetime.datetime.now
    
    def __init__(self):
        Plugin.__init__(self, 'seen')
        self._set_summary( _('Just use "seen user" to get information about \
user\'s last action'))
        self._add_command('seen')
                                 
    def seen(self, msg):
        params = msg.params.split()
        log('i', "You wanted to see:" + params[0])
        if len(params) != 1:
            msg.bot.msg(msg.reply_to, _("Usage: seen user"))
        else:
            try:
                if msg.user.name == params[0]:
                    return _(params[0] + \
                                    _(":Huh? You dont see yourself? WTF!?"))
                else:
                    return last_seen(params[0])
            except(KeyError, NameError):
                raise
                return _("Gee...I've never seen " + params[0])
        
    def _listen_(self, msg):
        record_action(msg.user.name, Action(_("saying"), msg.msg))
    
    def user_joined(self, bot, user, chan):
        record_action(user, Action(_("joining"), chan))

    def user_kicked(self, bot, chan, kickee, kicker, message):
        record_action(kickee, Action(_("getting kicked from"), chan))
        
    def user_action(self, bot, user, chan, data):
        record_action(user, Action(_("doing"), data))
        
    def topic_updated(self, bot, user, chan, data):
        record_action(user, Action(_("updating the topic"), data))

    def user_renamed(self, bot, oldname, newname):
        string = _("changing his name from  %s to %s"  % (oldname, newname))
        record_action(newname, Action(string, None))
    
    def user_quit(self, bot, user, quitmsg):
        record_action(user, Action(_("quitting"), quitmsg))

def record_action(user_name, action):
    try:
        User.users[user_name].last_action = action
    except(KeyError, NameError):
        return None

def last_seen(name):
    try:
        user = User.users[name]
        delta = SeenPlugin.now() - user.last_action.time
        return _("%s was last seen: %s ago, %s" % \
                 (user.name, time_ago_in_words(delta), user.last_action))
        #return user.last_action.time
    except KeyError:
        return _("Gee... I've never seen " + name)
        log('i', "Information about unknown User requested")
        raise
    except NameError:
        log('i', "User has no action defined yet")
        raise
                
                
class Action:
    """I contain the information about a users last action."""
    
    def __init__(self, action, msg):
        self.action = action
        self.msg = msg
        self.time = SeenPlugin.now()
    
    def __str__(self):
        return self.action + ":" + self.msg
        