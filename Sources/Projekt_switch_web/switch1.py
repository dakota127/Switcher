#!/usr/bin/env python
# coding: utf-8
#
#
#       TestProgramm zum Schalten des Handsenders ELRO
#       Commandline Parms   -D Dosennummer (A, B C oder D)
#                           -A Aktion On oder OFF
#                           -d debug
#                           -s Status aus File anzeigen

# import Libraries
import time
import RPi.GPIO as GPIO
import sys, os, platform, getopt

#define settings
waittime =1.0
debug=0
dose=""
onoff=""
swfile="swstatus.txt"
stat=0

# define GPIO signals to use
# and the mapping to signals -D and On/Off
Pins={'A': 4, 'B':22,'C':18,'D':25,'ON':24,'OFF':23}
Dose={'A': 1, 'B': 2,'C': 3,'D': 4}
State={'ON': "1", 'OFF': "0"}


# ***** Function Parse commandline arguments ***********************
# get and parse commandline args

def arguments(argv):
    global debug
    global dose
    global onoff, status, stat
    back=list()
    try:
        opts, args=getopt.getopt(argv,"hdsD:A:")
    except getopt.GetoptError:
        print ("Parameter Error")
        sys.exit(2)
    for opt, arg in opts:
        if opt in ("-h", "--help"):
            print ("App Settings -----------")
            print ("usage: switch1.py [-d -h -D dose -A on-off]")
            sys.exit(2)
        elif opt == '-d': 	debug = 1       # debug
        elif opt == "-D":	dose = arg      # Dose A bis D
        elif opt == "-A":	onoff = arg     # ON oder OFF
        elif opt == "-s":   stat=1          # nur Statusmeldung aus File gewünscht

    if stat: return(0)
    if len(dose) == 0:
        return(9)
  
    if len (onoff) == 0:
        onoff="ON" # defaultwrt 

# ***********************************************




# --- Function setSwitch ----------------
#   Switches "switch" to ON or OFF state
#   Paramaters are: "switch" (A,B,C,D) and "state" (ON,OFF)
#
def setSwitch(switch, state):
    if debug: 
        print "SetSwitch %s, %s" % (switch, state)
#       starte senden, wir senden während waittime (sekunden)
	GPIO.output(Pins[switch], True)
	GPIO.output(Pins[state], True)
	time.sleep(waittime)
#       senden wieder beenden		
	GPIO.output(Pins[switch], False)
	GPIO.output(Pins[state], False)
#--------------------------------------		

# --- Function setFile ----------------
#   Read und write back 4 Bytes des Statusfiles
#   Byte0: represent Dose A
#   Byte1: represent Dose B
#   usw
#   File wird angelegt, wenn er nicht existiert
#
def setFile(switch, state, swfile):
    if os.path.exists(swfile):       # check ob file vorhanden ist im current dir
      pass
    else:
        file = open(swfile, 'w') 
        file.write("0000\n")
        file.close()    
        if debug: print ("swfile %s erstellt" % swfile)	# file not found
     
#   status file gefunden 
    file = open(swfile, 'r+')
    status=file.readline()
    if debug: print "Statusfile alt %s" % status
#  entsprechende Position im String auf 1 resp. 0 setzen
    status=status[:Dose[switch]-1] + State[state] + status[Dose[switch]:]
    if debug: print "Statusfile neu %s" % status
    position = file.seek(0, 0);
    file.write(status + "\n")
    file.close()
    return(0)
#---------------------------------------------------

# --- Function statFile ----------------
#   Read Status aus File

def statFile(swfile):
    if not os.path.exists(swfile):       # check ob file vorhanden ist im current dir
      return (9)
     
#   status file gefunden 
    file = open(swfile, 'r')
    status=file.readline()
    if debug: print "Statusfile read  %s" % status
    file.close()
    return(status)
#---------------------------------------------------

# ***** Function zum Setzen der benoetigten GPIO Pins **********
def setpins(how):
    global GPIO
    if how:
# set all needed pins as output
        for pin in Pins:
            if debug: print Pins[pin]
            GPIO.setup(Pins[pin], GPIO.OUT)
            GPIO.output(Pins[pin], False)
    else:
# cleanup alle benötigten Pins - und nur diese!!
        for pin in Pins:
            if debug: print Pins[pin]
            GPIO.cleanup(Pins[pin])  # cleanup GPIO Pins
# *************************************************** 

# ***** Function lampen schalten im Loop **********
def fire():
    for i in range(3):
# posit: solange, falls kein Ctlr-C kommt
		setSwitch('A','ON')
		time.sleep(2)
		setSwitch('A','OFF')
		setSwitch('B','ON')
		time.sleep(2)
		setSwitch('B','OFF')
		time.sleep(1)

# end loop, terminate
#---------------------------------------------------			



# -------- Main starts here --------------------

if __name__ == '__main__':
    ret=arguments(sys.argv[1:])  # get commandline arguments
    if ret==9:
        print "Commandline Fehler"
        sys.exit(2) 
#  get path of appfile    
    full_path = os.path.realpath(__file__)
#  get directory of file
    dirname=os.path.dirname(full_path)
    if debug: print("this file's directory: %s" % dirname)
    
#  commandline Parm -s verlangt nur Status aus File, keine GPIO Aktivität
    if stat:
        status=statFile(swfile)
        sys.exit(status)    
#   nun andere Funktionen mit GPIO        
#Use BCM GPIO refernece instead of Pin numbers
    GPIO.setmode (GPIO.BCM)
    rev=GPIO.RPI_REVISION
    if debug:  
        print "Rasperry Version: ", rev	
        print "Schalten  Dose: %s  Aktion: %s" % (dose,onoff) 
    setpins(1)
    setSwitch(dose,onoff)
    setFile(dose,onoff, swfile)
    setpins(0)
    sys.exit(2)
#
#
#  Ende gut Alles gut
#