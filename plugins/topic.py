"""Various topic modification functions."""

from lib.logger import log
from lib.plugin import Plugin

class TopicPlugin(Plugin):
    
    
    def __init__(self):
        Plugin.__init__(self, 'topic')
        self._set_summary(_('Various functions for topic modification.'))
        self._add_command('topic', '<action> <text>', _('Performs action. \
Some actions require text as argument. See help topic actions.'))
        self._add_help_topic('actions', _('set <channel> <text>: sets topic \
to text; add <channel> <text>: appends text to topic; remove <channel> \
<index>: if no integer is given for index, the last item of the topic is \
being deleted, otherwise the "indexth" part of it; save <channel>: saves the \
current state of the topic; restore <channel>: restores a previously saved \
state of the topic; seperator <text>: sets text as seperator of the topic \
parts.'))
        self.resource = self._load_resource('topics')
        # self.resource dictionary structure:
        # {'_seperator': 'string', '#channel': ['part', 'part', 'part'], }
        # self.resource['#channel'] items represent the parts of a topic, 
        # seperated by self.resource['_seperator'].
        if not self.resource:
            self.resource['_seperator'] = '::'
            self.resource.sync()
        self.sep = ' %s ' % self.resource['_seperator']
    
    def topic_updated(self, bot, user, chan, data):
        if not user == bot.nickname:
            self.resource[chan] = data.split(self.sep)
            self.resource.sync()
    
    def topic(self, msg):
        """Dispatches actions and checks permissions."""
        levels = {'set': 10, 'add':10, 'remove': 10, 'save': 15, 
                'restore': 15, 'seperator': 25}
        params = msg.params.split()
        if len(params) > 0 and params[0] in levels.keys():
            if self.require_level(msg.user, levels[params[0]]):
                return getattr(self, '_' + params[0])(msg)
            else:
                return _('Unauthorized. Level %s required.' %
                                                levels[params[0]])
        else:
            return _('You invoked this action incorrectly.')
    
    def _set(self, msg):
        """Overwrites the entire topic"""
        tup = self._check_if_channel_given(msg)
        topic = tup[0]
        channel = tup[1]
        self.resource[channel] = topic.split(self.sep)
        self.resource.sync()
        msg.bot.topic(channel, topic)
    
    def _add(self, msg):
        """Appends an item to the current topic."""
        tup = self._check_if_channel_given(msg)
        part = tup[0]
        channel = tup[1]
        try:
            self.resource[channel].append(part)
        except KeyError:
            self.resource[channel] = [part, ]
        self.resource.sync()
        msg.bot.topic(channel, self.sep.join(self.resource[channel]))
    
    def _remove(self, msg):
        """Removes a given or the last part of the topic."""
        tup = self._check_if_channel_given(msg)
        channel = tup[1]
        length = len(self.resource[channel])
        try:
            index = int(tup[0].split()[0])
        except (ValueError, IndexError):
            index = length - 1
        if index <= length:
            del self.resource[channel][index]
            self.resource.sync()
            msg.bot.topic(channel, self.sep.join(self.resource[channel]))
        else:
            return _('Given index out of range. It must be lower than %s.' % length + 1)
    
    def _save(self, msg):
        """Backs up the certain state of a topic for later restoring."""
        channel = self._check_if_channel_given(msg)[1]
        self.resource[channel + '#save'] = self.resource[channel]
        self.resource.sync()
        return _('Memorized.')
    
    def _restore(self, msg):
        """Changes the current topic of a channel to the saved topic."""
        channel = self._check_if_channel_given(msg)[1]
        self.resource[channel] = self.resource[channel + '#save']
        self.resource.sync()
        msg.bot.topic(channel, self.sep.join(self.resource[channel]))
    
    def _seperator(self, msg):
        """Sets a new seperator for the parts of a topic."""
        params = msg.params.split()
        if len(params) > 1:
            self.resource['_seperator'] = params [1]
            self.sep = ' %s ' % params[1]
            self.resource.sync()
            return _('Topic seperator set to' + self.sep)
        else:
            return _('It seems you forgot something, did you?')
    
    def _check_if_channel_given(self, msg):
        """
        Takes all parameters of an action and finds out, if it contains a
        channel at the beginning, which is being returned as last element in 
        a tuple - the first is the rest of the params as one string. If this 
        is not given, the current channel is being returned.
        """
        params = msg.params.split()[1:]
        if len(params) > 0:
            if params[0][0] == '#':
                # Returns first parameter if it has # at the beginning and is 
                # therefore a channel name.
                return (' '.join(params[1:]), params[0])
            else:
                return (' '.join(params), msg.chan)
        else:
            return ('', msg.chan)