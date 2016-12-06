#!/usr/bin/python
# coding: utf-8
# ***********************************************************
# 	Programm zum Schalten von Funksteckdosen
# 	Designed and written by Peter K. Boxler, August 2014  
# 
#	Das Programm schaltet 4 Funksteckdosen Typ Elro ein uns aus. 
#	Die Aktionen (Einschalten/Ausschalten) pro Tag und Dose sind in einem externen XML-Inputfile codiert.
#	Es können beliebig viele Ein/Aus Schaltungen pro Wochentag (0 bis 6, also So bis Sa) und Dose definiert werden
#	Die gesamte Wochensequenz wird endlos wiederholt - Abbruch durch ctrl-c.
#   Mittels Commandline Parameter -f kann ein xml file spezifiziert werden, default file ist control.xml
#
#	Zum Testen kann mit Commandline Parameter -s eine Simulation gestartet werden: eine Woche wird 
#	dadurch in wenigen Minuten durchlaufen. 
#
#	Commandline Parameter
#	-d kleiner defglobal.debug, Statusmeldungen werden ausgegeben (stdout)
#	-D grosser defglobal.debug, weitere Statusmeldungen
#	-f filename  XML Inputfile
#	-s Simulation (Schnelldurchlauf durch 3 Wochen
#	-i min  Inkrement-Intervall bei Simulation (Minuten, 2-8 sinnvoll)
#	-t day	Wochentag, bei dem die Simulation gestartet wird
#	-h	help, usage wird ausgegeben
#	-a es werden nur die gefundenen Aktionen ausgegeben
#
#	Raspberry Besonderheiten: Das Programm wurde für GPIO-Version 2 und höher erstellt - die aktuelle
#	Version wird bei Start geprüft und ev. eine Fehlermeldung ausgegeben.
#
#	Bei Abbruch durch ctrl-c werden ev. unterbrochene Sendevorgänge  beendet (damit Handsender in definierten
#	Zustand kommt und die GPIO Pins werden zurückgesetzt (cleanup).
#
# ***** Imports ******************************
import sys, getopt, os
import time
from time import sleep
import datetime         
import RPi.GPIO as GPIO         #  Raspberry GPIO Pins
import defglobal                # global variables for all Modules
import swipc                 # Interprocess Comm with ZMQ
import swparse                 # Parse XML File


# ***** Variables *****************************

sim=0
simday=0			# wochentag für Start Simulation
startzeit=19		# Startzeit für Simulaton
stopzeit=23			# EndZeit für Simulaton
first=1				# First switch für loop
count=0
intervall=5  		# Minutenincrement für Simulation
simhour=0			# Stundenzähler der Simulation
simmin=0			# Minutenzähler der Simulation
simweek=0			# Zähler für Wochen
simweek_count=3		# Anzahl Wochen, die bei Simulation durchlaufen werden
sleeptime=3			# default sleeptime normaler Lauf
sleeptime_sim=0.02	# sleeptime für Simulation
tmp=0				# tmp für ein/aus
sending=0			# flag, tells if sending is in progress - used if keyboard Interrrupt
waittime_senden =1.5
doboth	=1		
xmlfile="control.xml"	#default input file name	
actions_only=0		# switch für commandline arg a

ret=[0,0]
#
# define Dosen (1-4) und passende Buchstaben
Dose={1:'A', 2:'B',3:'C' ,4:'D'}
# define GPIO signals to use for sending signals
# and the mapping to signals -D and On/Off
Pins={'A': 4, 'B':22,'C':18,'D':25,'ON':24,'OFF':23}
onoff={1:'ON', 0:'OFF'}
pin_blink=10    # GPIO für blinkende LED auf grünem Board 
home_switch=7   # I am Home Switch (hoch=not home/tief=home)
#
# ***** Function Parse commandline arguments ***********************
# get and parse commandline args

