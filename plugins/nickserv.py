"""
Plugin that provides authentication with the NickServ service (used
by Freenode and other IRC networks).

To use this plugin, you'll have to add the following entry to your
configuration file:

  X-NickServ-Password = your password here

"""

from lib.plugin import Plugin
from lib.logger import log
from lib.config import xdata

class NickservPlugin(Plugin):
    
    def __init__(self):
        Plugin.__init__(self, 'nickserv')
        self._set_summary(_('Plugin that provides authentication with NickServ'))
    
    def on_connect(self, bot):
        password = xdata(bot, self.name, 'password')
        if password:
        	log('i', 'Trying to identify with NickServ...')
        	bot.msg('NickServ', 'IDENTIFY ' + password)
