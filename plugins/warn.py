from lib.plugin import Plugin

class WarnPlugin(Plugin):
    
    def __init__(self):
        Plugin.__init__(self, 'warn')
        self._set_summary(_('Enables users with a higher level to warn other \
users in case they behave inappropriately. After being warned for three \
times, P1tr automatically kicks this user if he is op.'))
        self._add_command('warn', '<nick> <reason>', _('warns user with the \
given reason.'))
        self._add_command('criminal_record', '[<nick>]', _('if no parameters \
given, this command shows the invoker\'s own "criminal record". Users with \
higher levels can view the criminal records of other users.'))
        
        self.record = self._load_resource('criminal_record')
        # self.record dictionary structure:
        # {server_name:
        #     {channel: 
        #         {nick: {'warns': int, 'kicks': int, 'recent': str}, }, }, }
    
    def warn(self, msg):
        level = 15
        server = msg.bot.factory.connection.name
        chan = msg.chan
        if self.require_level(msg.user, level):
            params = msg.params.split()
            if len(params) == 0:
                return _('You have to name a target and a reason.')
            elif len(params) == 1:
                return _('You can\'t warn anyone without a reason.')
            else:
                reason = ' '.join(params[1:])
                # Check if the criminal_record already has entries for the
                # server and the channel
                if not server in self.record.keys():
                    self.record[server] = {}
                if not chan in self.record[server].keys():
                    self.record[server][chan] = {}
                
                # Check if this user already has a criminal record
                if not params[0] in self.record[server][chan].keys():
                    self.record[server][chan][params[0]] = {
                        'warns': 1, 'kicks': 0, 'recent': reason}
                else:
                    self.record[server][chan][params[0]]['warns'] += 1
                
                # Update recent_warn
                self.record[server][chan][params[0]]['recent'] = reason
                
                # Notify channel, that warning took place
                msg.bot.me(msg.chan, _('warns %s: %s') % (params[0], reason))
                
                # Kick user if number he has been warned three times since his
                # previous kick.
                if not self.record[server][chan][params[0]]['warns'] % 3:
                    msg.bot.msg(msg.reply_to, _('Alright, that does it. You \
are a kick-candidate, %s!' % params[0]))
                    msg.bot.kick(msg.chan, params[0], reason)
                    self.record[server][chan][params[0]]['kicks'] += 1
        else:
            return _('You are not permitted to warn other people.')
        self.record.sync()
    
    def criminal_record(self, msg):
        level = 10
        server = msg.bot.factory.connection.name
        params = msg.params.split()
        
        if len(params) == 0:
            data = self.record[server][msg.chan][msg.user.name]
            return _('You have been warned %i times, were kicked %i times, \
and your recent warning was: %s' % (data['warns'], data['kicks'],
data['recent']))
        else:
            if self.require_level(msg.user, level):
                if params[0] in self.record[server][chan].keys():
                    data = self.record[server][msg.chan][params[0]]
                    return _('%s has been warned %i times, was kicked %i \
times, and was recently warned with: %s' % (params[0], data['warns'],
data['kicks'], data['recent']))
                else:
                    return _('%s has no criminal record yet.' % params[0])
            else:
                return _('You are not permitted to view other user\'s \
criminal record.')