def arguments(argv):
    global  intervall, sim , simday, xmlfile, actions_only
    try:
        opts, args=getopt.getopt(argv,"hdaDst:i:f:")
    except getopt.GetoptError:
        myPrint ("Parameter Error")
        sys.exit(2)
    for opt, arg in opts:
        if opt in ("-h", "--help"):
            myPrint ("App Switch Lights -----------------------------------")
            myPrint ("usage: switch_lights [-s -d -a -D -i minutes -f filename]")
            sys.exit(2)
        elif opt == '-d': 	defglobal.debug = 1
        elif opt == '-D':	defglobal.debugg = 1
        elif opt == '-s':	sim = 1
        elif opt == "-a":	actions_only=1
        elif opt == "-i":	intervall = int(arg)
        elif opt == "-t":	simday = arg
        elif opt == "-f":	xmlfile = arg
	
# ***********************************************

# ***** Function zum Senden *********************
# Switches "switch" to ON or OFF state
#Paramaters are: "switch" (A,B,C,D) and "state" (ON,OFF), do what (1=start and stop sending,0=stop only)

def setSwitch(switch, state, what):
    global GPIO
    if defglobal.debug: print "SetSwitch Port: %s State: %s, what: %d" % (Pins[switch], state, what)
# parameter what indicates: 1: sender für waittime_senden einschalten und danch wieder ausschalten
#                           0: sender nur ausschalten (nötig bei Abbruch des programms durch ctrl-c)
    if what:				# what=1 says: do both
        GPIO.output(Pins[switch], True)
        GPIO.output(Pins[state], True)
        sending=1					# currently sending a signal - wegen Abbruch ctrl-c
        time.sleep(waittime_senden)
    # senden wieder ausschalten    
    GPIO.output(Pins[switch], False)
    GPIO.output(Pins[state], False)
    time.sleep(waittime_senden)     # korrektur habi (give transmitter time to settle down)
    sending=0					# done sending
# ************************************************** 		

			
# ***** Function zum Setzen der benötigteh GPIO Pins **********
def setpins(how):
    global GPIO, home_switch
    
    if how:             # 1 means setup  / 0 means clenaup
# set all needed pins as output
        GPIO.setup (pin_blink, GPIO.OUT)   # Port schaltet LED ein, diese zeigt, dass Programm läuft
        blink_led(pin_blink,3)    # blink led 3 mal beim Start
        GPIO.setup(home_switch, GPIO.IN, pull_up_down=GPIO.PUD_UP)          # switch Home / not Home


        for pin in Pins:
            GPIO.setup(Pins[pin], GPIO.OUT)
            GPIO.output(Pins[pin], False)
    else:
# cleanup alle benötigten Pins - und nur diese!!
        for pins in Pins:
            GPIO.cleanup(Pins[pins])  # cleanup GPIO Pins
        blink_led(pin_blink,3)    # blink led 3 mal beim Stop
        GPIO.cleanup(pin_blink)
        GPIO.cleanup(home_switch)

# *************************************************** 

# ***** Function myPrint **************************
def myPrint(meldung):
 
    swipc.sendPub(meldung)
    if defglobal.forep:
        print (meldung) 
# *************************************************** 

# ***** Function blink-led **************************
def blink_led(pin,anzahl):  # blink led 3 mal bei start und bei shutdown
        for i in range(anzahl):
            GPIO.output(pin, True)
            sleep(0.1)
            GPIO.output(pin, False)
            sleep(0.1)

# ***** Function show_time **************************
def show_time():
    zeit=str(datetime.datetime.now().strftime("%H.%M"))
    if not sim:
        myPrint ("Starting with Wochentag: %s / Zeit: %s " % (datetime.date.today().strftime("%w-%A"), zeit	))	
# *****************************************************    

# ***** Function increase simulated time **************
def addint():
    global simmin,intervall,simhour 
    incr=0
    if simhour==23:
        simmin=simmin+1				# increase minutes only 1 before midnight - 
									# simply to make sure simulation runs for switch time shortly before midnight
    else:
        simmin=simmin+intervall
    if simmin>59:
        simhour=simhour+1
        simmin=simmin-60
    if simhour>=24:
        simhour=0
        incr=1
			
    return ([simhour, simmin,incr])	
