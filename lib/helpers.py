"""I help P1tr wherever I can."""

import re
import gettext

from lib.logger import log
from lib.config import configuration

def parse_args(arg_list):
    """
    I put command line args and their proper values together in a 
    dictionaryionary and check, if the value is valid.
    """
    dictionary = {}
    for item in arg_list:
        common_pattern = re.compile(r'^(-pn|-s|-po|-pw|-n|-npw|-ho)$')
        common_pattern = common_pattern.search(item)
        if common_pattern:
            try:
                value = arg_list[arg_list.index(item)+1]
                dictionary[common_pattern.groups()[0]] = value
            except (KeyError, IndexError):
                log('e', 'Invalid command line argument.')
        
        help_pattern = re.compile(r'^(-h)$').search(item)
        if help_pattern:
            dictionary['-h'] = True
        else:
            dictionary['-h'] = False
        
        conf_pattern = re.compile(r'^(-cnf)$').search(item)
        if conf_pattern:
            try:
                value = arg_list[arg_list.index(item)+1]
                dictionary[common_pattern.groups()[0]] = value
            except (KeyError, IndexError):
                log('e', 'Invalid command line argument.')
        else:
            dictionary['-cnf'] = False
    return dictionary

def complete_args_dict(args):
    """
    Compatibility function; adds all missing values to the command line
    arguments dictionaryionary.
    """
    arg_list = ['-cnf', '-s', '-ho', '-n', '-po', '-ssl', '-pw', '-npw']
    defaults = {'-cnf': False, '-s': None, '-ho': 'localhost', '-n': 'P1tr',
                '-po': 6667, '-ssl': False, '-pw': None, '-npw': None}
    for item in arg_list:
        try:
            args[item]
        except KeyError:
            args[item] = defaults[item]
        return args

def load_language(lcode=None):
    """
    Installs language lcode; if not given the language from the configuration
    file will be installed. Useful for language changes at runtime.
    Returns a tuple; first item is the new language; second item is a arg_list of
    all available languages.
    """
    langs = {}
    for language in ['ca', 'da', 'de', 'en', 'es', 'fr', 'hi', 'la',
                    'ru', 'sv', 'tr']:
        langs[language] = gettext.translation('p1tr', './locale',
            languages=[language])
    if lcode:
        log('i', 'Lang "%s" loaded.' % lcode)
        langs[lcode].install()
    else:
        conf_lang = configuration.language
        log('i', 'Loaded language "%s" (specified in the config file).' % \
        conf_lang)
        langs[conf_lang].install()
    return (lcode or conf_lang, langs.keys())

def time_ago_in_words(delta):
    """
    I convert a the difference in time for a numeric to a textual
    representation. Takes a datetime type object as argument.
    """
    days = delta.days
    minutes = delta.seconds / 60
    seconds = delta.seconds - minutes * 60
    hours = minutes / 60
    minutes = minutes - hours * 60

    days = get_time_part(days, _('days'))
    hours = get_time_part(hours, _('hours'))
    minutes = get_time_part(minutes, _('minutes'))
    seconds = get_time_part(seconds, _('seconds'))

    return _('%s %s %s %s' % (days, hours, minutes, seconds)).strip()
    
def get_time_part(val, unit):
    if val:
        return str(val) + ' ' + unit
    else:
        return ''
