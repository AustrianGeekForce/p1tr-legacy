"""I'm core, king of the Britons."""

import shelve
from sets import Set
from twisted.words.protocols import irc
from twisted.internet import reactor, protocol

from lib.logger import log

class Connection:
    """I store all connection specific information."""
    
    def __init__(self, server):
        self.server = server

def try_to_log_msg(logs, channel, user, message):
    """
    Attempting to log something. If logfiles don't exist because logging
    has been disabled I have no effect.
    """
    try:
        logs[channel].write('<%s> %s' % (user.split('!')[0], message))
    except KeyError:
        # If it produces a key error it means that it comes from a source
        # which has no logfile.
        pass

class IRCBot(irc.IRCClient):
    """I connect to IRC and I'm the first one to get all those events."""
    
    def __init__(self, factory):
        self.factory = factory
        self.nickname = self.factory.connection.nick
        self.realname = self.factory.connection.realname
        self.extended = self.factory.connection.extended
        self.versionName = 'p1tr (bot)'
        self.versionNum = ''
        self.versionEnv = 'http://launchpad.net/p1tr'
        self.logs = {}
        self.plugins = Set(self.factory.plugin_handler.plugins.values())
    
    def msg(self, user, message, length=None):
        """Send a message to user or channel."""
        if hasattr(message, '__iter__'):
            for msg in message:
                irc.IRCClient.msg(self, user, msg, length)
        else:
            irc.IRCClient.msg(self, user, message, length)
        # Write P1tr's own talking to log, if activated.
        try_to_log_msg(self.logs, user, self.nickname, message)
    
    def privmsg(self, user, channel, msg):
        """Called when a PRIVMSG appears."""
        self.factory.plugin_handler.handle(Message(self, channel, user, msg))
    
    def me(self, channel, data):
    	"""Do an action in a channel."""
    	irc.IRCClient.me(self, channel, data)
    
    def action(self, user, channel, data):
        """Called when someone performs an action."""
        for plugin in self.plugins:
            plugin.user_action(self, user, channel, data)
    
    def connectionMade(self):
        """This may be considered the initializer of the protocol, because it
        is called when the connection is completed."""
        irc.IRCClient.connectionMade(self)
        for plugin in self.plugins:
            plugin.on_connect(self)
    
    def connectionLost(self, reason):
        """Called when the connection is shut down."""
        irc.IRCClient.connectionLost(self, reason)
        for plugin in self.plugins:
            plugin.on_disconnect(self, reason)
    
    def signedOn(self):
        """Called after successfully signing on to the server."""
        map(self.join, self.factory.connection.channels)
    
    def kickedFrom(self, channel, kicker, message):
        """Some bastard kicked me! He will pay for that."""
        for plugin in self.plugins:
            plugin.bot_kicked(self, channel, kicker, message) 
    
    def userKicked(self, kickee, channel, kicker, message):
        """Called when I watch someone getting kicked and smile meanwhile."""
        for plugin in self.plugins:
            plugin.user_kicked(self, channel, kicker, kickee, message)
    
    def modeChanged(self, user, channel, set, modes, args):
        """Called when modes get changed, obviously"""
        for plugin in self.plugins:
            plugin.mode_changed(self, user, channel, set, modes, args)
    
    def joined(self, channel):
        """Called when I come to a channel."""
        for plugin in self.plugins:
            plugin.bot_joined(self, channel)
    
    def userJoined(self, user, channel):
        """Called when I see someone entering the channel."""
        for plugin in self.plugins:
            plugin.user_joined(self, user, channel)
    
    def left(self, channel, reason):
        """Called when it is time to say goodbye and leave the channel."""
        for plugin in self.plugins:
            plugin.bot_part(self, channel, reason)
    
    def userLeft(self, user, channel):
        """Called when someone has to go."""
        for plugin in self.plugins:
            plugin.user_part(self, user, channel)
    
    def topicUpdated(self, user, channel, newTopic):
        """Called when topic is being changed."""
        for plugin in self.plugins:
            plugin.topic_updated(self, user, channel, newTopic)
    
    def userRenamed(self, oldname, newname):
        """Called when some user has the crazy idea to change his name."""
        for plugin in self.plugins:
            plugin.user_renamed(self, oldname, newname)
    
    def receivedMOTD(self, motd):
        """
        Thus Lord Server spake the Message of the day. And this is, what
        happens when he speaks.
        """
        for plugin in self.plugins:
            plugin.received_MOTD(self, motd)