# *******************************************************    


# ***** Function get_time and weekday *******************
# returns list["HH.MM", weekday]
#
def get_time (sim, startzeit,stopzeit):
    global count
    global first, intervall, simday, simhour, simmin, simweek
    returnlist=list()
    returnlista=list()

    hour=""
    min=""
    retu=""
	#  return current time if not simulation
    if not sim: 
        returnlist=[datetime.datetime.now().strftime("%H.%M"),datetime.date.today().strftime("%w")]
        return(returnlist)
		#	return(datetime.datetime.now().strftime("%H.%M"))
#
	# return start time if simulation first time round
    if first:
        count=startzeit
        simhour=startzeit
        simmin=0
        first=0
	# increase time if simulation 

    returnlist=addint()
	
    hour=str(returnlist[0])
    min=str(returnlist[1])
    if len(hour)==1: hour = "0" + hour
    if len(min)==1: min = "0" + min
# start simulation on day 0 (sunday)	
    simday=simday+returnlist[2]			# increase weekday if time excceeded 24.00 
    if simday>6: 
        simday=0
        simweek+=1	
    retu=hour+"."+min
    returnlist=[retu,simday]	
    return returnlist
# ************************************************


#  -------- Function INit ------------------------
def initswitcher():
    global actions_only, sleeptime, startaction,weekday_new,weekday_current,xmlfile
    global simday, intervall,sim, ret, GPIO
    if defglobal.debugg:
        defglobal.debug=1
        
    pfad=os.path.dirname(os.path.realpath(__file__))    # pfad wo dieses script läuft
    xmlfile=pfad + "/" + xmlfile
    if os.path.exists(xmlfile):
        myPrint ("XML file found: %s" % xmlfile)	# file found
    else:
        myPrint ("XML file %s not found" % xmlfile)	# file not      
        return(9) 
    defglobal.controlfile=xmlfile   
    swparse.parse_file(xmlfile)			# parse Input Datei (XML) 	
    myPrint ("Nun geht es los...")	# wir starten
    if (defglobal.debug or actions_only): swparse.print_actions()	# alle gefundenen Aktionen ausgeben
    if actions_only: sys.exit(2)
	
    #Use BCM GPIO refernece instead of Pin numbers
    GPIO.setmode (GPIO.BCM)
    rev=GPIO.RPI_REVISION
    setpins(1)  # set GPIO Pins zum Senden


    show_time()					# zeige Datum und WochenTag
    if rev==1:
        myPrint ("GPIO-Version 1 has different port numbering - please check program !")
        myPrint ("Program was developed for Rev2 and later.")
    if sim: 					# falls Simulation gewünscht - simulation requested
        myPrint ("Run Simulation for Weekday: %d  Minuten-Increment: %d"  % (simday,intervall))
        sleeptime=sleeptime_sim		# setze Sleeptime für Sim
    myPrint ("Raspberry GPIO-Version: %1.1f" % rev)	
    defglobal.startdat = "%s %s"  % (datetime.date.today().strftime("%A"), datetime.datetime.now().strftime("%d.%m.%Y %H.%M"))
    
    # check the Home/nothome switch 
    if GPIO.input(home_switch):     # check swich
                                    # true means high potential means not home - regular betrieb
        defglobal.i_am_home_old=1  # keep initail value switch open, high potential
        defglobal.i_am_home=1       # current value
        myPrint ("Nobody Home, start switching...")	# wir starten
    else:
        defglobal.i_am_home_old=0       # 0 means switch is closed (home), also nicht schalten  
        defglobal.i_am_home=0       # current value
        myPrint ("Someboy Home, just pretend...")	# Peter is at home
        GPIO.output(pin_blink, True)        # set led on if at home

    #   also, dass es jeder depp versteht: i_am_home=0 heisst: low potential, schalter zu, bin daheim
    #                                      i_am_home=1 heisst: high potential, schalter offen bin weg, normal schalten
    
    myPrint ("Nun geht es los...")	# wir starten
    
    # zu Beginn alle Dosen aus
    set_switches(0)             # alle Schalter off

    # init Interprocess Communication, set up Sockets
    swipc.initzmq()

