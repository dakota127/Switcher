#!/usr/bin/python

"""
    example.py

    Python Daemon example. Creates a simple web sever and runs as a daemon
    
    Usage:
        1. Run from a terminal / command line: "python example.py start".
        2. Notice that the terminal is available immediately after the app has been daemonized.
        3. From the terminal run "python example.py status". The PID of the daemonized process should be displayed.
        4. Open a browser (on the same computer if the IP is localhost) and go to http://127.0.0.1:8001 (or your defeinfe IP adddress and Port).
        5. Answer the important question post on the simple website.
        6. From the terminal run "python example.py stop". The daemon should now be stopped.
        7. From the terminal run "python example.py status". The staus should show that the daemon is not running.
    
    Requires:
        Python 2.x
        BaseHHTPServer, SimpleHTTPServer modules from the Python standard library

    v 1.0
    23 Jan 2013
"""

# Configuration
# Full path names are required because the daemon has no knowledge of the current directory/folder
SETTINGS_LINUX = {
    'APP' :     'swdaemon',
    'WWW' :     '/home/pi/switcher/example.html',
    'PIDFILE' : '/home/pi/switcher/swdaem.pid',
    'LOG' :     '/home/pi/switcher/swdaem.log'
}

SETTINGS_OTHER = {
    # Other Operating Systems/Platforms
    'APP' :     'mydaemon_example',
    'WWW' :     'index.html',
    'PIDFILE' : 'mydaemon_example.pid',
    'LOG' :     'mydaemon_example.log'}

# Std Python Modules
import sys, types, os, platform
from time import sleep


# App modules
from daemon import DaemonClass

import switcher
import defglobal

# Globals for this module
__version__ = '1.0'
# a=0

def waiting():
    for i in range(40):
        sys.stdout.write(str(i))
        sys.stdout.write('sleeping...\n')
        sleep(1)
        defglobal.work=1

class MyApp(DaemonClass):
    """
        Subclasses the Daemon Class from the daemon module.
        Overrides relevant methods.
        Configures a basic web server.
    """
    a=1
    def __init__(self, settings):
        # Initialise the parent class
        DaemonClass.__init__(self, settings)
        self.html = ""
	
    def before_start(self):
        sys.stdout.write("Config tasks go here")
  
    
    def on_exit(self):
        sys.stdout.write("Cleanup tasks go here")
    
    def run(self):
        """
            Runs after the process has been demonised.
            Overrides the run method provided by the class (which does nothing much anyway).
            When this method exits, the application exits.
        """
        sys.stdout.write("(pid:%s) Running MainLoop...\n" % self.pid)
        self.signaltrapped = False
#----------------------

        ret=switcher.initswitcher()  # init stuff
        if ret != 9:
            switcher.runswitch()         #  here is the beef, runs forever
        switcher.terminate()         #  Abschlussvearbeitung    
#

#-----------------------				

        sys.stdout.write('...Shutting down the daemon.\n')

        # Final tidy up - delete PID file etc
        self.on_exit()
        self.cleanup()
        sys.stdout.write("All Done.")
        # The daemon will close down now

    def on_interrupt(self):
        """
            Quit gracefully
        """

        sys.stdout.write("Interrupt received, so quitting gracefully...\n")
        defglobal.work=0  # signal for end
        defglobal.term=1  # signal for end

#        sys.stdout.write(str(define_a.a))
#
#
#
#   Main starts here
#        
if __name__ == '__main__':
    global app

    if platform.system() == 'Linux':
        SETTINGS = SETTINGS_LINUX
    elif platform.system() == 'Windows':
        SETTINGS = SETTINGS_WINDOWS
    else:
        SETTINGS = SETTINGS_OTHER

    print "----- %s (Release: %s) -----" % (SETTINGS['APP'], __version__)   # print signatur

    if len(sys.argv) == 2:
        if 'start' == sys.argv[1]:
            sys.stdout.write("Starting the switcher app...\n")
            app = MyApp(SETTINGS)
            sys.stdout.write("Starting daemon mode...")
            app.start()
        elif 'stop' == sys.argv[1]:
            app = MyApp(SETTINGS)
            sys.stdout.write("Stopping the daemon...\n")
            app.stop()
        elif 'restart' == sys.argv[1]:
            app = MyApp(SETTINGS)
            sys.stdout.write("Restarting the daemon...")
            app.restart()
        elif 'status' == sys.argv[1]:
            app = MyApp(SETTINGS)
            sys.stdout.write("Status Request...\n")
            app.status()
        elif 'fore' == sys.argv[1]:
            app = MyApp(SETTINGS)
            app.run()
        else:
            print "usage: %s start|stop|restart/status" % sys.argv[0]
            sys.exit(2)
    else:
            print "Invalid command: %r" % ' '.join(sys.argv)
            print "usage: %s start|stop|restart|status" % sys.argv[0]
            sys.exit(2)

    print "...Done"

# end of module
