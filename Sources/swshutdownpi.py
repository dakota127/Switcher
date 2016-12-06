#!/usr/bin/python
# coding: utf-8
#------------------------------------------
# Pi  Soft Shutdown Script
# Version 1.1
# Nathan Bookham 2013

# Shutdown Pi --------------------
#   Projekt Switcher
#   angepasst by Peter Boxler
#
# --------------------------------------------
# Import the modules to send commands to the system and access GPIO pins
from subprocess import call
import RPi.GPIO as GPIO

from time import sleep

# Define variables to store the pin numbers

soft_shutdown_pin = 27 # Default pin for Pi Supply is 27
led_shutdown_pin = 9 # Default pin for LED
#
var=1


# -----------------------------------------------------------------
# Define a function to run when an interrupt is called
def shutdown():
#    call(['shutdown', '-hP','+0.5'], shell=False)
    sleep(4)        # zeit geben den prozessen
    call('halt', shell=False)   # halt the Linux System

# Function blink_led() ----------------------------------------
def blink_led():  # blink led 3 mal bei start und bei shutdown
        for i in range(3):
            GPIO.output(led_shutdown_pin, True)
            sleep(0.3)
            GPIO.output(led_shutdown_pin, False)
            sleep(0.2)
    
# Callback -----------------------------------------------------
def my_callback(channel):
    print "Pin Falling: %d" % channel
    sleep(1)  # confirm the movement by waiting 1 sec 
    if not GPIO.input(soft_shutdown_pin): # and check again the input
        print("ok, pin ist tief!")
        blink_led()
        shutdown()

# Main starts here --------------------------------------
#--------------------------------------------------------
if __name__ == '__main__':

    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    GPIO.setup(soft_shutdown_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup (led_shutdown_pin, GPIO.OUT)   # Port schaltet LED ein, diese zeigt, dass Programm läuft
    sleep(5)

    blink_led()
    GPIO.add_event_detect(soft_shutdown_pin, GPIO.FALLING, callback=my_callback, bouncetime=300)

# you can continue doing other stuff here
    while True:
        sleep(1)
        pass    # pass ist leer statement
        
# End ---------------------------------------------------------
        