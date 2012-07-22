"""Plugin to count how often a word is mentioned."""

from lib.plugin import Plugin

class TrackerPlugin(Plugin):
    
    
    def __init__(self):
        Plugin.__init__(self, 'tracker')
        self._set_summary(_('Counts how often a word is mentioned. \
Case-sensitive. Words get counted only in one channel'))
        self._add_command('track', '<word>', _('Adds word to tracklist.'))
        self._add_command('untrack', '<word>', _('Removes word from \
tracklist.'))
        self._add_command('tracklist', '<channel>', _('Shows all tracked \
words for channel. If channel is not given, the words of the current one get \
displayed.'))
        self._add_command('trackstats', '<word>', _('Shows how often word \
was mentioned and the three people who mention it the most.'))
        self.resource = self._load_resource('resource')
        # Structure of self.resource dictionary:
        # {'server': {'channel': {'word': {'nick': int, }, }, }, }
        self.watched = []
        # For better performance inside listener all words P1tr watches
        # anywhere are stored in self.watched.
        for server in self.resource:
            for channel in self.resource[server]:
                self.watched.extend(self.resource[server][channel].keys())
    
    def _listen_(self, msg):
        """
        Watches for words on the tracklist. If such appear the number of
        calls by the respective nick gets increased.
        """
        server = msg.bot.factory.connection.server
        nick = msg.user.name
        for word in msg.msg.split():
            if (word in self.watched and
                        self._check_existance(server, msg.chan, word)):
                if nick in self.resource[server][msg.chan][word]:
                    self.resource[server][msg.chan][word][nick] += 1
                else:
                    self.resource[server][msg.chan][word][nick] = 1
                self.resource.sync()
    
    def track(self, msg):
        """Adds a word to the tracklist for this channel."""
        level = 10
        if self.require_level(msg.user, level):
            server = msg.bot.factory.connection.server
            if msg.params:
                word = msg.params.split()[0]
                if self._check_existance(server, msg.chan, word):
                    return _('"%s" is already being tracked.' % word)
                else:
                    self.resource[server][msg.chan][word] = {msg.user.name: 1}
                    self.resource.sync()
                    self.watched.append(word)
                    return _('Tracking "%s" now.' % word)
            else:
                return _('You forgot to enter a word to track.')
        else:
            return _('Unauthorized. Level %s required.' % level)
    
    def untrack(self, msg):
        """Removes a word from the tracklist for this channel."""
        level = 10
        if self.require_level(msg.user, level):
            server = msg.bot.factory.connection.server
            if msg.params:
                word = msg.params.split()[0]
                if self._check_existance(server, msg.chan, word):
                    del self.resource[server][msg.chan][word]
                    self.resource.sync()
                    del self.watched[self.watched.index(word)]
                    return _('Removed "%s" from tracklist.' % word)
                else:
                    return _('"%s" is not yet being tracked.' % word)
            else:
                return _('You forgot to enter a word to untrack.')
        else:
            return _('Unauthorized. Level %s required.' % level)
    
    def tracklist(self, msg):
        """Lists all tracked words for this channel or a given channel."""
        server = msg.bot.factory.connection.server
        if msg.params and msg.params[0] == '#':
            channel = msg.params.split()[0]
        else:
            channel = msg.chan
        return _('Tracked words in %s: %s' % (channel,
                        ', '.join(self.resource[server][channel].keys())))
    
    def trackstats(self, msg):
        """
        Shows the three nicknames in self.resource[server][channel][word] who
        have mentioned word the most often plus the total number of calls.
        """
        if msg.params:
            word = msg.params.split()[0]
            server = msg.bot.factory.connection.server
            if self._check_existance(server, msg.chan, word):
                stats = self.resource[server][msg.chan][word]
                total = sum([stats[calls] for calls in stats])
                # Sort caller's nicks by number of calls
                callers = [(stats[caller], caller) for caller in stats.keys()]
                callers.sort(reverse=True)
                # Make the tuples nice looking strings
                pairs = [_('%s (%i times)') % (pair[1], pair[0])
                        for pair in callers]
                return _('"%s" was mentioned %i times. Top callers: %s' %
                            (word, total, ', '.join(pairs)))
            else:
                return _('"%s" is not yet being tracked.' % word)
        else:
            return _('You forgot to enter which word\'s stats should be \
shown.')
    
    def bot_joined(self, bot, chan):
        """
        Check if channel already exists in self.resource. If not it is
        created.
        """
        self._check_existance(bot.factory.connection.server, chan, '')
    
    def _check_existance(self, server, channel, word):
        """
        Checks if there is a server-channel-word structure in self.resource
        for the given server, channel, and word. If server and channel don't
        exist yet they get created. If word exists, True gets returned,
        otherwise False.
        """
        if not server in self.resource.keys():
            self.resource[server] = {}
            self.resource.sync()
        if not channel in self.resource[server].keys():
            self.resource[server][channel] = {}
            self.resource.sync()
        if word in self.resource[server][channel].keys():
            return True
        else:
            return False