# End Function initswitcher**************************


# ---- Fuction set-switches ------------------------------
def set_switches(how):
# how=0: alle switches off, do not change status_dosenstatus variable
# how=1: set alle switches according to the variable status_dosenstatus (internal status)
#
    if how:
        if defglobal.status_dosenstatus[0]:  
            setSwitch('A','ON',doboth)
            defglobal.status_dosenstatus_ext[0]=1
            
        if defglobal.status_dosenstatus[1]:  
            setSwitch('B','ON',doboth)
            defglobal.status_dosenstatus_ext[1]=1
            
        if defglobal.status_dosenstatus[2]:  
            setSwitch('C','ON',doboth)
            defglobal.status_dosenstatus_ext[2]=1  
                      
        if defglobal.status_dosenstatus[3]:  
            setSwitch('D','ON',doboth)
            defglobal.status_dosenstatus_ext[3]=1
            
    
    
    else:       # set alle switches to OFF
        setSwitch('A','OFF',doboth)
        setSwitch('B','OFF',doboth)
        setSwitch('C','OFF',doboth)
        setSwitch('D','OFF',doboth)
        for i in range (len(defglobal.status_dosenstatus_ext)):
            defglobal.status_dosenstatus_ext[i]=0
#------------------------------------------------------------


#  -------- Function Terminate ------------------------
def termswitcher():     # terminate sending and switch off all Dosen
    global sending, doboth
    if sending:				# was sending going on? 
        setSwitch('A','OFF',0)
        setSwitch('B','OFF',0)
        setSwitch('C','OFF',0)
        setSwitch('D','OFF',0)
    sleep(0.5)					# works better
    set_switches(0)             # alle Schalter off
    GPIO.output(pin_blink, False)        # set led off if NOT at home

    return(0)
# End Function termswitcher**************************



# Main Loop -------------------------------------------------------------
def runswitch():

    global actions_only, sleeptime, startaction,weekday_new,weekday_current
    global simday, intervall,sim, ret, Dose
#
#    
    if defglobal.debug: sleep(3)
    myPrint ("Function runswitch() started")
    j=0
    ret=get_time(sim,startzeit,stopzeit)	# Aktuelle Zeit holen
# return ist liste mit [zeit,Wochentag]
# wir starten mit den aktuellen WochenTag (0 bis 6)
    weekday_new=int(ret[1])
    weekday_current=99
    startaction=0
    
#  ---- Main Loop -----------------------------------------------------------    
    while True:
            # check termination from daemon - signalled via global variable    
        if  defglobal.term: break             # break from main Loop


# posit: solange, falls kein Ctlr-C kommt
        try:

            if weekday_current != weekday_new:	# prüfe Gruppenbruch: neuer Wochentag?
                if defglobal.debug:  myPrint ("New Day %d" % weekday_new)
                weekday_current=weekday_new
                defglobal.status_weekday=weekday_new                              # für status request ===============
                actions=len (defglobal.tage[weekday_current])	# Anzahl Aktionen für diesen Tag holen
# prüfe, ob an diesem Wochentag überhaupt actions vorgesehen sind
                if sim or defglobal.debug:  
                    myPrint ("Working on Weekday: %d has %d" % ( weekday_current, actions) )
                    sleep(2)

