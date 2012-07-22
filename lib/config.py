"""I take care that the contents of a config file can be used."""
# -*- coding: utf-8 -*-

import os.path
import sys
from ConfigParser import SafeConfigParser

from lib.core import IRCConnection
from lib.logger import log

# Constants for usage in other files:
config_true = ('1', 'yes', 'true', 'on')
config_false = ('0', 'no', 'false', 'off')

def xdata(storage_object, plugin, key, default=None):
    if not hasattr(storage_object, 'is_storage_instance'):
        storage_object = getattr(storage_object, 'extended')
    if hasattr(storage_object, plugin) and \
    hasattr(getattr(storage_object, plugin), key):
        return getattr(getattr(storage_object, plugin), key)
    else:
        return default

def xdata_bool(*args):
    value = xdata(*args)
    if value and value.lower() in config_true:
        return True
    else:
        return False

class Storage:
    # An empty class to store data in it.
    is_storage_instance = True
    def __repr__(self):
        return str(vars(self))
    def __len__(self):
        return len(vars(self))

class ConfigLoader:
    
    config_file = None
    servers = []
    possible_locations = (
        os.path.join(os.path.dirname(os.path.abspath(__file__)), '../bot.conf'),
        os.path.join(os.path.dirname(os.path.abspath(__file__)), '../p1tr.conf'),
        os.path.join(os.path.expanduser('~'), '.p1tr'),
        os.path.join(os.path.expanduser('~'), '.config/p1tr/p1tr.conf'),
        os.path.join(os.path.expanduser('~'), '.p1tr', 'bot.conf'),
        '/etc/p1tr.conf'
    )
    
    def __init__(self):
        for file in self.possible_locations:
            if os.path.isfile(file):
                self.config_file = os.path.normpath(file)
                log('i', 'Using configuration file "%s".' % self.config_file)
                break
        if not self.config_file:
            log('f', 'Could not find any configuration files.')
            try:
                import install
                self.config_file = install.main()
                log('i', 'Starting the installer...')
            except ImportError:
                pass
        
        self._load()
    
    def _get(self, section, option, default=None):
        """
        Wrapper for SafeConfigParser's get() function, which returns
        None when a NoOptionError would be raised.
        """
        if self.config.has_option(section, option):
            value = self.config.get(section, option)
        else:
            value = default
        
        return value
    
    def _load(self):
        # Read the configuration file
        self.config = SafeConfigParser()
        self.config.readfp(open(self.config_file, 'r'))
        
        # Extract the general configuration options
        self.language = self._get('global', 'language') or 'en'
        self.superadmin = self._get('global', 'superadmin') or ''
        self.plugins_blacklist = tuple([module for module in
            self._get('global', 'plugins_blacklist', '').split(' ') if module])
        self.extended = self._load_extended('global')
        if not self.superadmin:
            log('w', 'There\'s no superadmin defined in the configuration \
file; the bot won\'t recognize its owner.')
        
        # Create the different connection classes
        for conn in [conn for conn in self.config.sections() if
        conn != 'global']:
            self._create_connection(conn)
        
        if not len(self.servers):
            log('f', 'No valid connection defined in configuration file.')
            log('i', 'Aborting.')
            sys.exit(1)
    
    def _load_extended(self, section):
        extended = Storage()
        for option in [opt for opt in self.config.options(section) if
        opt.startswith('x-')]:
            try:
                (plugin, key) = option.split('-', 2)[1:]
            except ValueError:
                log('w', 'Incorrect entry "%s" in config section "%s"' % (
                    option, section))
                continue
            if not hasattr(extended, plugin):
                setattr(extended, plugin, Storage())
            setattr(getattr(extended, plugin), key, self._get(section, option))
        return extended
    
    def _create_connection(self, conn):
        # Initialize variables
        channels = []
        port = 0
        
        # Server and Port
        server = self._get(conn, 'server') or None
        if not server:
            log('e', 'No server defined for connection "%s".' % conn)
            return False
        if ':' in server:
            server, port = server.split(':')
        
        # Channels
        if not self.config.has_option(conn, 'channels'):
            log('w', 'Connection "%s" has no channel definition.' % conn)
        for channel in self._get(conn, 'channels').split(' '):
            if not channel.startswith('#'):
                log('w', 'Channel "%s" doesn\'t start with a hash (#); \
ignoring.' % channel)
            channels.append(channel)
        if not len(channels):
            log('e', 'No valid channel defined for connection "%s".' % conn)
            return False
        
        # Create the connection class
        connection = IRCConnection(server)
        connection.name = conn
        connection.port = int(port) or 6667
        connection.ssl = self._get(conn, 'ssl') or False
        connection.password = self._get(conn, 'password') or None
        connection.host = self._get(conn, 'host') or 'localhost'
        connection.nick = self._get(conn, 'nick') or 'p1tr'
        connection.realname = self._get(conn, 'realname') or 'P1tr IRC Bot'
        connection.nickpw = self._get(conn, 'nickpw') or None
        connection.channels = channels
        connection.signal_char = (self._get(conn, 'signal') or '*')[0]
        
        # Load X-* values for this connection
        connection.extended = self._load_extended(conn)
        
        # Save it
        self.servers.append(connection)
        log('i', 'Loaded configuration for connection "%s".' % conn)
        return connection

configuration = ConfigLoader()
