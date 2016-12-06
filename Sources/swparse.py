#!/usr/bin/python
# coding: utf-8
# ***********************************************************
# 	Funktionen für Switcher
#   In diesem File sind die 2 Funktionen
#   parse_file()
#   print_actions()
#   
#   implementiert.
#	Diese Funktionen werden im programm switcher.py und swactions.py verwendet.
#
#   Verbessert Januar 2015, P.K. Boxler
#
# ***** Imports *********************************************
import sys, getopt, os
from xml.dom import minidom     # parsing xml
import time
from time import sleep
import datetime    
import math
     
import defglobal                # global variables for all Modules

Weekdays={0: "Sonntag", 1:"Montag", 2: "Dienstag",3: "Mittwoch",4: "Donnerstag",5: "Freitag", 6: "Samstag"}
onoff={1:'ON', 0:'OFF'}

maxlen=90
maxdose=4
maxday=7
woche2=list()  
timelin3="17       18        19        20        21        22        23        24        01        02"


# ***** Function myPrint **************************
def myPrintp(meldung):
    
    if defglobal.forep:     # runs im Vordergrund
        print meldung

# *****************************************************    


# -- Funktion und Position und Länge für Chr X zu ermitteln auf der gedachten Zeitachse
#
#   Die grafische Zeitachse ist 90 Positionen lang, diese decken die Zeit von 17.00 bis 02.00 ab
#   Alle Schaltzeiten ausserhalb dieses Bereiches werden nicht berücksichtigt
#   Schaltzeiten, die in den Bereich hineinragen (vorher oder nachher), werden entsprechend berücksichtigt
#   Für Stunden 0 und 1 (nach Mitternacht) wird je 24 addiert.
#
#   nach diversen Tests funktioniert folgender Code - ist aber nicht komplett fehlerfrei   
#
def posanz (start,end):
    returnvalue=[[0],[0]]
    
    if defglobal.debug: print "    Pos und Anz ermitteln für: %4.2f/%4.2f ---------------" % (start, end)
    s1=math.modf(start)
    e1=math.modf(end)
# s1[0] = dezimal Minuten
# s1[1] = Ganzahl Stunden
    
    if defglobal.debug: print "    Anfang/Ende in Std: %s/%s  %s/%s " % (s1[1], s1[0], e1[1],e1[0])  

    std_anfang=s1[1]               # stunden Start
#    if ((std_anfang==0) or (std_anfang==1)):        
    if ((std_anfang>=0) and (std_anfang<12)):        
        std_anfang=std_anfang+24          # ajustiere für nach Mitternacht

    std_ende=e1[1]               # stunden ende
    if ((std_ende>=0) and (std_ende<12)):        
        std_ende=std_ende+24          # ajustiere für nach Mitternacht
    
    star=int(math.floor((s1[0]*100)+(std_anfang*60)))  # berechne start in Minuten (ab 0.00)
    end=int(math.floor((e1[0]*100)+(std_ende*60)))   # berechne Minuten der Endezeit
    if defglobal.debug: print "    Anfang/Ende Min: %s  %s " % (star, end)  

    
    if (((end < 1020) and (star < 1020))) or  \
        (((star >1560) and (end > 1560))):  # diese kommen nicht in Frage
#    if ((std_ende < 17) and (std_ende > 2)):  # diese kommen nicht in Frage
        returnvalue[0]=0
        returnvalue[1]=0
        if defglobal.debug: print "    Kommt nicht in Frage"
        return (returnvalue)

    
    if defglobal.debug: print "    Anfang/Ende  2 Std: %s  %s " % (std_anfang, std_ende)  
    
    
    if star < 1020:                             # wenn Start kleiner 17.00
        pos=0
        star=1020                               # setze Start 17.00
  
    else:    
        pos= int(math.floor((star-1020)/6))     # berechne Position ab welcher Zeichen

