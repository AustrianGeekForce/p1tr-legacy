"""Plugin for generating search links for wikipedia, google, yahoo and
wikia."""

from lib.plugin import Plugin

class SearchPlugin(Plugin):
    
    
    def __init__(self):
        Plugin.__init__(self, 'search')
        self._set_summary('Plugin to provide a quick way to generate search \
links')
        self._add_command('search', '<searchengine> <something>', 
            _('returns a link of the given search engine searching something'))
        self.searches = {'-google': 'http://www.google.com/search?\
hl=en&q=searchstring', 
'-wiki_en': 'http://en.wikipedia.org/wiki/Special:Search?search=searchstring',
'-wiki_de': 'http://de.wikipedia.org/wiki/Special:Search?search=searchstring',
'-yahoo': 'http://search.yahoo.com/search?p=searchstring',
'-wikia': 'http://re.search.wikia.com/search#searchstring', }
      
    def search(self,msg):
        """
        If term and engine are given, returns search link. Otherwise search
        returns a help message.
        """
        search = msg.msg.split(' ', 2)
        if len(search) < 3:
            
            engines = ' Engine can be: '
            for key in self.searches: 
                engines = engines + ', ' + key
            return 'With which search engine should I search after what? \
Use: \''+ msg.bot.factory.connection.signal_char +'search -engine searchterm \'.' + engines 
        else:
            return 'You searched for ' + search[2] + ': ' + \
                            self.searches[search[1]].replace('searchstring', 
                                            (search[2].replace(' ', '%20')))
