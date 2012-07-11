#!/usr/bin/env python3

import sys
from oyoyo.client import IRCClient
from oyoyo.cmdhandler import DefaultCommandHandler
from oyoyo import helpers

class MyHandler(DefaultCommandHandler):
    def privmsg(self, nick, chan, msg):
        print("%s in %s said: %s" % (nick, chan, msg))


def on_connect(client):
    helpers.join(client, '#p1tr-test')

def main():
    client = IRCClient(MyHandler, host='irc.freenode.net', port=6667, nick='p1tr-test', connect_cb=on_connect)
    connection = client.connect()
    while True:
        try:
            next(connection) 
        except KeyboardInterrupt:
            break



if __name__ == '__main__':
    main()
