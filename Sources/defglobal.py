#!/usr/bin/python
# coding: utf-8
#
#  Global Variables für Switcher-Daemon --------------------
#
work=1     # default value: 1 means keep on working
forep=1  # default value für Vordergund Run - steuert Function myPrint
z_send = 1


# for receiving messages
z_recv = 1
must_send=0
debug=0
sim=0
i=0
term=0
logging=0
status=0
anzerr=0
status_status=0
status_dosenstatus=[0,0,0,0]        # interner Dosenstatus, wird auch bei not at home nachgeführt, damit wieder richtig angezündet werden kann, wenn Peter heim kommt
status_dosenstatus_ext=[0,0,0,0]    # externer Status, zeigt den Status der 4 Dosen in jedem Moment, wird vom Client angezeigt, alle 0 bei at home
#                                       bei at home sind alle dosen off - wir müssen aber wissen, welche einzuschalten sind, wenn not at home eintritt
#                                       erweitert am 7. April 2015
status_dose=0
status_anzactions=0             # Anzahl Actions durchgeführt seit Start
status_waitaction=""
status_weekday=0                # aktueller wochentag
status_waitfor=""               # Zeit der nöchsten, in der Zukunft liegenden Aktion
status_currtime=""
status_lastaction="none"        # was wurde zuletzt geschaltet
controlfile=""
startdat =""                    # Startdatum/Zeit Programmstart
control_id=" "      # Identifikation (Text) des XML-Files.
forep=0             # runs in forground (no daemon)
tage=list()			# List of Lists of List für Tage, Aktionsliste, Aktion
tage2=list()
doseli=list()
control_id=" "      # Identifikation (Text) des XML-Files.
debug=0			    # debug switch, simple debug
debugg=0			# debug switch, voller debug
i_am_home=1         # I am home status - switch is checked once in main loop
                    # 1 = not at home switch normally
                    # 0 = at home, do not switch light
i_am_home_old=0       # to check for change




#
#
#-------------------------------------




