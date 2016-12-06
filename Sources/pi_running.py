#!/usr/bin/python
# coding: utf-8
# ***********************************************************
# 	Programm zum anzeigen, dass Pi läuft
#   Blinkt LED3 auf grünen Board
# 	Designed and written by Peter K. Boxler, August 2014  
#***********************************************************
#
#

led_3=11

import RPi.GPIO as gpio
from time import sleep
import sys
#

 
#from time import sleep
import RPi.GPIO as GPIO
var=1
sleep(1)

if __name__ == '__main__':
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    GPIO.cleanup(led_3)
    GPIO.setup (led_3, GPIO.OUT) 

    sleep(1)
    while True:
        GPIO.output(led_3, True)
        sleep(0.1)
        GPIO.output(led_3, False)
        sleep(1.5)
        
    GPIO.cleanup(led_3)
    sys.exit(2)
    
    
    


          
            