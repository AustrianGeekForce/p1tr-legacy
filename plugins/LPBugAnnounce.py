"""
P1tr plugin which announces new bugs reported against particular
Launchpad projects in IRC channels.

Copyright (C) 2009 Ryan Kavanagh <ryanakca@kubuntu.org>
Copyright (C) 2009 Siegfried-Angel Gevatter <rainct@ubuntu.com>

Based upon https://launchpad.net/eeebotu, which is:
 Copyright (C) 2008 Mike Rooney <eeebotu@rowk.com>

CONFIGURATION:

Add, to the sections of your configuration file for the connections
where you want new bugs to be reported, a line like the following one:

  X-LPBugAnnounce-Report = project1:#channel1,#channel2 project2:#channel1

Where "project1" and "project2" are the names of the Launchpad projects
for which you want to report new bugs, and "#channel1" and "#channel2"
the channels where you want them to be reported. 

LICENSE:

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

import time
import re
import urllib2
import feedparser
from twisted.internet import task
from BeautifulSoup import BeautifulSoup

from lib.logger import log
from lib.plugin import Plugin
from lib.config import configuration, xdata

class LpbugannouncePlugin(Plugin):
    
    def __init__(self):
        Plugin.__init__(self, 'LPBugAnnounce')
        self._set_summary(_('Announces new bugs for a LP project'))
        self.projects = {}
        self.loop = self.warmup = None
        # Structure:
        # {project: [{connection: [channel, ...], ...}, (lastbugs)], ...}
    
    def on_connect(self, bot):
        """ Register the projects/channels for a new connection. """
        projects = xdata(bot, self.name, 'report').split()
        for project, channel_part in [p.split(':', 2) for p in projects]:
            channels = channel_part.split(',')
            if not project in self.projects:
                self.projects[project] = [{}, ()]
            self.projects[project][0][bot] = channels
        
        # If they aren't running yet, start the periodic checks
        if not self.loop:
            self.loop = task.LoopingCall(self.mainloop)
            self.loop.start(60.0) # run every 60 seconds
    
    """
    # Commented out because this is untested and currently we provide
    # no command to disconnect from a single server.
    def on_disconnect(self, bot, reason=None):
        # Delete the projects/channels for a removed connection.
        for project in self.projects.itervalues():
            project[0][:] = [p for p in project if bot not in p]
            if not project[0]: del self.projects[project]
    """
    
    def get_latest_bugs(self, project, num=5):
        """
        Get the `num' latest bugs in the defined project, as defined by
        Launchpad's atom feed.
        
        Returns a list of tuples in the form of:
            (bugNumber, bugDescription, bugUrl).
        """
        
        feed = feedparser.parse(
            'http://feeds.launchpad.net/%s/latest-bugs.atom' % project)
        
        bugs = []
        for i in xrange(num):
            entry = feed.entries[i]
            bugUrl = entry.link
            title = entry.title
            numEnd = title.find(']')
            bugNum = title[1:numEnd]
            bugDesc = title[numEnd+2:].replace('&lt;', '<').replace(
                '&gt;', '>').replace('&amp;', '&')
            html = entry.content[0].value
            
            # Attempt to grab the package, status, and importance from
            # the HTML of the feed entry
            try:
                package, status, importance = [tag.contents[0] for tag \
                    in BeautifulSoup(html).div.table.findAll('tr')[1].findAll('td')[1:4]]
            except Exception:
                package = status = importance = '???'
            
            bugs.insert(0,
                (bugNum, bugDesc, bugUrl, package, status, importance))
        
        return bugs
    
    def get_bug_location(self, bugUrl):
        """
        Get the location of a package (universe/main).
        """
        
        html = urllib2.urlopen(bugUrl).read()
        # clean up the HTML a little first... on second thought, don't bother.
        # Commenting out.
        # for char in ['\n', '\t']:
        #    html = HTML.replace(char, '')
        
        component = re.findall(', uploaded to ([a-z]+) on', html) 
        if component is None:
            component = '?'
        else:
            component = component[0]
        
        return component
    
    def mainloop(self):
        """
        This is the main loop, which checks for new bugs every minute,
        and reports any new ones to the IRC channel.
        """
        
        if not self.warmup:
            self.warmup = True
            return
        
        for project in self.projects:
            
            # Fetch new bugs
            try:
                bugs = self.get_latest_bugs(project)
            except Exception:
                log('e',
                    'Failed to fetch bugs for %s, skipping' % project)
                continue
            
            # If this is the first run for this project
            if not self.projects[project][1]:
                # Mark all recent bugs as already reported
                self.projects[project][1] = [x[0] for x in bugs]
            
            # Filter out already reported bugs
            new_bugs = [bug for bug in bugs if bug[0] not in \
                self.projects[project][1]]
            self.projects[project][1] = [x[0] for x in bugs]
            
            # Report the bugs
            for (number, desc, url, package, status, imp) in new_bugs:
                if package == 'ubuntu':
                    # Try to find the component (main/universe) of package.
                    try:
                        location = ' (%s)' % self.get_bug_location(url)
                    except Exception:
                        location = ' (?)'
                else:
                    location = ''
                
                msg = 'New bug: #%s in %s%s: "%s" [%s, %s] %s' % \
                    (number, package, location, desc, imp, status, url)
                log('i', msg)
                
                for bot, chans in self.projects[project][0].iteritems():
                    for channel in chans:
                        bot.msg(channel, str(msg))             
