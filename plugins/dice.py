"""
Plugin for rolling various dices. Parsing and rolling functions are taken from
mrc_001's NetDice. For the parse_dice_string and roll_it function's docs, see
http://server.austriangeekforce.net/stuff/netdice/netdiced.py
"""

from random import randint
import re
from lib.plugin import Plugin

class DicePlugin(Plugin):
    
    def __init__(self):
        Plugin.__init__(self, 'dice')
        self._set_summary(_('Plugin for rolling various dices'))
        self._add_command('roll', '<expression>', _('makes P1tr roll one or \
more dices like specified in expression. expression should look like this: \
d6 or 2d20 or d3+7; d and the succeeding number are obligate and specify the \
dice type. The preceeding number specifies the number of rolls. You can \
append a small mathematical expression with one of the symbols +-*/. The \
results of multiple expressions get added. Limits: see "help dice limits"'))
        self._add_help_topic('limits', _('The number of rolls and the \
modification must not have more than 2 digits, number of sides is limited \
to three.'))
        self._add_command('dice', '<expression>', _('alias of roll. See \
"help dice roll" for help'))
    
    def parse_dice_string(self, string):
        rolls = []
        string = string.split()
        pattern = re.compile(r'((\d{0,2})d(\d{1,3})([\+\-\*\/]\d{1,3})?)*')
        for item in string:
            li = list(pattern.match(item).groups())
            if not li:
                rolls.append((item, 0, 0, ''))
            else:
                if li[1] == '':
                    li[1] = 1
                try:
                    rolls.append(tuple((item, int(li[2]), int(li[1]), li[3])))
                except TypeError:
                    rolls.append((item, 0, 0, ''))
        return rolls

    def roll_it(self, dice, times, mod=""):
        result_li = []
        i = 0
        result = 0
        total = 0
        while i < times:
            if mod and mod[0] in ('+', '-', '*', '/') and len(mod) < 4:
                result = eval("randint(1, dice)%s" % mod)
            else:
                mod = ""
                result = randint(1, dice)
            result_li.append(result)
            total += result
            i += 1
        return (total, result_li, mod)
    
    def roll(self, msg):
        parsed = self.parse_dice_string(msg.params)
        if not parsed:
            return _('Sorry, I can\'t roll that dice.')
        else:
            results = []
            total = 0
            for roll in parsed:
                result = [roll[0], ]
                result.extend(list(self.roll_it(roll[1], roll[2], roll[3])))
                results.append(tuple(result))
                total += result[1]
            # Check if we have a valid result
            if not results[0][1]:
                return _('Invalid roll. Mind the rules in help dice roll.')
            else:
                # Compose a good looking string for return
                string = "You rolled a total of %d. Details: " % total
                for roll in results:
                    string += "%s=%d: " % (roll[0], roll[1])
                    for dice in roll[2]:
                        string += "%d, " % dice
                    string += "mod:%s; " % roll[3]
                return string
    
    def dice(self, msg):
        """Alias for roll"""
        return self.roll(msg)