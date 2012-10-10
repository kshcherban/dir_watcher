#!/usr/bin/env python
#
#  directory_watcher.py
#
#  Copyright 2012 Konstantin Shcherban <k.scherban@gmail.com>
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#

# All stuff will be done by pyinotify
import os
import sys
import time
import optparse
import pyinotify
import subprocess

path = '/home/insider/Downloads/test'

# Function to become a daemon
def daemonize(logfile):
    if os.fork():
      os._exit(0)
    os.setsid()
    pid = os.getpid()
    print 'To kill daemon run:'
    print 'kill', pid
    # Pidfile, should be implemented in future
    # pidfile = open('/tmp/dir_watcher.pid', 'a')
    #sys.stdout = open('/dev/null', 'a')
    #sys.stderr = open('/dev/null', 'a')

# Handling files modifications class
class OnModifyHandler(pyinotify.ProcessEvent):

    def my_init(self, start_time, cmd, sync_time, cwd, logfile):
        self.last_change = start_time
        self.count = 0
        self.host_name = os.uname()[1]
        self.pid = os.getpid()
        self.cmd = cmd
        self.sync_time = sync_time
        self.cwd = cwd
        self.logfile = logfile

    # Watch for modification periods
    # If last modification was done more than n minutes ago then run command
    # Also run command after first modification
    def timer(self, seconds):
        logformtime = time.strftime("%b  %d %H:%M:%S")
        if self.logfile != sys.stdout:
            f = open(self.logfile, 'a')
        else:
            f = self.logfile
        if self.count == 0:
            f.write('%s %s dir_watcher[%s]: Executing %s\n' % (logformtime,\
        self.host_name, self.pid, self.cmd))
            subprocess.call(self.cmd.split(), cwd=self.cwd)
            self.count = 1
        else:
            if (seconds - self.last_change) >= self.sync_time:
                subprocess.call(self.cmd.split(), cwd=self.cwd)
                f.write('%s %s dir_watcher[%s]: Executing %s\n' % (logformtime,\
        self.host_name, self.pid, self.cmd))
            self.last_change = seconds
        if self.logfile != sys.stdout:
            f.close()

    # Function to write logs
    def post_inotify(self, mod, pathname):
        logformtime = time.strftime("%b  %d %H:%M:%S")
        if self.logfile != sys.stdout:
            f = open(self.logfile, 'a')
        else:
            f = self.logfile
        f.write('%s %s dir_watcher[%s]: %s %s\n' % (logformtime,\
        self.host_name, self.pid, mod, pathname))
        if self.logfile != sys.stdout:
            f.close()

    # Inotify watchers
    def process_CLOSE_WRITE(self, event):
        self.timer(time.time())
        self.post_inotify('Written', event.pathname)

    def process_IN_CREATE(self, event):
        self.timer(time.time())
        self.post_inotify('Created', event.pathname)

    def process_IN_DELETE(self, event):
        self.timer(time.time())
        self.post_inotify('Deleted', event.pathname)

    def process_IN_MODIFY(self, event):
        self.timer(time.time())
        self.post_inotify('Modified', event.pathname)


if __name__ == '__main__':
    # Command line options definition
    parser = optparse.OptionParser("usage: %prog [options]")
    parser.add_option("-d", "--directory", dest="directory", \
    help="directory/file to watch changes")
    parser.add_option("-e", "--execute", dest="execute", \
    help="command to execute after changes")
    parser.add_option("-o", "--output", dest="logfile", \
    help="log file location [optional]")
    parser.add_option("-t", "--time", dest="synctime", \
    help="execution frequency in seconds after last change [optional]")
    (options, args) = parser.parse_args()
    if options.directory is None:
        parser.error('Please specify directory or file to watch changes')
    if options.execute is None:
        parser.error('Please specify command to execute after changes found')
    # Default schedule frequency is 3min
    if options.synctime is None:
        options.synctime = 180
    # If output file is not set we redirect log messages to stdout
    if options.logfile is None:
        options.logfile = sys.stdout
    # Adding mask for all file modifications
    mask = pyinotify.ALL_EVENTS
    wm = pyinotify.WatchManager()
    handler = OnModifyHandler(start_time = time.time(), cmd = options.execute,\
    sync_time = options.synctime, cwd = options.directory, logfile = options.logfile)
    notifier = pyinotify.Notifier(wm, default_proc_fun=handler)
    wm.add_watch(options.directory, mask)
    #daemonize(options.logfile)
    notifier.loop()
