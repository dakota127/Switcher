#!/usr/bin/env python
# coding: utf-8
# ***********************************************
# Interprocess Communication server-part
# Function check() wird in programm switcher periodisch aufgerufen für check auf request vom client
#
#************************************************
#
import os
import sys
import time
from time import sleep
import zmq
import defglobal

sombodyhome={1:'Nobody Home', 0:'Peter at Home'}

#-------------Init ZerMQ ------------------------------------------
def initzmq():
    global context
    global z_send
    global server
    # ZMQ context, only need one per application
    sys.stdout.write ("Init und Context")
    context = zmq.Context()

# for sending messages
    z_send = context.socket(zmq.PUB)
    z_send.bind("tcp://*:5555")

# for receiving messages

    server = context.socket(zmq.REP)
    server.bind("tcp://*:5556")
#------------------------------------------------

#-------------Terminate ZerMQ ------------------------------------------
def termzmq():
    global context
    global z_send
    global server
    server.close()    
    z_send.close()
    context.term()
#--------------Check if Request ------------------------------------------
def check():
# non-blocking check if message gekommen ist
#
    global anzerr
    global logging
    global term
    reply="acknowlege request"
    request = None
    dstatus=""
#
    # wait for incoming message
    try:
        request = server.recv(zmq.DONTWAIT) # non-blocking get
        sys.stdout.write ("dies kam rein: %s \n" % request)
    except zmq.ZMQError as err:
#        sys.stdout.write "Receive error: " + str(err)
        defglobal.anzerr+=1

    if request:    
# es ist ein request gekommen, schauen, welcher es ist und entprechend reagieren    
        if "stat" in request.strip(): 
            for j in range(4):          # status der 4 dosen erstellen aus list
                dstatus=dstatus+str(defglobal.status_dosenstatus_ext[j])
            reply="* Status: %d * Running since: %s * XML: %s * File-ID: %s * Logging: %d * Debug: %d * Weekday: %d * AnzActions: %d * Dosenstatus: %s * WaitFor: %s * ZeitNow: %s * LastAction: %s * NextAction: %s * Home: %s" %  \
            (defglobal.status_status, defglobal.startdat, defglobal.controlfile,defglobal.control_id, defglobal.logging, defglobal.debug,  defglobal.status_weekday,  defglobal.status_anzactions, dstatus, defglobal.status_waitfor, \
            defglobal.status_currtime, defglobal.status_lastaction, defglobal.status_waitaction, sombodyhome[defglobal.i_am_home] )
            
        if request=="log": defglobal.logging=1
        if request=="deb": defglobal.debug=1
        if request=="sdeb": defglobal.debug=0
        if request=="sim" : defglobal.sim=1
        if request=="slog": defglobal.logging=0
        if request=="stop":
            sys.stdout.write ("Stop from CLient received")
            defglobal.term=1  
        sleep(0.3)
# send reply, entweder standard ack oder status-antwort        
        try:
            server.send_unicode(reply)
            sys.stdout.write ("Send Reply ")
        except zmq.ZMQError as err:
            sys.stdout.write ("SendReply error: " + str(err))
#            
    return (0)
#--------------------------------------------------------------

#--------------Check if Request ------------------------------------------
def sendPub(message):
#  wenn logging verlangt ist, sende meine Arbeitsschritte an den Client 
    if defglobal.logging:
 #         sys.stdout.write "nun noch senden via PUB machen"
        try:
            z_send.send(message)
            sleep(0.1)
        except zmq.ZMQError as err:
            sys.stdout.write ("Send error PUB: %s" % str(err)) 
 #   Client sollte was bekommen haben, wir fahren weiter


    return (0)
#--------------------------------------------------------------


#
#---------- Function tuwas , hier passiert die Arbeit, ist Main -----
def tryloop(): 
  #  sys.stdout.write "ZMQ mysender7 started."
    while True:
 #   message = None
        defglobal.i+=1
# do whatever you need to do  
   
        for j in range (6):
            message="MyMsg7 " + str(defglobal.i) + " "+ str(j) + "  " + "MyMessage"
            sendPub(message)

               
        sleep(0.2)
        if defglobal.logging:
            sys.stdout.write ("Mit Logging, last sent: %d  Anzahl err: %d" % (defglobal.i, defglobal.anzerr)) 
        else:
            sys.stdout.write ("Ohne Logging, last sent: %d  Anzahl err: %d" % (defglobal.i, defglobal.anzerr))
           
# check if a request came in
        check()
#  wenn request term gekommen ist hoeren wir auf
        if  defglobal.term: break
        if  defglobal.work==0: break
#------ while TRue ends here



#-------------------------------------------------
#
# ----- MAIN --------------------------------------
if __name__ == "__main__":
    
    initzmq()
    tryloop()

    termzmq()

    sys.stdout.write ("Shut down in __main__.")