#----- Loop1 über alle Actions eines Tages -------------------------------------------------- 
#  prüfen, ob es aktionen für diesen Tag hat, die zeitlich vor der aktuellen Zeit liegen
#  diese Aktionen werden zu Beginn ausgeführt !
                for j in range(actions):           #actions enthält alle aktionen des tages
                    if defglobal.debugg: 
                        myPrint ("CheckDoNow: action: %d currtime: %s , actiontime: %s" % (j, ret[0], defglobal.tage[weekday_current][j][0]))
                    if ret[0] > defglobal.tage[weekday_current][j][0]:			# ret[0] sind Stunden.Minuten, check Actions times to current time
                                                                        # mache actions die in der vergangenheit liegen
                        if sim or defglobal.debug: myPrint ("-----> DoNow Action Dose: %s Zeit: %s / %s" % (defglobal.tage[weekday_current][j][1], defglobal.tage[weekday_current][j][0], onoff[ defglobal.tage[weekday_current][j][2] ] ))
                        startaction=j
            # die Actions, die in der Vergangenheit werden, werden ausgeführt, damit initialzustand ok ist
                        setSwitch ( Dose[int(defglobal.tage[weekday_current][j][1]) ], onoff[defglobal.tage[weekday_current][j][2]], doboth)
                        defglobal.status_dosenstatus[defglobal.tage[weekday_current][j][1]-1] = defglobal.tage[weekday_current][j][2]    # set internal status - 
                        defglobal.status_dosenstatus_ext[defglobal.tage[weekday_current][j][1]-1] = defglobal.tage[weekday_current][j][2]    # set external status - client might want to know it

                    else: break	
                if startaction>0: startaction +=1	# bei dieser Aktion dieses Tages wird begonnen		
#  nun wissen wir, mit welcher Aktion für diesen Tag zu starten ist.				
                if sim or defglobal.debug: myPrint ("Start mit Aktion: %d"  % startaction)
#
#----- Loop2 über alle Actions eines Tages --------------------------------------------------                   
                for j in range(startaction, actions):	# loop über alle remaining Aktionen dieses Tages
			#	if defglobal.debugg: 
#				myPrint ("Current Time %s Waiting for next Action Time (Actionlist): %s" % (ret[0], defglobal.tage[weekday_current][j][0]))
#
                    defglobal.status_waitaction="Zeit: %s Dose: %s / %s" % (defglobal.tage[weekday_current][j][0],defglobal.tage[weekday_current][j][1], onoff[defglobal.tage[weekday_current][j][2]])
                    defglobal.status_status=2                                     # für status request ===============                                        
                    defglobal.status_waitfor=defglobal.tage[weekday_current][j][0]          # für status request ===============
#
#                    
# --------------Loop bis es Zeit ist für eine neue Aktion -------------------------------------While True ----------------------
                    while True:	
                        if defglobal.debugg: myPrint ("start inner loop")
                        if  defglobal.term: 
#                            myPrint ("\ninner Loop finds term=1")
                            break
                        if defglobal.debug: 
                            defglobal.debugg=1
                        else:
                            defglobal.debugg=0
                        defglobal.status_currtime=ret[0]        # für status request =============== 
                        if defglobal.sim: sim=1 

     #           Home NoHome Switch prüfen
                        defglobal.i_am_home=int(GPIO.input(home_switch))        # check swich
     # debug               print "NEU: %d , ALT: %d" %  (defglobal.i_am_home,defglobal.i_am_home_old)       # true means high potential means not home - regular betrieb
                        if defglobal.i_am_home_old != defglobal.i_am_home:   #  has switch changed ?
                            defglobal.i_am_home_old=defglobal.i_am_home     # save new value in old value
                            if defglobal.i_am_home:
                                myPrint ("Nun niemand daheim, setzt Dosen gemäss Dosenstatus")
                                set_switches(1)                             # nun niemand da, setze Dosen gemäss gespeichertem Status
                                GPIO.output(pin_blink, False)        # set led off if NOT at home


                            else:
                                myPrint ("\Wieder jemand daheim, setze alle Dosen OFF")
                                set_switches(0)                             # nun wieder jemand daheim, setze alle Dosen OFF
                                GPIO.output(pin_blink, True)        # set led on if at home

    #
                        if ret[0] >= defglobal.tage[weekday_current][j][0]:	#	prüfe ob jetzt die Zeit da ist für aktuelle Aktion		
                        
#  ++++++++++++++++++++++++
# ++++++++++++++++++++++++++++++++
#  ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++				
#  ++++++++++++	Führe Aktion aus (Ein oder Aus schalten einer Dose)  +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++		
                            if sim or defglobal.debug: myPrint ("-----> Action on Dose: %d  Zeit: %s %s" % ( defglobal.tage[weekday_current][j][1], ret[0], onoff[defglobal.tage[weekday_current][j][2]]   ))				
