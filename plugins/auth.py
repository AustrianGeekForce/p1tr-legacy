"""Authentication plug-in for rights management."""

from lib.plugin import Plugin
from lib.core import User
from lib.logger import log
from lib.config import configuration

class AuthPlugin(Plugin):
    
    def __init__(self):
        Plugin.__init__(self, 'auth')
        self._set_summary(_('Authentification plugin'))
        self._add_command('auth', '<password>', _('Show that you are you by \
using your password from registration. Better do this using private \
adressing.'))
        self._add_command('register', '<password>', _('Registers your nick \
with password. Better do this using private adressing.'))
        self._add_command('set', '<user> <level>', _('Changes user\'s level \
to the indicated one, which can be an integer from 1 to 29.'))
        self._add_command('level', '[<user>]', _('Shows user\'s level, or \
yours if you specify no username.'))
        for user in User.users.values():
            user.trusted = False
    
    def _private_only(self, msg):
        """Complains to the user and returns True if the given message
        was send in a query."""
        if msg.chan != msg.bot.nickname:
            msg.bot.msg(msg.reply_to,
                msg.prefix + _('Please, tell me this in a private query.'))
            return True
        else:
            return False
    
    def auth(self, msg):
        """
        If a user uses auth with the correct password he can use all
        possibilities of the level associated with his account.
        """
        if self._private_only(msg):
            return False
        log('i', 'User attempting to authenticate: ' + str(msg.user))
        if msg.params == msg.user.password:
            msg.user.trusted = True
            return msg.prefix + _("You're authenticated by now.")
        else:
            return msg.prefix + _("Passwords do NOT match. DO NOT TRY TO FOOL ME!")
    
    def register(self, msg):
        """
        Enables a user to authenticate and therefore reach higher levels by
        assigning a password of his choice to his user object.
        """
        if self._private_only(msg):
            return False
        log('i', 'User tries to register: ' + str(msg.user))
        if msg.user.password is not None:
            return msg.prefix + _('Sorry! Your nick is already registered.')
        elif not msg.params:
            return msg.prefix + _('You have to specify a password.')
        else:
            msg.user.password = msg.params
            log('i', 'User %s registered with password %s.' % (msg.user.name,
                msg.user.password))
            if msg.user.name.lower() == configuration.superadmin:
                msg.user.level = 30
            else:
                msg.user.level = 0
            msg.user.trusted = True
            User.users.sync()
            return msg.prefix + _('Your nick has been successfully registered!')
    
    def set(self, msg):
        """Sets level of a user to a certain value."""
        token = msg.params.split()
        if len(token) == 2:
            level = int(token[1])
            allowed = self.require_level(msg.user, level + 1)
            if allowed:
                if token[0] in User.users:
                    old_level = User.users[token[0]].level or 0
                    User.users[token[0]].level = level
                    User.users.sync()
                    log('i',
                        '%s changed the level of user %s from %d to %d.' % (
                        msg.user.name, token[0], old_level, level))
                    return msg.prefix + \
                        _('Changed the level of user %s from %d to %d.') % (
                        token[0], old_level, level)
                else:
                    return msg.prefix + \
                        _('User %s is not registered.' % token[0])
            else:
                return msg.prefix + \
                    _('Unauthorized. Level %d required.' % (level + 1))
        else:
            return msg.prefix + \
                _('You need to specify the username and the level.')
    
    def level(self, msg):
        """Tells which level the user you ask for has, or if you don't specify
        a user, which level you have and if you have already authentificated
        yourself for the current run or not."""
        user = (msg.params.split() + [None])[0]
        if user and user != msg.user.name:
            if user in User.users:
                if User.users[user].password is not None:
                    return msg.prefix + _('User %s has level %d.') % \
                        (user,User.users[user].level)
                else:
                    return msg.prefix + _('User %s is not registered.') % user
            elif user == msg.bot.nickname:
                return msg.prefix + _('That\'s me, I have no level.')
            else:
                return msg.prefix + _('I\'ve never seen %s.') % user
        else:
            if msg.user.password is None:
                return msg.prefix + _('You are not registered.')
            levelstr = _('Your level is %d ') % msg.user.level
            if msg.user.trusted:
                return msg.prefix + levelstr + \
                    _('and you are authenticated.')
            else:
                return msg.prefix + levelstr + \
                    _('but you are currently not authenticated.')
    
    def __unauthenticate(self, user, bot):
        try:
            User.users[user].trusted = False
        except KeyError:
            User.users[user] = User(user, bot.factory.connection)
       
    def user_quit(self, bot, user, quitmsg):
         self.__unauthenticate(user, bot)
    
    def user_part(self, bot, user, chan, reason=None):
        self.__unauthenticate(user, bot)
        
    # def user_joined(self, bot, user, chan):
    #     try_to_add_user(user)
    #     
    # def user_kicked(self, bot, chan, kickee, kicker, message):
    #     try_to_add_user(user)
    # 
    # def user_action(self, bot, user, chan, data):
    #     try_to_add_user(user)
    #     
    # def user_part(self, bot, user, chan, reason=None):
    #     try_to_add_user(user)
        
def try_to_add_user(name):
    try:
        User.users[name]
    except KeyError:
        User.users[name] = User(name)
