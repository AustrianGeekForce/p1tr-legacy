"""Plugin to insult a person with a random phrase."""

###########################################################################

if __name__ == '__main__':
    
    # Massive insult importer
    
    import sys
    import os
    import shelve
    
    resourcefile = 'data/insult_insults'
    
    if len(sys.argv) < 2 or sys.argv[1] != 'import':
        print 'Usage: %s import <file>' % sys.argv[0]
        sys.exit(1)
    
    if not os.path.isfile(resourcefile):
        print 'Please execute this from inside P1tr\'s root folder.'
        sys.exit(1)
    
    if not os.path.isfile(sys.argv[2]):
        print 'File "%s" does not exist.' % sys.argv[2]
        sys.exit(1)
    
    resource = shelve.open(resourcefile, protocol=0, writeback=True)
    
    insults = [line.strip('\n') for line in
        open(sys.argv[2]).readlines() if line]
    for insult in insults:
        if insult not in resource['ins']:
            resource['ins'].append(insult)
    
    resource.sync()
    resource.close()
    sys.exit(0)

###########################################################################

from random import choice
from lib.logger import log
from lib.plugin import Plugin

class InsultPlugin(Plugin):
    
    def __init__(self):
        Plugin.__init__(self, 'insult')
        self._set_summary(_('Plugin to insult somebody in the channel'))
        self._add_command('insult', '<nick>', _('Insults nick.'))
        self._add_command('add_insult', '<phrase>', _('Adds phrase to the \
insults file.'))
        self._add_command('delete_insult', '<phrase>', _('Deletes phrase \
from the insults file.'))
        self.insults = self._load_resource('insults')
        if not self.insults:
            import urllib2
            log('w', 'No insults found in your insults file. Fetching them...')
            self.insults['ins'] = []
            try:
                insults = urllib2.urlopen('http://server.austriangeekforce.' + \
                                          'net/insults.txt')
                insult = True
                while insult:
                    insult = insults.readline()[:-1]
                    if insult:
                        self._add(insult)
            except urllib2.URLError:
                log('e', 'Could not fetch insults.')
                self._add('You are dumber than someone who knows just one ' + \
                          'insult!')
                raise
    
    def insult(self, msg):
        """
        Insults a person randomly; if target is the bot himself, the invoker
        of insult gets insulted.
        """
        if msg.params:
            target = msg.params.split()[0]
        else:
            target = msg.user.name
        if target.lower() == msg.bot.nickname.lower():
            target = _('Who dares to insult me? ') + msg.user.name
        return target + ": " + choice(self.insults['ins'])
    
    def add_insult(self, msg):
        """Adds an insult to the list."""
        insult = msg.params.strip()
        if not insult:
        	return _('You have to tell me the insult that you want to add.')
        if insult in self.insults['ins']:
            return msg.prefix + _('I already knew that insult.')
        self._add(msg.params.strip())
        return msg.prefix + _('Done, my master.')
    
    def delete_insult(self, msg):
        """Deletes an insult from the list."""
        insult = msg.params.strip()
        if not insult:
            return msg.prefix + \
                _('You have to tell me the insult that you want to delete.')
        if insult not in self.insults['ins']:
            return msg.prefix + _('I don\'t know this insult.')
        self.insults['ins'].remove(msg.params.strip())
        self.insults.sync()
        return msg.prefix + _('Done, my master.')
    
    def _add(self, insult):
        self.insults['ins'].append(insult)
        self.insults.sync()
