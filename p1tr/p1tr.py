#!/usr/bin/env python3

import sys
from oyoyo.client import IRCClient
from oyoyo.cmdhandler import DefaultCommandHandler


class MyHandler(DefaultCommandHandler):
    def privmsg(self, nick, chan, msg):
        print("%s in %s said: %s" % (nick, chan, msg))


def main():
    print(sys.args)
    client = IRCClient(MyHandler, host='irc.freenode.net', port=6667, nick='p1tr-test')
