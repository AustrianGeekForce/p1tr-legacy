"""P1tr is very grateful that I exist, because I provide the great features of
loading and handling plug-ins. For I'm very well coded P1tr is much better
than some bot with worse plug-in support, obviously."""
 
import os.path
import glob
 
from lib.logger import log
from lib.config import configuration
 
class PluginLoader:
    """ I'm responsible for loading plugins."""
    def __init__(self):
        self.plugins = []
 
    def load_plugins(self, plugin_list=None):
        """
        If no plug-ins are listed in my argument I load all plug-ins in the
        plugin directory.
        """
 
        if plugin_list:
            names = plugin_list
        else:
            names = [os.path.split(file)[1] for file in glob.glob(
                os.path.join('plugins', '*.py'))]
        
        for ignore in ('__init__.py',):
            if ignore in names:
                names.remove(ignore)
        
        for blacklisted in configuration.plugins_blacklist:
            blacklisted_name = blacklisted + '.py'
            if blacklisted_name in names:
                log('i', 'Ignored blacklisted plugin "%s".' % blacklisted_name)
                names.remove(blacklisted_name)
        
        for name in names:
            mod_name = name.split('.')[0]
            try:
                module = __import__('plugins.' + mod_name)
                self.plugins.append(getattr(getattr(module, mod_name),
                                        mod_name.capitalize() + 'Plugin')())
                log('i', 'Loaded plugin "%s".' % name)
            except ImportError:
                log('e', 'Invalid plugin specified.')
                raise
            except:
                raise
 
        return self.plugins
 
class PluginHandler:
    """I make it possible to handle plug-ins, in particular register()
    and handle()."""
    def __init__(self, plugins):
        self.help_topics = {}
        self.plugins = {}
        self.listeners = []
        for plugin in plugins:
            self.register(plugin)
 
    def register(self, plugin):
        """I let users register a password associated with their nickname."""
        self.plugins[plugin.name] = plugin
        for keyword in plugin.keywords:
            self.plugins[keyword] = plugin
        if hasattr(plugin, '_listen_'):
            self.listeners.append(plugin)
        self.help_topics[plugin.name] = plugin.get_help_topics()
 
    def handle(self, msg):
        """I get the correct plugin for a keyword and call the right method."""
        if msg.chan == msg.bot.nickname:
            msg.reply_to = msg.user.name
        else:
            msg.reply_to = msg.chan
        if msg.keyword in self.plugins:
            answer = self.plugins[msg.keyword].privmsg(msg)
            self._reply(msg, answer)
        elif msg.keyword == 'help':
            args = [x for x in msg.params.split(' ') if x]
            if len(args) > 0 and args[0] in self.help_topics:
                plugin = args[0]
                if len(args) > 1:
                    if args[1] in self.help_topics[plugin]:
                        self._reply(msg, self.plugins[plugin].help(args[1]))
                else:
                    self._reply(msg, self.plugins[plugin].help())
            else:
                self._reply(msg, _('Help topics: ')
                         + ', '.join(self.help_topics.keys()))
        for listener in self.listeners:
            answer = listener._listen_(msg)
            self._reply(msg, answer)
 
    def _reply(self, msg, answer):
        if answer:
            msg.bot.msg(msg.reply_to, answer)
