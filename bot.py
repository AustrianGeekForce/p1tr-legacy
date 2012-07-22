#!/usr/bin/env python2.6
# -*- coding: utf-8 -*-

"""P1tr launcher."""

import os
import sys
from twisted.internet import reactor

from lib.helpers import *
from lib import core
from lib import plugins
from lib.logger import log
from lib.config import configuration

args = complete_args_dict(parse_args(sys.argv))
if args['-h']:
    print """P1tr IRC Bot by AustrianGeekForce
-h                  - display this help message
-s <server>         - connect bot to this server
-po <port>          - port to connect
-pw <password>      - server password
-ssl true           - connect via SSL
-n <nick>           - use this nickname to connect
-npw <password>     - password for identifying nick
-cnf <path>         - specify path to config file
-ho <host>          - specify host used for server identification"""

def main():
    """Called when this file is being executed."""
    
    try:
        log('i', 'P1tr 0.1 is starting up...')
        
        # Go to p1tr's directory
        os.chdir(os.path.dirname(os.path.abspath(__file__)))
        
        # Load language
        load_language()
        
        # Load configuration
        servers = configuration.servers
        
        # Loads plug-ins and plug-in handlers
        plugs = plugins.PluginLoader().load_plugins()
        handler = plugins.PluginHandler(plugs)
        
        for srv in servers:
            srv.connect(handler)
        
        reactor.run()
        
        log('i', 'Regular P1tr shutdown.\n**********\n**********\n')
    
    except KeyboardInterrupt:
        log('e', 'Shutdown, caused by KeyboardInterrupt.')
        core.User.users.sync()
        reactor.stop()

if __name__ == "__main__":
    main()
