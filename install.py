"""P1tr installer - usually used when no config file is found."""

import os
import shutil
import sys

def main():
    """
    Everything is contained here.
    If install.py is run standalone a new config file gets created in the
    same directory. If P1tr is run without a config file in one of the
    searched directories this function is called before P1tr startup
    continues.
    """
    print 'No config file found. Writing one.'
    print 'Checking dependencies...'
    # Dependency check imports dependent modules to check if they are here
    try:
        import twisted
    except ImportError:
        print 'FATAL: Twisted (essential) not found. Exiting.'
        sys.exit(1)
    if float(sys.version[:3]) < 2.5:
        print 'FATAL: Python 2.5 is required to run P1tr. Exiting.'
        sys.exit(1)
    print 'Dependencies fulfilled.'
    
    sequence = ['nick', 'nickpw', 'server', 'port', 'ssl', 'password',
                'host', 'channels', 'signal_char', 'language', 'superadmin']
    prompts = {'nick': 'Bot nick [P1tr]: ',
               'nickpw': 'Bot nick\'s password, if available [None]: ',
               'server': 'Server [irc.freenode.net]: ',
               'port': 'Port [6667]: ',
               'ssl': 'Use SSL; either True or False [False]: ',
               'password': 'Server password [None]: ',
               'host': 'Your hostname [localhost]: ',
               'channels': 'Channels, seperated with spaces \
[#internationalgeekforce]: ',
               'signal_char': 'Character to signalize a command [*]: ',
               'language': 'Code of the language to use [en]: ',
               'superadmin': 'The nickname of the master of P1tr [P1tr]: '}
    res = {'nick': 'P1tr', 'nickpw': 'None', 'server': 'irc.freenode.net',
           'port': '6667', 'ssl': 'False', 'password': 'false',
           'host': 'localhost', 'channels': '#internationalgeekforce',
           'signal_char:': '*', 'language': 'en', 'superadmin': 'P1tr'}
    print 'Welcome to P1tr Installer!\n \
P1tr is a great IRC bot, made by the guys of the AustrianGeekForce. Before \
you can get started, enter some information which is necessary to make P1tr \
do what YOU want.\n \
If you see square brackets next to a prompt it contains the default value. \
If you are not really sure what you should enter, just take this one by \
hitting Enter without writing anything to the prompt.\n \
If everything you entered was valid a config file will be created in the \
place you select.\n \
Alternatively to this script you can modify bot.conf.ex by hand.'
    for key in sequence:
        input = raw_input(prompts[key])
        if input:
            res[key] = input
    
    # Copy P1tr to a folder in ~ -- PREVIOUSLY DISABLED
    target = os.path.join(os.path.expanduser('~'), '.p1tr')
    try:
        shutil.copytree(os.getcwd(), target)
    except (IOError, OSError):
        print 'FATAL: Cannot create P1tr directory in your home:'
        raise
        sys.exit(1)
    os.chdir(target)
    
    # Write configuration file to this folder
    config = open('bot.conf', 'a')
    contents = """#P1tr 0.1 configuration \

[global]
language = %s
superadmin = %s

[ConnectionOne]
service = IRC
server = %s:%s
ssl = %s
password = %s
host = %s
nick = %s
nickpw = %s
channels = %s
signal = %s
""" % (res['language'], res['superadmin'], res['server'], res['port'],
       res['ssl'], res['password'], res['host'], res['nick'], res['nickpw'],
       res['channels'], res['signal_char'])
    config.write(contents)
    config.close()
    
    print 'Congratulations! P1tr is ready to go.'
    # Launch P1tr inside the new directory -- PREVIOUSLY DISABLED
    #bot.main()
    
    return 'bot.conf'

if __name__ == '__main__':
    main()
