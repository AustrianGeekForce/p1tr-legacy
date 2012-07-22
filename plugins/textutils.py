"""
Plug-in which demonstrates the basic structure of such things. It is great
as a template for other plug-ins. The function: reversion or length measure of
a string.
"""

from lib.plugin import Plugin

class TextutilsPlugin(Plugin):
    
    def __init__(self):
        Plugin.__init__(self, 'textutils')
        self._set_summary(_('Plugin to return length and reversed string'))
        self._add_command('length', '<string>', _('returns the length of the \
given string'))
        self._add_command('reverse', '<string>', _('reverses the given \
string'))
    
    def length(self, msg):
        if msg.params:
            return len(msg.params)
    
    def reverse(self, msg):
        if msg.params:
            return msg.params[::-1]
