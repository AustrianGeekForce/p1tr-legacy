"""Plugin which allows you to store facts associated with a specific keyword.

One way to add new informations is using "<signal><key> is <information>", and
to retrieve the facts for a keywoard you have to use "<signal><key>?". However,
if you don't to use the same signal character for p1tr's normal commands and
for factoids, you can choose a second one by adding the following line to
your configuration file (in section "global"):

  X-Factoids-Signal = <signal>

"""

import re
from random import choice

from lib.plugin import Plugin
from lib.logger import log
from lib.config import configuration, xdata

class FactoidsPlugin(Plugin):
    
    def __init__(self):
        
        Plugin.__init__(self, 'factoids')
        
        self._set_summary(_('Factoids stores strings to a keyword'))
        self._add_command('factoids', '[<filter>]', _('shows a list of \
keywords'))
        self._add_command('associate', '<word> <info>', _('Associates the \
given info string with the word.'))
        self._add_command('forget', '<word> <id>', _('If id is given it makes \
me delete the word\'s fact with that id, otherwise I forget everything about \
word.'))
        self._add_command('random_fact', None, _('displays a random fact from \
any word'))
        self._add_command('search_factoid', '<term>', _('searches all \
factoids for term. Add "word:something" in the begining to find only factoids \
of something'))
        self._add_help_topic('association', _('Examples: Arthur is the king \
of the Britons; Romans are hook-nosed.'))
        self._add_help_topic('remembering', _('Example: arthur? - response: \
[0] Arthur is the king of the britons\\n[1] Arthur is seeking the holy grail.'))
        
        self.vault = self._load_resource('vault')
        self.old_request = None # Contains the last requested sequence
        
        if xdata(configuration, self.name, 'signal'):
            self.factoid_char = xdata(configuration, self.name, 'signal')[0]
        else:
            # The signal char will be assigned during the first _listen_
            # execution. We can't do this now as here we don't know which it.
            self.factoid_char = None
    
    def _listen_(self, msg):
        """
        I'm listening to what the people say. If it looks like "keyword?",
        "keyword is something", or "things are something" I do the appropriate
        thing.
        """
        if not self.factoid_char:
            self.factoid_char = msg.bot.factory.connection.signal_char
        
        # Explanation: [word, (is|are)|range(optional), fact(optional)]
        sequence = [None, None, None]
        message = msg.msg.split(' ')
        # Adds, if present, values to sequence. If not, None as default is not
        # overwritten.
        if len(message) > 0:
            sequence[0] = message[0][1:]
        if len(message) > 1:
            sequence[1] = message[1]
        if len(message) > 2:
            sequence[2] = ' '.join(message[2:])
        # Checks step-by-step if all parts of sequence required for a certain
        # action are not None.
        if sequence[0]:
            if message[0][0] == self.factoid_char:
                if sequence[0] == 'more':
                    request = self.old_request
                    request[1] = range(request[1][-1:][0] + 1,
                                       request[1][-1:][0] + 4)
                    self._view(msg, request[0], request[1])
                    self.old_request = request
                elif sequence[0][-1:] == '?' or (self.factoid_char !=
                    msg.bot.factory.connection.signal_char and not sequence[2]):
                    # This code is executed if request looks like:
                    # *P1tr? 0-2 - where 0-2 is optional, as checked here:
                    if sequence[1]:
                        ints = sequence[1].split('-')
                        try:
                            sequence[1] = range(int(ints[0]),
                                                int(ints[1]) + 1)
                        except ValueError:
                            msg.bot.msg(msg.reply_to, _('Invalid range, dude.'))
                    else:
                        sequence[1] = range(0, 3)
                    self._view(msg, sequence[0], sequence[1])
                    # self.old_request gets overwritten as soon as another
                    # request is made.
                    self.old_request = sequence
                elif sequence[1] in (_('is'), _('are'), 'is', 'are') and \
                sequence[2]:
                    msg.bot.msg(msg.reply_to, msg.prefix +
                        self._add(sequence[0], ' '.join(sequence)))
    
    def factoids(self, msg):
        """Prints a list of the words which have factoids."""
    	args = [arg for arg in msg.msg.split(' ')[1:] if arg]
        msg.bot.msg(msg.reply_to, self._list(args[0] if args else ''))
    
    def forget(self, msg):
        """Deletes all factoids of a word or just specific factoids."""
        level = 10
        if self.require_level(msg.user, level):
            params = msg.msg.split(' ')[1:]
            word = params[0].lower()
            if word not in self.vault:
                msg.bot.msg(msg.reply_to,
                    _('I don\'t know anything about %s') % word)
            elif len(params) > 1 and len(self.vault[word]) > int(params[1]):
                del self.vault[word][int(params[1])]
                msg.bot.msg(msg.reply_to, _('Forgot %s\'s fact number %s') %
                            (word, params[1]))
                self.vault.sync()
            else:
                del self.vault[word]
                msg.bot.msg(msg.reply_to,
                    _('Forgot everything about %s') % word)
                self.vault.sync()
        else:
            return _('Unauthorized. Level %s required.' % level)
    
    def random_fact(self, msg):
        """Prints a random factoid from any word."""
        msg.bot.msg(msg.reply_to, self._random())
    
    def associate(self, msg):
        """Associates the given information with the indicated name."""
        params = msg.params.split(' ')
        if len(params) > 1:
            return msg.prefix + self._add(params[0], ' '.join(params[1:]))
        else:
            return msg.prefix + _('Not enough arguments.')
    
    def search_factoid(self, msg):
        """Searches all factoids or just one word for facts containig a
        term."""
        self.results = []
        if 'word:' in msg.params:
            params = msg.params.split('word:')[-1:][0].split(' ')
            self._search(' '.join(params[1:]), params[0])
        else:
            for word in self.vault:
                self._search(msg.params, word)
        if self.results:
            msg.bot.msg(msg.reply_to, _('%s: Results of your search: %s' % \
                                    (msg.user.name, ', '.join(self.results))))
        else:
            msg.bot.msg(msg.reply_to, _('Sorry, nothing found.'))
    
    def _list(self, filter=''):
        filter = filter.lower()
        if not filter:
            keys = self.vault.keys()
        else:
        	keys = [key for key in self.vault.keys() if filter in key]
        return ', '.join(keys)
    
    def _add(self, word, fact):
        word = word.lower()
        # Check if this fact has already been entered
        if word in self.vault and fact in self.vault[word]:
            return _('You already told me that.')
        else:
            if word in self.vault:
                self.vault[word].append(fact)
            else:
                self.vault[word] = [fact, ]
            self.vault.sync()
            return _('Memorized.')
    
    def _view(self, msg, word, from_to):
        word = word.lower().strip('?')
        if word not in self.vault:
            msg.bot.msg(msg.reply_to,
                _('I don\'t know anything about %s') % word)
        else:
            for item in self.vault[word]:
                index = self.vault[word].index(item)
                if index in from_to:
                    msg.bot.msg(msg.reply_to,
                        '[%s] %s' % (index, self.vault[word][index]))
                if index == from_to[-1]:
                    if len(self.vault[word]) > (index + 1):
                        self.vault[word][index + 1]
                        msg.bot.msg(msg.reply_to,
                            '%smore to see more entries.' % self.factoid_char)
    
    def _random(self):
        wordlist = self.vault.keys()
        word = choice(wordlist)
        fact = choice(self.vault[word])
        return '%s %s' % (word, fact)
    
    def _search(self, term, word):
        for fact in self.vault[word]:
            if term in fact:
                self.results.append('%s %s [%s]' % (word,
                                        self.vault[word].index(fact), fact))
