#!/usr/bin/env python
# coding: utf-8
#
#   Client-Programm für Switcher-Daemon
#  Basierend auf Lazy Pirate client von Daniel Lundin hhttp://zguide.zeromq.org/py:all
#  Use zmq_poll to do a safe request-reply
#
#   Uses reliable request-reply to send request to server
#
#   if server does logging we use the subscriber model to receive logging messages from the server.
#
#   Author: Peter K. Boxler, August 2014
#------------------------------------------------------------

import sys, getopt, os
import zmq
import time
from time import sleep
REQUEST_TIMEOUT = 4500
REQUEST_RETRIES = 3
SERVER_ENDPOINT = "tcp://localhost:5556"
GET_RETRIES=10
lastcommand=""
status=0
debug=0
web=0

# ***** Function Parse commandline arguments ***********************
# get and parse commandline args

def arguments(argv):
    global status, debug, web
    try:
        opts, args=getopt.getopt(argv,"sdS")
    except getopt.GetoptError:
        print ("Parameter Error")
        sys.exit(2)
    for opt, arg in opts:
        if opt in ("-h", "--help"):
            print ("App Switcher Client -----------------------------------")
            print ("usage: swclient [-s -S]")
            sys.exit(2)
        elif opt == '-s': 	status = 1
        elif opt == '-S': 	
            web=1   # aufruf im Web
            status=1
        elif opt == '-d': 	debug = 1
	
# ***********************************************


#----------------------------------------------------------
def printReply(meldung):
    spos=0
    epos=0
    
    #  wenn status-Antwort kommt
    if "* " in meldung.strip():
        spos=meldung.find("* ", epos)   # initil start pos
        print "--------------------------------------"
        if web: print"</br>"
        # extract all the info from the message and print it on the screen
        while True:
            epos=meldung.find("* ",spos+1)
            if epos < 0:
                epos = len(meldung)
                print "%s" % meldung[spos:epos]
                if web: print"</br>"
                break
    #        print spos,epos
            print "%s" % meldung[spos:epos]
            if web: print"</br>"
            spos=epos
            
 #       print "Statusmeldung %s" % meldung
        print "--------------------------------------"
        if web: print"</br>"
 #
 
 #   wenn andere Antwort kommt
    else:
        print "Antwort %s" % meldung
#        print "Receive %s" % meldung 
    return()
#----------------------------------------------------------

#--------------------------------------------
# try to send request to the server
#--------------------------------------------
def try_Send(meldung):
    retries_left = REQUEST_RETRIES
    global sequence
    global client

    while retries_left:
        if debug: print "Sending: %s" % meldung
        client.send(meldung)
        expect_reply = True
        while expect_reply:
            socks = dict(poll.poll(REQUEST_TIMEOUT))
            if socks.get(client) == zmq.POLLIN:
                reply = client.recv()
                if not reply:
                    break
                if ("ack" in reply.strip() or "Status" in reply.strip()):
                    printReply (reply)
                    return(0)
                    retries_left = REQUEST_RETRIES
                    expect_reply = False
                else:
                    print "E: Malformed reply from server: %s" % reply

            else:
                print "W: No response from server, retrying"
                # Socket is confused. Close and remove it.
                client.setsockopt(zmq.LINGER, 0)
                client.close()
                poll.unregister(client)
                retries_left -= 1
                if retries_left == 0:
                    print "E: Server seems to be offline, abandoning"
                    return(9)
                    break
                print "I: Reconnecting and resending (%s)" % meldung
            # Create new connection
                client = context.socket(zmq.REQ)
                client.connect(SERVER_ENDPOINT)
                poll.register(client, zmq.POLLIN)
                client.send(meldung)
#--------------------------------------------------------------

#-------------Get Command from Keyboard----------------------------------
def get_command() :
    while True:
        stop=0
        slog=0
        global lastcommand

        sys.stdout.write("Please give a command: ")
        message = raw_input().strip()
        if (len(message)==0 and lastcommand=="stat"): return (lastcommand)
        
        if (message != "log" and message != "stop" and message !="slog"   \
        and message !="term" and message !="stat" and message !="get" and message !="sim" and message !="deb" and message !="sdeb"): continue
        lastcommand=message
        return(message)              
#-----------------------------------------------


#------Receive als SUB ----------------------------   
#  receive loghing messages from server (subscriber model)   
def receive_msg():
    global anzerr
    anzerr=0
    anztry=0
   
    while True:
        try:
            message = None
           # wait for incoming message
            sleep(0.2)
            try:
                message = sub_recv.recv(zmq.DONTWAIT)
                if message:
                    print "Message IN: ", message
                if "endeeee" in message.strip():
                    break
            except zmq.ZMQError as err:
                anztry+=1
                if anztry>GET_RETRIES:
                    print "Receive error: " + str(err)
                    break
                else:
                    sleep(1)
               
        except KeyboardInterrupt:
            print "empfangen fertig, now sending again"
            break
#
#---------------------------------------------


# ---- Function empty Queue --------------
def empty_queue():
    global anzerr
    anzerr=0
    message=None
    while True:             # clear out queue
        try:
     #    print "Empying the queue...."
            message = sub_recv.recv(zmq.DONTWAIT)
                    
        except zmq.ZMQError as err:
            anzerr+=1
            if anzerr>5:
                break
            else:
                sleep(0.2)
                continue
    if message:
        print "Queue emptied, last was ", message
    else:
        print "Queue emptied, no messages"
   
    return(0)
#------------------------------    
#--------------------------
# Main


arguments(sys.argv[1:])  # get commandline arguments

#common.setup_log('ZMQ_TEST')
context = zmq.Context()

sub_recv = context.socket(zmq.SUB)
sub_recv.connect("tcp://localhost:5555")
sub_recv.setsockopt(zmq.SUBSCRIBE, '')  # subscribe to everything

client = context.socket(zmq.REQ)
client.connect(SERVER_ENDPOINT)

poll = zmq.Poller()
poll.register(client, zmq.POLLIN)

sequence = 0
retries_left = REQUEST_RETRIES
#log("ZMQ SendClient Started!")
i=0
anzerr=0
anztry=3
message=" "
stop=0
slog=0
ret=0
#

# commandline -s verlangt eine Status-Abfrage, dann exit

if status:
    cmd="stat"
    ret=try_Send(cmd)           # try to send request
    if ret == 9:
        sys.exit(2)
    sub_recv.close()
    client.close()
    context.term()
    sys.exit(2)

# Loop until command term is given
while True:
    # get command from user
    cmd=get_command()       # command in cmd
    if (cmd == "stop" or cmd=="slog"):
        ret=try_Send(cmd)           # try to send request
        if ret == 9:
            break               # senden timeout
        empty_queue()
    if (cmd=="log"):
        ret=try_Send(cmd)           # try to send request
        if ret == 9:
            break               # senden timeout
        receive_msg()           # receive from SUBScribe
    elif (cmd=="term"): 
        sleep(0.2)
        break
    elif (cmd=="stat" or cmd=="deb" or cmd=="sdeb" or cmd=="sim"): 
        ret=try_Send(cmd)           # try to send request
        if ret == 9:
            break
    elif (cmd=="get"):               # senden timeout
        receive_msg()           # receive from SUBScribe
    
    

sub_recv.close()
client.close()
context.term()
print "Client terminating..."
#            
#