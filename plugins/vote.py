"""
Plugin for votations.
"""

from lib.plugin import Plugin

class VotePlugin(Plugin):
    
    def __init__(self):
        
        Plugin.__init__(self, 'vote')
        self._set_summary(_('Plugin for votations'))
        self._add_command('vote', None, _('starts a vote.'))
        self._add_command('endvote', None, _('ends a running votation.'))
        
        self._listen = False
        self._votings = {}
    
    def _ensure_channel(self, msg):
        if msg.chan == msg.bot.nickname:
            msg.bot.msg(msg.reply_to,
                msg.prefix + _('This plugin can only be used in channels.'))
    
    def _has_voting(self, msg):
        return id(msg.bot) in self._votings and \
            msg.chan in self._votings[id(msg.bot)]
    
    def _get_voting(self, msg):
        return self._votings[id(msg.bot)][msg.chan]
    
    def vote(self, msg):
        
        self._ensure_channel(msg)
        if self._has_voting(msg):
            return _('There is already a running voting...')
        else:
            if not id(msg.bot) in self._votings:
                self._votings[id(msg.bot)] = {}
            self._votings[id(msg.bot)][msg.chan] = Voting()
            return _('The voting starts... now!')
    
    def endvote(self, msg):
        
        self._ensure_channel(msg)
        if not self._has_voting(msg):
            return msg.prefix + _('There is no running voting...')
        
        voting = self._get_voting(msg)
        result = _('The voting has ended with %d positive vote(s), %d negative \
vote(s) and %d abstain(s). %d people have participated.') % voting.get_stats()
        del(self._votings[id(msg.bot)][msg.chan])
        
        return result
    
    def _listen_(self, msg):
        
        if msg.chan == msg.bot.nickname or not self._has_voting(msg):
            return False
        
        message = msg.msg.strip() + ' '
        for element in (msg.bot.nickname, ':', ',', ';'):
            message = message.replace(element, '')
        
        if message.startswith('+1 '):
            self._add_vote(0, msg)
        elif message.startswith('-1 '):
            self._add_vote(1, msg)
        elif message[0:3] in ('+0 ', '-0 '):
            self._add_vote(2, msg)
    
    def _add_vote(self, vote, msg):
        
        voting = self._get_voting(msg)
        
        if voting.user_has_voted(msg.user.name):
            msg.bot.msg(msg.chan, msg.prefix + 
                        _('You have already voted once.'))
        else:
            voting.add(msg.user.name, vote)
            msg.bot.msg(msg.chan, msg.prefix + _('Vote recorded. There \
are %d positive vote(s), %d negative vote(s) and %d abstain(s) so far.'
) % voting.get_stats()[:3])

class Voting:
    
    def __init__(self):
        
        self._listen = True
        self._votes = [0, 0, 0]
        self._users = []
    
    def add(self, user, vote):
        if user in self._users:
            raise AssertionError, 'The user has already voted once.'
        else:
            self._votes[vote] += 1
            self._users.append(user)
    
    def user_has_voted(self, user):
        return user in self._users
    
    def get_stats(self):
        return tuple(self._votes) + (len(self._users),)
