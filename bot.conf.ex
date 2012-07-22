# Configuration File for P1tr

[global]
language = en
superadmin = your_nick
plugins_blacklist =

######################################################################

# CONNECTIONS
#
# A single instance of P1tr can connect to several servers and use a
# different nickname on each of those (or even connect multiple times
# to the same server, but with different nicknames). If you want to
# use more than one connection, create different sections and
# define all the configuration options described below in each of those.
#
# A section looks just like this:
#  [ConnectionName]

# SERVICE (PROTOCOL)
#
# In the future, P1tr will be able to connect to different types of
# services (like IRC, Jabber, MSN, etc).
#
# However, at the moment only the Internet Relay Chat (IRC) protocol
# is supported, so simply write this (or omit the option entirely):
#  service = IRC

# SERVER AND PORT
#
# Of course you also have to specify the server to which you want to
# connect to. This is done with the server option, which takes the
# form "example.com" or "subdomain.example.com".
#
# If you want P1tr to connect to a special port, add the port number to
# the domain name separated by a colon; eg, "example.com:1234". The
# default value is 6667.
#
# For example:
#  server = irc.freenode.net:8001

# SSL
#
# If you want P1tr to use SSL to connect, set the ssl option as true;
# else, just omit it.
#
# Most likely omitting this should work, but if you do want SSL, use:
#  ssl = True

# SERVER PASSWORD
#
# If the server requires a password to connect to it, specify it
# using the password option. This is, however, a rather uncommon
# thing and you probably won't need it; but if you need it, just
# set it like this:
#  password = keepmesecret

# NICKSERV PASSWORD
#
# If you connect to a server which uses the NickServ service (like Freenode),
# and you registered the username of your bot with it, you can use the following
# line to let the both authenticate with it:
#   X-NickServ-Password = keepmesecret

# HOST
#
# This is just used for authentication. It might be displayed if
# someone whoises the bot, or it might not.
#
# The default value is:
#  host = localhost

# NICK
#
# You need to choose a nickname, of course! Like with all other
# options, setting one is easy:
#  nick = p1tr

# NAME
#
# Although it's not really necessary, if you want your bot to have a
# nice \whois message you will probably be looking for this:
#  realname = Mr. Bot

# IDENTIFICATION
#
# If you have registered the nickname which you want the bot to
# use, you'll need to tell p1tr what the password is. This is done
# with the nickpw option.
#
# If the nickname isn't registered just omit this.
#
# An example can't hurt:
#  nickpw = keepmesecret

# CHANNELS
#
# And, you guess what? You also need to specify to which channel(s)
# P1tr should connect, and this is done with the channels option.
#
# If you want it to be in more than one channel for this connection,
# just list all the names separated by a space.
#
# Here's an example:
#  channels = #austriangeekforce #bots #example

# SIGNAL CHARACTER
#
# P1tr needs some way to recognize when you are talking with him and
# when not. You can just start all your orders to the bot saying its
# name, but as this might be a bit unconvenient here you can also
# choose a character (or, if you prefer, a word) which, prepended to
# any of the commands it knows, will let him recognize it. This
# character is choosen using the signal_char option.
#
# Common choices for this are symbols like "!", "@", "+", etc., but
# it's better to get creative and choose something more original to
# avoid clashes with other bots which might be in some of the same
# channels.
#
# As you might have expected, here is an example:
#  signal = *

# Here's a full example:

[ConnectionOne]
service = IRC
server = irc.freenode.net:6667
host = localhost
nick = p1tr
realname = Mr. Bot
channels = #agftestchan
signal = *
