"""
Plug-in which demonstrates the usage of the listener. It returns the
things other people say. Now, that is meaningful.
"""

from lib.plugin import Plugin

class TalkbackPlugin(Plugin):
    
    
    def __init__(self):
        Plugin.__init__(self, 'talkback')
        self._set_summary(_('Plugin to repeat what others say in a channel'))
        self._add_command('talkback', None, _('initiates talkback'))
        self._add_command('stfu', None, _('lets talkback shut up'))
        self.talk_back = False
    
    def talkback(self, msg):
        access_granted = self.require_level(msg.user, 10)
        if access_granted:
            self.talk_back = True
        else:
            return _("Thou shall not try to abuse mighty " + msg.bot.nickname)
    
    def stfu(self, msg):
        self.talk_back = False
    
    def _listen_(self, msg):
        if msg.msg and self.talk_back and msg.chan != msg.bot.nickname:
            return msg.msg
        else:
            return None