#nun die dauer
    std=e1[1]                                   # Stunden der EndeZeit
    if ((std==0) or (std==1) or (std==2)):        
        std=std+24                              # ajustiere für nach Mitternacht
    if defglobal.debug: print "    Ende Std: %s" % std    
    end=int(math.floor((e1[0]*100)+(std*60)))   # berechne Minuten der Endezeit
    if defglobal.debug: print "    Ende 1: %s" % end
    if end < 1020:                              # wenn Ende kleiner 17 Uhr
        end=1560                                # setze Ende auf 02.00 Uhr
    elif end > 1560:                            # wenn Ende grösser 02.00 Uhr setze Ende 02.00
        end=1560    
    if defglobal.debug: print "    Ende 2: %s" % end
    dauer=end-star                              # Leuchtdauer in Minuten
    if defglobal.debug: print "    Brenndauer: %s" % dauer
    if dauer < 0:
        returnvalue[0]=0
        returnvalue[1]=0
        return (returnvalue)

    if dauer <= 6: anz=1
    else:
        div=dauer/6
        anz=int(math.floor(div))
#    if defglobal.debug: print "    Position: %s  Anzahl: %s" % (pos,anz)
    
    returnvalue=(pos,anz)
    
    return (returnvalue)
#-----------------------------------------


# --- Funktion umd Char X in die Zeile zu setzen -----------------
def setburn (woch ,z,y, pos,anz):
    if defglobal.debug: print "    setchar:  Tag: %d  Dose: %d Pos: %d  Anz: %d " % (z,y, pos,anz)

    j=0
    for i in range (anz):       # anz = Anzahl der Char zu setzen
#        print "Anz %d / %d" % (i,z)
        woch[z][y-1][pos+j]='0'           # z=tag / y=Dose  (muss -1 sein, da dosen mit 1-4 bezeichnet sind)
        j=j+1
        if (pos+j) >=maxlen: break         # ueberlauf vermeiden

# Testdruck des Tages
    if defglobal.debug:
        for u in range(maxlen):
            sys.stdout.write(woche2[z][0][u])
        print '\r'

    return(0)
#-------------------------------------------------------



# ***** Function print actions items in Liste 1, 2 und 3 *************

def print_actions():
    global  woche2, maxlen, maxdose, maxday
    
    myPrintp ("Control-File-ID : %s " % defglobal.control_id)
    
  #  dies sind die Zeilen: für jeden der 7 Wochentage 4 Zeilen (für die 4 Dosen)  
    woche2=[    [[],[],[],[]], \
                [[],[],[],[]], \
                [[],[],[],[]], \
                [[],[],[],[]], \
                [[],[],[],[]], \
                [[],[],[],[]], \
                [[],[],[],[]] \
            ]

    for z in range (maxday):            # init alle Zeilen für alle Tage mit '-'
        for i in range (maxdose):
           for k in range(maxlen):
                woche2[z][i].append('-')
    
    #
    #  Liste 1 *********************************************
    #
    print '\n'
    myPrintp ("Liste 1:  Aktionen pro Wochentag ---------------\n")
    for i in range (len(defglobal.tage)):       # loop über alle Tage 
        l=len(defglobal.tage[i])                # hat Tag überhaupt Aktionen ?
        if l != 0:                              # ja, hat er
            myPrintp ("Wochentag: %s - Anzahl Aktionen: %d" % (Weekdays[i],len(defglobal.tage[i])))
            for j in range (len(defglobal.tage[i])):    # loop über alle Aktionen eines Tages
                switch="On"
	# hole ein/aus für action j am tag i			
                if defglobal.tage[i][j][2] == 0:
                    switch="Off"
                myPrintp ("Zeit: %s Dose: %s  Switch %s" % (defglobal.tage[i][j][0],defglobal.tage[i][j][1], switch))
    myPrintp ("End Aktionen pro Wochentag ----------------------\n")
    
    #
    #  Liste 2 ***********************************************
    #
    myPrintp ("Liste 2: Aktionen pro Dose ----------------------\n")
    for i in range(len(defglobal.tage2)):           # loop über alle Tage
        print "---- %s %s" % (Weekdays [i], "----------------")
    
        for j in range(len(defglobal.tage2[i])):    # loop über alle Dosen
            anzact=len(defglobal.tage2[i][j])   # number of actions for this dose on this day
       
            if anzact == 0:
                continue     #  keine Aktionen, also skip 
            print "---- Dose %d, Anzahl Actions %d " % ((j),anzact)
        
            if anzact % 2:
                print "Error, Dose %s hat ungerade Anzahl Actions -------"   %  anzact       
