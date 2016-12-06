#!/usr/bin/python
# coding: utf-8
# ***********************************************************
# 	Programm zum Anzeigen des Inhalts des XML COntrolfiles
# 	Designed and written by Peter K. Boxler, Februar 2015  
# 
#   Hilfsprogramm, welches die Aktionen im Control-File detailliert anzeigt
#
#
#	Commandline Parameter
#	-d kleiner defglobal.debug, Statusmeldungen werden ausgegeben (stdout)
#	-f filename  XML Inputfile
#
#   Verbessert/Erweitert im Januar 2015, Peter K. Boxler
# ***** Imports ******************************
import sys, getopt, os
from xml.dom import minidom
import time
from time import sleep
import datetime
import swparse
import defglobal                # global variables for all Modules

# ***** Variables *****************************
tmp=0				# tmp für ein/aus
xmlfile="control.xml"	#default input file name	
forep=1
# aWeekdays
Weekdays={0: "Sonntag", 1:"Montag", 2: "Dienstag",3:"Mittwoch",4:"Donnerstag",5:"Freitag", 6:"Samstag"}
onoff={1:'ON', 0:'OFF'}

#

#
# ***** Function Parse commandline arguments ***********************
# get and parse commandline args

def arguments(argv):
    global intervall, sim , simday, xmlfile, actions_only
    try:
        opts, args=getopt.getopt(argv,"hdDf:")
    except getopt.GetoptError:
        myPrint ("Parameter Error")
        sys.exit(2)
    for opt, arg in opts:
        if opt in ("-h", "--help"):
            myPrint ("App Switch Actions -----------------------------------")
            myPrint ("usage: swactions [-d  -f filename]")
            sys.exit(2)
        elif opt == '-d': 	defglobal.debug = 1
        elif opt == '-D': 	defglobal.debugg = 1

        elif opt == "-f":	xmlfile = arg
	
# ***********************************************


# ***** Function myPrint **************************
def myPrint(meldung):
    
    if defglobal.forep:         # im Vordergrund
        print meldung

# *****************************************************    




# *************************************************
# Program starts here
# *************************************************

if __name__ == '__main__':
#

    defglobal.forep=1       # runs in foreground
    arguments(sys.argv[1:])  # get commandline arguments

# set defglobal.debug is full defglobal.debug is requested (-D)
    if defglobal.debugg:
        defglobal.debug=1
        myPrint ("Full defglobal.debug.....")

    pfad=os.path.dirname(os.path.realpath(__file__))    # pfad wo dieses script läuft
    xmlfile=pfad + "/" + xmlfile
    if os.path.exists(xmlfile):
        myPrint ("XML file found: %s" % xmlfile)	# file found
    else:
        myPrint ("XML file %s not found" % xmlfile)	# file not found      
        sys.exit(2)
    
    defglobal.controlfile=xmlfile   

    swparse.parse_file(xmlfile)			# parse Input Datei (XML) 	and fill lists with data

    if defglobal.debug: myPrint ("Parsing done, Nun geht es los...")	# wir starten

    swparse.print_actions()	    # alle gefundenen Aktionen in Listen ausgeben

#
#  Abschlussvearbeitung
    myPrint ("Program terminated....")
    sys.exit(0)
#**************************************************************
#  That is the end
#***************************************************************
#