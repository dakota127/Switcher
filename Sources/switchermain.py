#!/usr/bin/python
# coding: utf-8
# ***********************************************************

import sys, getopt
import defglobal
import switcher


# *************************************************
# Program starts here
# *************************************************

if __name__ == '__main__':
    switcher.arguments(sys.argv[1:])  # get commandline arguments
    
    ret=switcher.initswitcher()  # init stuff
    if ret==9:
        sys.exit(2)

    switcher.runit()         #  here is the beef, runs forever
    
    switcher.sorry()         #  Abschlussvearbeitung

#**************************************************************
#  That is the end
#***************************************************************
#