#                 
            for k in range(0,anzact,2): # loop über alle Aktionen einer Dose
                print "Zeit: %s, Action: %s" % (defglobal.tage2[i][j][k][0],onoff[defglobal.tage2[i][j][k][1]])
                print "Zeit: %s, Action: %s" % (defglobal.tage2[i][j][k+1][0],onoff[defglobal.tage2[i][j][k+1][1]])
                
                #  anzahl und position feststellen für gedachte Zeitachse 
                ret=posanz( float(defglobal.tage2[i][j][k][0] ) , float(defglobal.tage2[i][j][k+1][0]) )
                if defglobal.debug: print "    Return: Pos: %d  Len: %d" % (ret[0], ret[1])
                
                # Nun den gewählten Charakter an die ermittelte Position und Länge in der passenden Zeile (Zeitachse) schreiben
                setburn (woche2, (i), (j) ,ret[0],ret[1])    # i=tag / j= dose / ret[0]=Position / ret[1]= Länge

            pass
# -----------------------------
## Ende einer Dose
#-----------------------------
    pass
# -----------------------------
# Ende aller Dosen
#-----------------------------

    pass

# -----------------------------
# Ende aller Tage
#-----------------------------
    myPrintp ("End Aktionen pro Dose ------------------------\n")
    print '\r'

    #
    #  Liste 3 ***************************************************
    #
    myPrintp ("Liste 3: Schaltaktionen Graphisch ------------\n")

    for i in range(maxday):             # über alle Tage
        print "%s" % Weekdays[i]
        print "%s" % timelin3

        for k in range (maxdose):       # über alle Dosen
            for u in range(maxlen):     # Zeitachse hat 90 Stellen
                sys.stdout.write(woche2[i][k][u])
            print "  Dose %d" % (k+1)   # Am Ende anfügen Dosennummer
          #  print '\r'
        print '\r'
 
    myPrintp ("End Aktionen Graphisch -----------------------\n")


# *************************************************



# ***** Function readfile (xml-file) and parse ***************
def parse_file ( filename):
    if defglobal.debug: myPrintp ("\nStart Parsing Inputfile: %s" % filename)
    xmldoc = minidom.parse(filename)
    control =xmldoc.getElementsByTagName("control")[0]
    dosen = xmldoc.getElementsByTagName("dose")
# Hole Identifier aus dem File - der sagt was aus über den File
    defglobal.control_id = control.getElementsByTagName("file-id")[0].firstChild.data

    seqtmp=list()
# a sequence is one on-off sequence for a particulr switch and a particular day
    seq=list()
    action=list()
    actionListperDay=list()
    defglobal.tage=[[99,99],[99,99],[99,99],[99,99],[99,99],[99,99],[99,99]]  # defines defglobal.tage als Liste von Listen
    defglobal.tage2=[ [[],[],[],[],[]] , [[],[],[],[],[]] , [[],[],[],[],[]], [[],[],[],[],[]], [[],[],[],[],[]],[[],[],[],[],[],[]] ,[[],[],[],[],[]] ]
    d=0
    s=0

#   Erklärung des Elements tage: das ist eine Liste von Listen
#   -----------------------------------------------------------
#   Nämlich:
#   Eine Liste von 7 Elementen Weekday (eines für jeden Wochentag 0-7) 
#   Jedes Element Weekday ist eine Liste von Schaltaktionen (actions) für den Wochentag
#   Jede Schaltaktion (action) ist ebenfalls einen Liste (Zeit, Dose, On/Off)
#

