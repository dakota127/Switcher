#!/usr/bin/python
# coding: utf-8
#
#
#
#       TestProgramm zum Schalten des Handsenders ELRO
#
#

# import Libraries
import time
import RPi.GPIO as GPIO
import sys

#define settings
waittime =1.0

# define GPIO signals to use
# and the mapping to signals -D and On/Off
Pins={'A': 14, 'B':15,'C':18,'D':25,'ON':24,'OFF':23}


# Switches "switch" to ON or OFF state
#Paramaters are: "switch" (A,B,C,D) and "state" (ON,OFF)

# --- Function setSwitch ----------------
def setSwitch(switch, state):
		GPIO.output(Pins[switch], True)
		GPIO.output(Pins[state], True)
		time.sleep(waittime)
		GPIO.output(Pins[switch], False)
		GPIO.output(Pins[state], False)
--------------------------------------		


# ***** Function zum Setzen der benoetigten GPIO Pins **********
def setpins(how):
    global GPIO
    if how:
# set all needed pins as output
        for pin in Pins:
            GPIO.setup(Pins[pin], GPIO.OUT)
            GPIO.output(Pins[pin], False)
    else:
# cleanup alle benötigten Pins - und nur diese!!
        for pins in Pins:
            GPIO.cleanup(Pins[pins])  # cleanup GPIO Pins
# *************************************************** 
			


# -------- Main starts here --------------------

if __name__ == '__main__':

#Use BCM GPIO refernece instead of Pin numbers
    GPIO.setmode (GPIO.BCM)
    rev=GPIO.RPI_REVISION
    print "Rasperry Version: ", rev	
    if rev==1:
	    print "GPIO-Version 1 has different port numbering - please check program !"
	    print "Program was developed for Rev2 and later."

    setpins(1)

    for i in range(3):
# posit: solange, falls kein Ctlr-C kommt
	    try:
		    setSwitch('A','ON')
		    time.sleep(2)
		    setSwitch('A','OFF')
		    setSwitch('B','ON')
		    time.sleep(2)
		    setSwitch('B','OFF')
		    time.sleep(1)

	    except KeyboardInterrupt:
	# cleanup
		    print "Keyboard Interrupt, alle Dosen OFF und clean up pins"
		    setSwitch('A','OFF')
		    setSwitch('B','OFF')
		    setSwitch('C','OFF')
		    setSwitch('D','OFF')
		    setpins(0)  # set GPIO Pins zum Senden
		    sys.exit(2)

# end loop, terminate
    setpins(0)

    sys.exit(2)

	