"""Home of the mother of all plug-ins."""

import os
import shelve
import subprocess
from lib.core import User
from lib.logger import log

class Plugin:
    """
    I'm the mother of all plug-ins. Therefore thou shall inherit from me in
    case of writing a plugin!
    """
    
    def __init__(self, name):
        self.name = name.lower()
        self.keywords = []
        self._summary = None
        self._help_topics = {}
    
    def _set_summary(self, summary):
        """Changes content of the top-level help message of this plugin."""
        if self._summary:
            log('w', 'Plugin summary is being overwritten.')
        self._summary = summary
    
    def _add_command(self, command, usage='', description=None):
        """
        Adds a keyword to self.keywords and, if given, a help message for it
        to the help system.
        """
        self.keywords.append(command)
        if description:
            if usage:
                usage = ' ' + usage
            else:
                usage = ''
            self._add_help_topic(command, _('Usage: ') + command + usage
                                  + ' - ' + description)
    
    def _add_help_topic(self, topic, description):
        """
        Adds a topic and a help message to the help system, but without
        reserving a keyword.
        """
        self._help_topics[topic] = description
    
    def get_help_topics(self):
        """Returns a list of top-level help topics, usually named like the
        commands."""
        return self._help_topics.keys()
    
    def help(self, topic=None):
        """Return the help message."""
        
        if topic:
            if topic in self._help_topics:
                return self._help_topics[topic]
            else:
                raise ValueError, 'No help for the given topic.'
        else:
            if not self._summary:
                 return _('This plugin has no help.')
                    
            if not self._help_topics:
                return self._summary
            else:
                return self._summary + '; ' + _('topics: ') \
                         + ', '.join(self._help_topics.keys())
    
    def _load_resource(self, title):
        """
        Returns a shelve if it can be opened, otherwise None.
        Example usage in a plugin: self.data = self._load_resource('info')
        This creates data/pluginname_info, where everything you write to
        self.data is stored. After adding information to self.data it is
        recommended to to self.data.sync() to write changes to the file.
        In case you need the resource just for a limited time you can close
        it using self._close_resource(self.data). This does the sync() for
        you.
        """
        try:
            res = shelve.open(os.path.join('data', '%s_%s' % (self.name,
                                    title)), protocol=0, writeback=True)
            return res
        except anydbm.error:
            log('e', 'Unable to open resource file:')
            raise
            return None
    
    def _get_output(self, command, stdout = True, stderr = False):
        """
        Runs a program specified in the first argument and returns its output
        as a string.
        """
        if (stdout or stderr) and not (stdout and stderr):
            pipe = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE)
            if stdout:
            	return pipe.stdout.read()
            else:
            	return pipe.stderr.read()
        elif stdout and stderr:
        	return subprocess.Popen(command, shell=True, stdout=subprocess.PIPE,
                                    stderr=subprocess.STDOUT).stdout().read()
        else:
            try:
                return bool(subprocess.Popen(command))
            except OSError:
                log('w', "could not execute process")
                return None
    
    def _close_resource(self, res):
        """Syncs and closes a shelve."""
        res.sync()
        res.close()
        log('i', 'Resource was closed successfully.')
    
    def privmsg(self, msg):
        """I call the appropriate function for a keyword"""
        return getattr(self, msg.keyword)(msg)
        
    def listen(self, msg):
        pass
    
    #this is a bit dirty atm,workin on it
    def require_level(self, user, level):
        """
        Use this function inside a plugin to determine if the level of the
        user who invokes a keyword is sufficient. Returns True if it is
        and False otherwise.
        """
        if user.level >= level and user.trusted:
            log('i', 'Permission granted to user ' + str(user))
            return True
        else:
            log('i', 'Permission denied to user ' + str(user))
            return False
    
    def on_connect(self, bot):
        """This may be considered the initializer of the protocol, because it
        is called when the connection is completed."""
        pass
    
    def on_disconnect(self, bot, reason):
        """Called when the connection is shut down."""
        pass
    
    def user_joined(self, bot, user, chan):
        """Called when some user joins a channel."""
        pass
    
    def user_kicked(self, bot, chan, kickee, kicker, message):
        """Called when some user gets kicked."""
        pass
    
    def user_action(self, bot, user, chan, data):
        """Called when some user performs an action (most IRC clients use 
        /me for actions)."""
        pass
    
    def topic_updated(self, bot, user, chan, data):
        """Called when topic gets changed."""
        pass
    
    def user_renamed(self, bot, oldname, newname):
        """Called when some user changes his nickname."""
        pass
    
    def received_MOTD(self, bot, motd):
        """Called when server sends a MOTD to me."""
        pass
    
    def user_quit(self, bot, user, quitmsg):
        """Called when some user leaves the server."""
        pass
    
    def user_part(self, bot, user, chan, reason=None):
        """Called when some user leaves a channel."""
        pass
    
    def mode_changed(self, bot, user, chan, set, modes, args):
        """Called when modes inside a channel get changed."""
        pass
    
    def bot_kicked(self, bot, chan, kicker, message):
        """Called when someone dares to kick me, teh b0t."""
        pass
    
    def bot_joined(self, bot, chan):
        """Called when I enter a channel."""
        pass
    
    def bot_part(self, bot, chan, reason):
        """Called when I leave a channel."""
        pass