class IRCBotFactory(protocol.ClientFactory):
    """I produce IRCBot instances. And I'm proud of it. """
    
    # the class of the protocol to build when new connection is made
    protocol = IRCBot
    
    def __init__(self, connection, plugin_handler):
        self.connection = connection
        self.plugin_handler = plugin_handler
        self.build_protocol = None
    
    def clientConnectionLost(self, connector, reason):
        """If we get disconnected, reconnect to server."""
        connector.connect()
    
    def clientConnectionFailed(self, connector, reason):
        """When connection to the server fails reactor is stopped."""
        log('f', 'Connection failed: ' + str(reason))
        protocol.ClientFactory.clientConnectionFailed(self, connector, reason)
    
    def buildProtocol(self, addr):
        self.build_protocol = self.protocol(self)
        return self.build_protocol

class IRCConnection(Connection):
    """I contain the IRC specific connection making functionality. """
    
    def connect(self, plugin_handler):
        """I create a TCP connection and an IRCBot using a IRCBotFactory"""
        self.factory = IRCBotFactory(self, plugin_handler)
        reactor.connectTCP(self.server, self.port, self.factory)

class Message:
    
    def __init__(self, bot, chan, user, msg):
        self.bot = bot
        self.chan = chan
        self.msg = msg
        self.keyword = None
        self.params = None
        self.parse_message()
        try: 
            self.user = User.users[user.split("!")[0]]
        except KeyError:
            self.user = User(user, self.bot.factory.connection)
        self.prefix = self.user.name + ': '
    
    def generate_signals(self):
        """
        Returning a list of strings which people need to use if they want
        to make P1tr react on a keyword is great fun.
        """
        return (self.bot.nickname, self.bot.nickname.capitalize(),
                   self.bot.nickname.lower(),
                   self.bot.factory.connection.signal_char,
                   self.bot.factory.connection.signal_char + self.bot.nickname,
                   self.bot.factory.connection.signal_char \
                        + self.bot.nickname.capitalize(),
                   self.bot.factory.connection.signal_char \
                        + self.bot.nickname.lower())
    
    def parse_message(self):
        """I give P1tr messages which he can handle."""
        signals = self.generate_signals()
        token = self.msg.split()
        
        if len(token) >= 3 and \
                (token[0][:-1] in signals or token[0] in signals):
            self.keyword = token[1]
            self.params = ' '.join(token[2:])
        
        elif len(token) == 2 and \
                (token[0][:-1] in signals or token[0] in signals):
            self.keyword = token[1]
            self.params = ''
        
        elif token and token[0][0] == self.bot.factory.connection.signal_char:
            try:
                self.keyword = token[0][1:]
                if ' ' in self.msg:
                    self.params = self.msg[self.msg.index(' ')+1:]
                else:
                    self.params = ''
            except IndexError:
                self.keyword = token[0][1:]
        
        else:
            self.keyword = None
            self.params = ''

class User:
    """My instances represent each user in an IRC channel."""
    
    users = shelve.open("./data/users", protocol=0, writeback=True)
    
    def __init__(self, name, level=None, trusted=False,):
        self.name = name.split("!")[0]
        self.hostmask = name
        self.password = None
        self.trusted = False
        self.level = 0
        User.users[self.name] = self
        log('i', 'Saved user %s into the database.' % self.name)
    
    def __str__(self):
        return '%s (Hostmask: %s, Level: %d, Trusted: %s)' % (self.name,
            self.hostmask, self.level, str(self.trusted))