#http://im-sandkasten.ch/node/52
#   call setSwitch ("A", "ON", int) to switch ON or OFF
#   ABER nur, wenn niemand daheim ist : Home-NOHOME switch schon geprüft, bei daheim schalten wir nicht, setzen aber den Dosenstatus
                            
                            if defglobal.i_am_home:         # 1 means: NOT at home
                                setSwitch ( Dose[int(defglobal.tage[weekday_current][j][1]) ], onoff[defglobal.tage[weekday_current][j][2]], doboth)
#   set Status-String (Dosenstatus), set corresponding position to 1 (ON) or 0 (OFF), is internal Status , also set external status                               
                            defglobal.status_dosenstatus[defglobal.tage[weekday_current][j][1]-1] = defglobal.tage[weekday_current][j][2]  
                            defglobal.status_dosenstatus_ext[defglobal.tage[weekday_current][j][1]-1] = defglobal.tage[weekday_current][j][2]   
                             
#
#  ++++++++++++ Schalten und Status setzen fertig ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
#  +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
#  ++++++++++++++++++++++++++++++++
#  +++++++++++++++++++
# 
                            defglobal.status_lastaction="Zeit: %s Dose: %s / %s" % (defglobal.tage[weekday_current][j][0],defglobal.tage[weekday_current][j][1], onoff[defglobal.tage[weekday_current][j][2]]  ) 
                            defglobal.status_anzactions+=1          # increment anzahl getaner Aktionen                

                            break                   # break While True, wir haben eine Aktion ausgeführt
#  check if all actions for this particular day are done	

                        sleep(sleeptime)
                        if defglobal.i_am_home:         # 1 means: not home, blink only when not at home
                            blink_led(pin_blink,2)    # blink led 2 mal while waiting
                        ret=get_time(sim,startzeit,stopzeit)	#  get new time
                        if defglobal.debugg: myPrint ("Timemarching on: %s  Tag %d" % (ret[0], weekday_current))
# 
                        swipc.check()		# check if request from client came in - and answer it.
#----End While True --------------------------------------------------
#       this ausserhalb inner loop
#
                    weekday_new=int(ret[1])			# get new weekday
#
#----End Loop über alle actions des Tages -----------------------------
                    if  defglobal.term:  break    # break loop über alle actions des Tages


#  back in the Main Loop again                              
            startaction=0
            ret=get_time(sim,startzeit,stopzeit)
            weekday_new=int(ret[1])
            if defglobal.debugg: myPrint ("Timemarching on 2: %s" % ret[0])
            sleep(sleeptime)
            if simweek==simweek_count: break    # aufhören bei Simulation nach n wochen
            


#  der loop läuft, bis ein Keyboard interrupt kommt, ctrl-c ----

        except KeyboardInterrupt:
    # aufräumem
            myPrint ("\nKeyboard Interrupt, alle Dosen OFF und clean up pins")
            termswitcher()
            return()

#---- End Main Loop -------------------------------------------------------------

# End Funtion runit ********************************

#*********  endebehandlung **********
def terminate():
    myPrint("switcher terminating")
    global GPIO
    termswitcher()    
#
    setpins(0)      # cleanup GPIO Pins nur die verwendeten

    myPrint ("Anzahl Wochen simuliert: %d " % simweek)			
    myPrint ("Program terminating....")
    swipc.termzmq()     # terminating INterprocess-Communication, Sockets und so....
#************************************    
	
# *************************************************
# Program starts here
# *************************************************

if __name__ == '__main__':
#
    defglobal.forep=1     # zeigt, dass Programm im Vordergrund läuft, Main wurde gerufen
    arguments(sys.argv[1:])  # get commandline arguments

    ret=initswitcher()  # init stuff
    if ret==9:
        sys.exit(2)
    runswitch()         #  here is the beef, runs forever
    
    terminate()         #  Abschlussvearbeitung

#**************************************************************
#  That is the end
#***************************************************************
#