#   Element tage=   (   Weekday ,
#                       Weekday ,
#                       Weekday ,
#                       Weekday ,
#                       Weekday ,
#                       Weekday ,
#                       Weekday )
#
#   Element Weekday = ( action ,
#                       action ,
#                       action ,
#                       .....
#                       action )
#
#   Element action = (Zeit, Dose, ON/OFF)
#
#        
#
#   Erklärung des Elements tage2: das ist eine Liste von Listen von Listen
#   ----------------------------------------------------------------------
#   Nämlich:
#   Eine Liste von 4 Dosen-Elementen (eines für jede Dose 0-3) 
#   Jedes Dosen-Element besteht Wochentages-Elementen (0-7)
#   Jedes Wochentag-Element besteht aus einer Liste von Schaltaktionen
#   Jede Schaltaktion (action2) ist ebenfalls einen Liste (Zeit, On/Off)
#
#
#   tage2 = (   Dose ,
#               Dose ,
#               Dose ,
#               Dose  )
#
#   Element Dose=(  Weekday ,
#                   weekday ,
#                   weekday ,
#                   weekday ,
#                   weekday ,
#                   weekday ,
#                   weekday )
#
#   Element Weekday = ( action2 ,
#                       action2 ,
#                       action2 ,
#                       .....
#                       action2 )
#
#   Element action2 = (Zeit, ON/OFF)
#
#
#
#
#
    for dose in dosen:
#	myPrint "Anzahl Dosen: ", len(dosen)
        d+=1
        dosennummer = int(dose.getElementsByTagName("dose-nr")[0].firstChild.data)
        if defglobal.debugg: myPrintp ("Process Dosennummer: %s  -----------------" % dosennummer)
# get days for a Dose
        days = dose.getElementsByTagName("day")	
        for day in days:
#			myPrint "Anzahl Days :", len(days)
# get weekday number for a day	
            wochentag = int(day.getElementsByTagName("weekday")[0].firstChild.data)
            if defglobal.debugg: myPrintp ("Process     weekday: %s" % wochentag)
# get off/on sequences for a weekday
            sequenzen = day.getElementsByTagName("sequence")	
#			myPrint  sequenzen
            if defglobal.debugg: myPrintp ("--------------------------------------")
            for sequenz in sequenzen:
                s+=1
#				myPrintp "Sequenz fuer Dose: ",dosennummer
                start = str(sequenz.getElementsByTagName("start")[0].firstChild.data)
                stop = str(sequenz.getElementsByTagName("stop")[0].firstChild.data)
#				myPrintp "Dose: ", dosennummer, "Wochentag: ", wochentag, "  ", start, "/", stop

# build a list for each sequence
                seqtmp.append(dosennummer)
                seqtmp.append(wochentag)
                seqtmp.append(start)
                seqtmp.append(stop)

                if defglobal.debugg: myPrintp ("Processing Dose %s  Wochentag %s " % (dosennummer,wochentag)	)		
# create action ON from a sequence
          
                action= [start,dosennummer,1]
                defglobal.tage[wochentag].append(action)
                action2=[start,1]                

                if defglobal.debugg: myPrintp ("Action1 für Dose: %s  Wochentag: %s Action: %s ON" % (dosennummer,wochentag,action[0]) )
                defglobal.tage2[wochentag][dosennummer].append(action2)
                action= [stop,dosennummer,0]
                defglobal.tage[wochentag].append(action)
                action2=[stop,0]
                defglobal.tage2[wochentag][dosennummer].append(action2)
        
                if defglobal.debugg: myPrintp ("Action2 für Dose: %s  Wochentag: %s Action: %s OFF" % (dosennummer,wochentag,action[0]) )
		
# build o list of sequence-lists			
                seq.append(seqtmp[:])
                seqtmp=[]
#				myPrint seq
# done with sequence -------------------------------------
            if defglobal.debugg: myPrintp ("Done with Sequence")
         
           
# done with a day ----------------------------------------
        if defglobal.debugg: myPrintp ("Done with Days")
#        print defglobal.defglobal.tage2

# done with dosen ----------------------------------------
    if defglobal.debugg: myPrintp ("Done with Dosen   ")

    for i in range(len(defglobal.tage)):
        x=defglobal.tage[i].pop(0)
        x=defglobal.tage[i].pop(0)
        defglobal.tage[i].sort()
    

							
    if defglobal.debugg: myPrintp ("Anzahl Dosen gefunden: %d" %d)
    if defglobal.debugg: myPrintp ("Anzahl Sequenzen gefunden: %d " %s)
    if defglobal.debug: myPrintp ("Done Parsing Inputfile\n")
#  return from parsing inputFile
    return(0)
# *************************************************


