"""
Plugin base class and related utilities.
"""

def load_by_name(plugin_name):
    """
    Attempts to load a plugin. The steps for that are as follows:
    1. Search for a directory named the all-lowercase version of plugin_name.
       The search order is:
        - Current working directory
        - P1tr home (as specified in config file)
        - P1tr install location
       In all locations mentioned above, a "plugin" sub-directory is searched
       for a directory with the fitting name.
    2. If the directory was found, read the .py file with the same name and
       instantiate the class with the capitalized version of plugin_name, which
       should be defined in the file.
    3. The resulting object is checked, whether its class is derived from 
       Plugin.
    4. The instance of the plugin is returned.
    If any step fails, a PluginError exception is thrown.
    """
    pass

class PluginError(Exception):
    """
    Thrown when plugin loading fails.
    """

class Plugin:
    """
    Base class of all plugins.

    Inheriting from this class is necessary in order to create a working plugin.
    Consider this class abstract - do not instantiate!
    You may give your plugin functionality by overriding the following methods:
    [TBD]
    """
    
    """ Persistent key-value storage. """
    _storage = dict();
    """ Plugin-specific settings; meant to be accessible to the plugin container. """
    settings = dict();

    def __init__(self):
        """
        Always call this constructor first thing in your plugin's constructor.
        """
        # TODO: load settings and persistend storage
