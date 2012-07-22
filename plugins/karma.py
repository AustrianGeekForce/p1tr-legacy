"""Plugin for Karma tracking."""

from lib.plugin import Plugin
from lib.logger import log

class KarmaPlugin(Plugin):
    
    def __init__(self):
        Plugin.__init__(self, 'karma')
        self._set_summary(_('Keeps track of the karma people/things have'))
        self._add_command('karma', '<item>', _('Displays Karma statistics for\
 item. If item is not given, it shows global karma stats.'))
        self._add_command('reset_karma', '<item>', _('Resets karma stats for \
item.'))
        self._add_help_topic('usage', _('Append ++/-- to a term without \
spaces in it to in-/decrease the karma of this term. Use the karma command \
to get statistics to a certain term.'))
        self.vault = self._load_resource('vault')
    
    def _listen_(self, msg):
        """Watching if ++ or -- appear in a channel appended to a single
        word."""
        for word in msg.msg.split(' '):
            if word[:-2].lower() == msg.user.name.lower():
                return msg.prefix + \
                       _('Don\'t even think of modifying your own karma.')
            else:
                if word[-2:] == '++':
                    self._xcrease(True, word[:-2].lower())
                elif word[-2:] == '--':
                    self._xcrease(False, word[:-2].lower())
    
    def karma(self, msg):
        """
        If parameters given, returns a summary of first parameter's karma. IF
        not you can see some pretty stats."""
        if len(msg.msg.split(' ')) > 1:
            word = msg.msg.split(' ')[1].lower()
            if self._word_exists(word):
                pos = self.vault[word][0]
                neg = self.vault[word][1]
                sum = self.vault[word][2]
                if sum > 99:
                    comment = _('%s is far too good! Practice Evil, my friend.'
                     %  word)
                elif 100 > sum > 0:
                    comment = _('What a nice %s, so many good deeds...') % word
                elif sum == 0:
                    comment = _('The ultimate way to Nirvana.')
                elif -50 < sum < 0:
                    comment = _('Such a bad boy.')
                elif -49 < sum:
                    comment = _('%s seems to be an evil genius in training.' %
                                word)
                return _('Karma statistics for %s: +%i -%i => %i -- %s' % 
                          (word, pos, neg, sum, comment))
            else:
                return _('%s has no karma recordings yet.' % word)
        else:
            highest = ['None', 0]
            lowest = ['None', 0]
            pos = 0
            neg = 0
            sum = 0
            for k, v in self.vault.items():
                log('i', '%s#%s' % (str(k), str(v)))
                if v[2] > highest[1]:
                    highest = [k, v[2]]
                if v[2] < lowest[1]:
                    lowest = [k, v[2]]
                pos += v[0]
                neg += v[1]
                sum += v[2]
            return _('I keep track of %i people\'s karma. Overall I noticed \
%i positive and %i negative karma points. %s is the most well behaved I \
know. %s seems to have a Bachelor\'s degree in Darkness. The common karma of \
all people I know is %i.' % (len(self.vault), pos, neg, highest[0], lowest[0],
                            sum))
    
    def reset_karma(self, msg):
        """Resets karma of first parameter if invoker has level."""
        level = 15
        if self.require_level(msg.user, level):
            word = msg.params.split(' ')[0].lower()
            if self._word_exists(word):
                del self.vault[word]
                self.vault.sync()
                return _('Reset karma of %s.' % word)
            else:
                return _('%s has no karma recordings yet.' % word)
        else:
            return _('Unauthorized. Level %s required.' % level)
    
    def _word_exists(self, word):
        """Checks if word exists and returns either True or False."""
        try:
            self.vault[word]
            return True
        except KeyError:
            log('w', 'No vault entry for %s.' % word)
            return False
    
    def _xcrease(self, what, word):
        """
        what specifies if the karma of word is being in- or decreased. what
        can be either True or False. word must be a string without spaces.
        """
        # The self.vault dictionary is structured like this (example with
        # one item):
        # {'word': [pos, neg]}
        # pos is an integer which gets increased if what is True
        # neg is an integer which gets increased if what is False
        if not self._word_exists(word):
            self.vault[word] = [0, 0, 0]
        if what:
            self.vault[word][0] += 1
        else:
            self.vault[word][1] += 1
        self.vault[word][2] = self.vault[word][0] - self.vault[word][1]
        self.vault.sync()
