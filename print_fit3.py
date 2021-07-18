#!/usr/bin/env python3
#
# Author: Gerhard Schmid
# License: MIT
# installiere Fitfileparser mit
#	pip3 install fitparse
# installiere Matplotlib mit
#	apt-get python3-matplotlib
###############################

from __future__ import division
from fitparse   import FitFile
from matplotlib import pyplot as plt
from mpl_toolkits.axes_grid1.inset_locator import inset_axes, zoomed_inset_axes
from mpl_toolkits.axes_grid1.anchored_artists import AnchoredSizeBar
from datetime   import datetime
import time
import numpy as np
#import sys
import os
from tkinter import *
from tkinter import filedialog
from cycler import cycler
import glob
from operator import add

###################################### Settings ####################################################
zonen = [0,138,149,160,170] # HF zone limits
FTP   = 255
lower_Plimit = int(FTP/2)
raeder = ('MTB','2er','Poison','Sab','Leihrad') # Bike names
#[0.81,0.9,0.94,1,1.03,1.07]
#tbPow = np.multiply([0,0.53,0.71,0.86,1],float(FTP))
tbPow = np.multiply([0,0.55,0.75,0.9,1.05],float(FTP)) # Power zones
smooth_Pprint = 600 # 
smooth_P30 = 30
max_hf = 180 # for scaling the plots
schwelle_zwischen =  3000

debug_print = 0 # show all records for debugging purposes
print_csv   = 0 # generate .csv file with result
plot_weg    = 1 # plot data vs. distance
plot_zeit   = 1 # plot data vs. time
plot_pause  = 1 # plot data vs. time including pauses (plot vs. Uhrzeit)
plot_hoehe  = 1 # plot altitude profile
CP          = 1 # calculate critical power?
Fitness     = 0 # correction of heart rate (for bad days)
bike_id     = 1 # default bike profile in case it can't be read from file
####################################################################################################

def smooth(y, box_pts):
    box = np.ones(box_pts)/box_pts
    y_smooth = np.convolve(y, box, mode='same')
    return y_smooth

list_of_files = glob.glob('[0-9]*.fit') # Search for newest Fitfile beginning with a number
latest_file = max(list_of_files, key=os.path.getctime)
print ("Neueste Ausfahrt: %s" % (latest_file))

fen1 = Tk()                              # Create window
fen1.title("FitFileParser")
T = Text(fen1, height=5, width=40)
T.pack()
T.insert(END, "Asking for filename\n\n")
name = filedialog.askopenfilename(filetypes=[("Fit files","*.fit")],initialfile=latest_file)
fitfile = FitFile(name)
csvdatei = name.replace('fit','csv')
T.insert(END, "Parsing %s\n" % (os.path.basename(name)))
if print_csv == 1:
	T.insert(END, "Will create %s\n" % (os.path.basename(csvdatei)))
else:
	T.insert(END, "\n")

T.insert(END, "Wait a moment...\n")

fen1.update()

#fitfile = FitFile('171028094355.fit')

def datetime_to_local(utc_datetime):
    now_timestamp = time.time()
    offset = datetime.fromtimestamp(now_timestamp) - datetime.utcfromtimestamp(now_timestamp)
    return utc_datetime + offset

x     = []
speed = [] # Geschwindigkeit vs. Fahrzeit
speedt= [] # Geschwindigkeit vs. Uhrzeit
xspeed= [] # Weg Achse für Geschwindigkeit
tspeed= [] # Uhrzeit Achse für Geschwindigkeit
hf    = [] # Herzfrequnez vs. Fahrzeit
hft   = [] # etc.
xhf   = []
thf   = []
power = []
powt  = []
xpow  = []
tpow  = []
cad   = []
cadt  = []
xcad  = []
tcad  = []
alt   = []
altt  = []
xalt  = []
talt  = []
T     = [] # Temperatur
tT    = []
# Get all data messages that are of type record
for record in fitfile.get_messages('record'):
	# Go through all the data entries in this record
	x.append(record.get_value('distance'))
	T.append(record.get_value('temperature'))
	zs = datetime_to_local(record.get_value('timestamp'))
	temp = zs.second + zs.minute*60 + zs.hour*3600
	try:
		if temp < t[-1]:
			temp = temp + 24*3600
		t.append(temp)
	except:
		t = [temp]
	temp = record.get_value('enhanced_speed')
	if (temp != None):
		speedt.append(temp*3.6)
		tspeed.append((t[-1]/float(3600)))
		speed.append(temp*3.6)
		xspeed.append(x[-1])
	hft.append(record.get_value('heart_rate'))
	try:
		thf.append(t[-1]/float(3600))
	except:
		del hft[-1]
	try:
	  if (speedt[-1] != 0):
	    hf.append(hft[-1])
	    xhf.append((x[-1]))
	except:
	  pass
	powt.append(record.get_value('power'))
	try:
		tpow.append(t[-1]/float(3600))
	except:
		del powt[-1]
	try:
	  if (speedt[-1] != 0):
	    power.append(powt[-1])
	    xpow.append(x[-1])
	except:
		pass

	altt.append(record.get_value('enhanced_altitude'))
	try:
		talt.append(t[-1]/float(3600))
	except:
		del altt[-1]
	try:
	  if (speedt[-1] != 0):
	    alt.append(altt[-1])
	    xalt.append(x[-1])
	except:
	  pass
	cadt.append(record.get_value('cadence'))
	try:
		tcad.append(t[-1]/float(3600))
	except:
		del cadt[-1]
	try:
	  if (speedt[-1] != 0):
	    cad.append(cadt[-1])
	    xcad.append(x[-1])
	except:
	  pass

if debug_print == 1:
	for record in fitfile.get_messages('record'):
		for record_data in record:
			if record_data.units:
				print(" * %s: %s %s" % (record_data.name, record_data.value, record_data.units))
			# Print the records name and value (and units if it has any)
			else:
				print(" * %s: %s" % (record_data.name, record_data.value))
		print()
	
# test what event stands for (SRM makes event for every stop)
# ereignis = []
# for event in fitfile.get_messages('event'):
# 	# Go through all the data entries in this record
# 	for record_data in event:
# 		if record_data.name == "timestamp":
# 			print(" * %s: %s" % (record_data.name, record_data.value))
# 			zs   = datetime_to_local(record_data.value)
# 			temp = zs.second + zs.minute*60 + zs.hour*3600
# 			ereignis.append(temp/3600)

class rstruct:
	x       = 0
	x_start = 0
	x_end   = 0
	zeit    = 0 # Fahrzeit
	t_start = 0 # t = Uhrzeit
	t_end   = 0
	z_start = 0
	z_end   = 0
	speed   = 0
	h       = 0
	m       = 0
	s       = 0
	gzeit   = 0 # Gesamtzeit
	HF      = 0
	power   = 0
	anstieg = 0
	v_max   = 0
	pos     = 0
	s_linie     = 0
	s_zeitlinie = 0
	s_pauslinie = 0
	e_linie     = 0
	e_zeitlinie = 0
	e_pauslinie = 0

Runden = []

for Laps in fitfile.get_messages('lap'):
	Runden.append(rstruct())
	print("Runde " + str(len(Runden)))
	for record_data in Laps:
		if record_data.name == "start_time":
			zs   = datetime_to_local(record_data.value)
			temp = zs.second + zs.minute*60 + zs.hour*3600
			Runden[-1].t_start = temp
			#Runden[-1].x_start = x[t.index(temp)]
			idx = (np.abs(np.asarray(t) - temp)).argmin()
			Runden[-1].z_start = idx
			Runden[-1].x_start = x[idx]
		if record_data.name == "timestamp":
			zs   = datetime_to_local(record_data.value)
			temp = zs.second + zs.minute*60 + zs.hour*3600
			Runden[-1].t_end = temp
			idx = (np.abs(np.asarray(t) - temp)).argmin()
			Runden[-1].z_end = idx
			Runden[-1].x_end = x[idx]
		if record_data.name == "total_distance":
			Runden[-1].x = record_data.value
		if record_data.name == "avg_speed":
			Runden[-1].speed = record_data.value*3.6
		if record_data.name == "total_timer_time":
			Runden[-1].zeit = record_data.value
		if record_data.name == "total_elapsed_time":
			Runden[-1].gzeit = record_data.value
		if record_data.name == "avg_heart_rate":
			Runden[-1].HF = record_data.value
			if Runden[-1].HF == None:
				Runden[-1].HF = 0
		if record_data.name == "avg_power":
			Runden[-1].power = record_data.value
			if Runden[-1].power == None:
				Runden[-1].power = 0
		if record_data.name == "total_ascent":
			Runden[-1].anstieg = record_data.value
		if record_data.name == "max_speed":
			Runden[-1].v_max = record_data.value*3.6
		if record_data.units:
			print(" * %s: %s %s" % (record_data.name, record_data.value, record_data.units))
		else:
			print(" * %s: %s" % (record_data.name, record_data.value))
		Runden[-1].h = np.floor(Runden[-1].zeit/3600)
		Runden[-1].m = np.floor((Runden[-1].zeit - Runden[-1].h*3600)/60)
		Runden[-1].s = Runden[-1].zeit - Runden[-1].h*3600 - Runden[-1].m*60
		Runden[-1].s_linie = Runden[-1].x_start/1000
		Runden[-1].s_zeitlinie = Runden[-1].z_start/3600
		Runden[-1].s_pauslinie = Runden[-1].t_start/3600
		Runden[-1].e_linie = Runden[-1].x_end/1000
		Runden[-1].e_zeitlinie = Runden[-1].z_end/3600
		Runden[-1].e_pauslinie = Runden[-1].t_end/3600
		Runden[-1].pos = ( (np.abs(np.array(xspeed) - Runden[-1].e_linie*1000)).argmin() )
	print()

# Check, ob zwischen den Runden > 5 km sind, dann mach eine zusätzliche Runde draus:
Zwischen = []
Alle     = Runden[:]
i = 0
if len(Runden) > 0:
	if (Runden[0].x_start - x[0]) > schwelle_zwischen:
		Zwischen.append(rstruct())
		Zwischen[-1].x_start = x[0]
		Zwischen[-1].x_end = Runden[0].x_start
		Zwischen[-1].z_start = 0
		Zwischen[-1].z_end = Runden[0].z_start
		Zwischen[-1].t_start = t[0]
		Zwischen[-1].t_end = Runden[0].t_start
		Zwischen[-1].x = Runden[0].x_start
		Zwischen[-1].zeit = Runden[0].z_start
		Alle.insert(0,Zwischen[-1])
	if len(Runden) > 1:
		for i in range(1,len(Runden)):
			if (Runden[i].x_start - Runden[i-1].x_end) > schwelle_zwischen:
				Zwischen.append(rstruct())
				Zwischen[-1].x = Runden[i].x_start - Runden[i-1].x_end
				Zwischen[-1].zeit = Runden[i].z_start - Runden[i-1].z_end
				Zwischen[-1].z_start = Runden[i-1].z_end
				Zwischen[-1].z_end = Runden[i].z_start
				Zwischen[-1].t_start = Runden[i-1].t_end
				Zwischen[-1].t_end = Runden[i].t_start
				Zwischen[-1].x_start = Runden[i-1].x_end
				Zwischen[-1].x_end = Runden[i].x_start
				Alle.insert(i,Zwischen[-1])
	if (x[-1] - Runden[-1].x_end) > schwelle_zwischen:
		Zwischen.append(rstruct())
		Zwischen[-1].x = x[-1] - Runden[-1].x_end
		Zwischen[-1].z_start = Runden[-1].z_end
		Zwischen[-1].z_end = len(hf)
		Zwischen[-1].t_start = Runden[-1].t_end
		Zwischen[-1].t_end = t[-1]
		Zwischen[-1].zeit = len(tspeed) - Runden[-1].z_end
		Zwischen[-1].x_start = Runden[-1].x_end
		Zwischen[-1].x_end = x[-1]
		Alle.append(Zwischen[-1])

for i in range(0,len(Zwischen)):
	Zwischen[i].h = np.floor(Zwischen[i].zeit/3600)
	Zwischen[i].m = np.floor((Zwischen[i].zeit - Zwischen[i].h*3600)/60)
	Zwischen[i].s = Zwischen[i].zeit - Zwischen[i].h*3600 - Zwischen[i].m*60
	Zwischen[i].speed = Zwischen[i].x/Zwischen[i].zeit*3.6
	Zwischen[i].v_max = max(speed[Zwischen[i].z_start:Zwischen[i].z_end])
	auf = np.diff(alt[Zwischen[i].z_start:Zwischen[i].z_end])
	auf[auf < 0] = 0
	Zwischen[i].anstieg = sum(auf) 
	try:
		hfz = np.array(hf[Zwischen[i].z_start:Zwischen[i].z_end])
		hfz = list(filter(None,hfz))
		Zwischen[i].HF = sum(hfz)/len(hfz)
	except:
		print("Keine HF für Zwischenstrecke verfuegbar")
	try:
		pz = np.array(power[Zwischen[i].z_start:Zwischen[i].z_end])
		pz = list(filter(None,pz))
		Zwischen[i].power = sum(pz)/len(pz)
	except:
		print("Keine Leistung für Zwischenstrecke verfuegbar")


for Summary in fitfile.get_messages('session'):
	print("Zusammenfassung")
	print("===============")
	for record_data in Summary:
		if record_data.name == "total_distance":
			strecke = record_data.value
		if record_data.name == "avg_speed":
			avspeed = record_data.value*3.6
		if record_data.name == "total_timer_time":
			zeit = record_data.value
		if record_data.name == "avg_heart_rate":
			HF = record_data.value
		if record_data.name == "normalized_power":
			NP = record_data.value
		if record_data.name == "total_ascent":
			anstieg = record_data.value
		if record_data.name == "total_discent":
			abstieg = record_data.value
		if record_data.name == "max_speed":
			v_max = record_data.value*3.6
		if record_data.name == "total_calories":
			kCal = record_data.value
		if record_data.name == "total_work":
			if (record_data.value != None):
				if (record_data.value > 0):
					kCal = record_data.value/1000
		if record_data.name == "total_elapsed_time":
			totalzeit = record_data.value
		if record_data.name == "avg_cadence":
			kadenz = record_data.value
		if record_data.name == "start_time":
			startzeit = record_data.value
		if record_data.name == "sport":
			sport = record_data.value
		if record_data.units:
			print(" * %s: %s %s" % (record_data.name, record_data.value, record_data.units))
		else:
			print(" * %s: %s" % (record_data.name, record_data.value))
	print()

for file_id in fitfile.get_messages('file_id'):
	for record_data in file_id:
		if record_data.name == "manufacturer":
			hersteller = record_data.value
			print('Hersteller erkannt: %s' % (hersteller))

km = [0,0,0,0,0]
bike = "Default"
id = 1
bike_id = 1
if hersteller == "srm":
	for bike_profile in fitfile.get_messages('bike_profile'):
		for record_data in bike_profile:
			if record_data.name == "name":
				bike = record_data.value
				bike_id = int(bike[-1])

				totfile = FitFile('Totals.fit')
				for totals in totfile.get_messages('unknown_65292'):
					for record_data in totals:
						if (record_data.name == "unknown_0"): 
							id = record_data.value	
							#print(" * %s: %s" % (record_data.name, record_data.value))
						if record_data.name == "unknown_3":	
							km[id] = record_data.value/1000
				bike = raeder[bike_id - 1]
				id = bike_id

# Bei Igpsport finde ich keinen Hinweise auf Radprofil, kann über Gewicht unterscheiden (alternativ Sensor-Id):
elif hersteller == "igpsport":
	totfile = FitFile('user.fit')
	for totals in totfile.get_messages('bike_profile'):
		for record_data in totals:
			if (record_data.name == "bike_weight"):
				bike_weight = record_data.value
				if bike_weight == 8:
					bike_id = 1
				elif bike_weight == 6:
					bike_id = 2
				elif bike_weight == 7:
					bike_id = 3
				else:
					bike_id = 4
				id = bike_id
				bike = raeder[bike_id - 1]
	for totals in totfile.get_messages('bike_profile'):
		for record_data in totals:
			if (record_data.name == "odometer"): 
				km[bike_id] = record_data.value/1000

elif hersteller == "bryton":
	for bike_profile in fitfile.get_messages('unknown_68'):
		for record_data in bike_profile:
			if (record_data.name == "unknown_7"): 
				id = record_data.value
				bike_id = id
				bike = raeder[0]
				if (id == 2):
					bike_id = 3
				elif (id == 0x10):
					bike_id = 2
				elif (id == 0x20):
					bike_id = 4
				bike = raeder[bike_id - 1]
				#Beim Rider 450 ist 0x10 Rad 1 und 0x20 Rad 2, daher:
				if id > 2:
					id = id >> 4

				#Remove \x00 at the end of the file (Korean coding?)
				fileObject = open("System.ini", "r")
				data = fileObject.read()
				data = data.rstrip('\x00')
				fileObject.close()
				fileObject = open("System.ini", "w")
				fileObject.write(data)
				fileObject.close()
				import configparser
				config = configparser.ConfigParser()
				config.read	("System.ini")
				system = config['System']
				trip2_str =('Trip2%d_km' % (id))
				km[bike_id] = system[trip2_str]
if hersteller == "garmin":
	for Summary in fitfile.get_messages('session'):
		for record_data in Summary:
			if record_data.name == "unknown_110":
				bike = record_data.value
			if record_data.name == "unknown_178":
				km[bike_id] = record_data.value
else:
	print('Hersteller nicht implementiert, kann Odometer nicht lesen')

kmstr = [' ;',' ;',' ;',' ;',' ;',' ;']
kmstr[bike_id] = ("%s;" % str(km[bike_id]))
kmstr = ('%s%s%s%s%s%s' % (kmstr[0],kmstr[1],kmstr[2],kmstr[3],kmstr[4],kmstr[5]))
print("Rad: %s  (id: %d), Kilometerstand: %s" % (bike,id,str(km[bike_id])))
print("===============")
print()


if (NP == None):
  NP = 0

startzeit  = datetime_to_local(startzeit)

h = np.floor(zeit/3600)
m = np.floor((zeit - h*3600)/60)
s = zeit - h*3600 - m*60

pausenzeit = totalzeit - zeit
hp = np.floor(pausenzeit/3600)
mp = np.floor((pausenzeit - hp*3600)/60)
sp = pausenzeit - hp*3600 - mp*60
#hf = list(map(add, hf, [Fitness]*len(hf)))

# Replace all 'None' by 0s and calc. mean excluding zeros:
hf    = np.array([e if e != None else 0 for e in hf])
af    = np.mean(hf[hf > 0])
if np.isnan(af):
	af = 0
cad   = np.array([e if e != None else 0 for e in cad])
ac    = np.mean(cad[cad > 0])
if np.isnan(ac):
	ac = 0

power = np.array([e if e != None else 0 for e in power])
powt   = [e if e != None else 0 for e in powt]
powt   = smooth(powt,smooth_Pprint)
Pprint = smooth(power,smooth_Pprint)
P30    = smooth(power,smooth_P30)
NPcalc = int(np.sqrt(np.sqrt(np.mean(np.power(P30[P30 > 0],4)))))
print("Normierte Leistung Gerät/Berechnet:  %d/%d W" % (NP,NPcalc))

if (NP == 0):
	if (af == 0):
		print("Keine Leistung und keine HF verfuegbar, schaetze TSS mit 80% Intensitaet")
		tss = int(zeit/3600*80)
	else:
		tss = int(zeit/3600*af/zonen[4]*100)
else:
    tss = (NP/float(FTP)*zeit/3600*100)
print("TSS = %d" % (tss))

stretch_power = 1
if max(Pprint) > 0:
	while max(Pprint)*stretch_power < (max_hf/2*1.1):
		stretch_power = stretch_power*2
	while max(Pprint)*stretch_power > (max_hf*1.1):
		stretch_power = stretch_power/2
	print ("stretch_power: " + str(stretch_power))

stretch_T = 10
while max(T)*stretch_T < (max_hf/2*1.1):
	stretch_T = stretch_T*2
while max(T)*stretch_T > (max_hf*1.1):
	stretch_T = stretch_T/2
print ("stretch_temperature: " + str(stretch_T))


TB = np.zeros(len(zonen)+1)
strZonen  = " "
#print(range(0,len(zonen)))
for i in range(0,(len(zonen))):
  if i == (len(zonen)-1):
    if (NP == 0):
      TB[i] = sum(j > zonen[i]  for j in list(filter(None,hf)))
      messageZ = ("(HF >%2d Schläge) " % (zonen[i])) 
    else:
      TB[i] = sum(j > tbPow[i]  for j in list(filter(None,P30)))
      messageZ = ("(>%2d W) " % (tbPow[i]))
  else:
    if (NP == 0):
      TB[i] = sum(((j > zonen[i]) and (j <= zonen[i+1])) for j in list(filter(None,hf)))
      messageZ = ("(HF %2d - %2d) " % (zonen[i],zonen[i+1])) 
    else:
      TB[i] = sum(((j > tbPow[i]) and (j <= tbPow[i+1])) for j in list(filter(None,P30)))
      messageZ = ("(%2d - %2d W) " % (tbPow[i],tbPow[i+1]))

  hz = np.floor(TB[i]/3600)
  mz = np.floor((TB[i] - hz*3600)/60)
  sz = TB[i] - hz*3600 - mz*60
  print("Training in Zone %d: %02d:%02d:%02d " % (i,hz,mz,sz) + messageZ)
  strZonen = ("%s %2d:%2d:%2d;" % (strZonen,hz,mz,sz))

rstr = ("%0.2f; %0.1f; %02d:%02d:%02d; %0.1f; %02d" % (strecke/1000,avspeed,h,m,s,v_max,kCal))
rstr = ("%s ; %02d; %02d; %02d; %02d; %02d; %s %02d:%02d:%02d; %s;;" % (rstr,af,NP,ac,anstieg,tss,kmstr,hp,mp,sp,strZonen))
for i in range(0,len(Alle)):
	rstr = (rstr+" %0.2f; %0.2f; %02d:%02d:%02d; %02d; %02d; %02d; %0.1f;" % (Alle[i].x/1000, Alle[i].speed,Alle[i].h,Alle[i].m,Alle[i].s,Alle[i].HF,Alle[i].power,Alle[i].anstieg,Alle[i].v_max))
rstr = rstr.replace('.',',')
rstr = ("%d.%d.; ;%d;%2d:%2d:%2d;%s" % (startzeit.day,startzeit.month,bike_id,startzeit.hour,startzeit.minute,startzeit.second,rstr))

print("Markiere diese Zeile inklusive \">\" und kopiere sie in die Tabelle: ")
print(rstr)
print(">")

ueberschrift1 = "Allgemein;;;;;Zusammenfassung;;;;;;;;;;km-Stand;;;;;;Trainingsbereiche;;;;;;;"
for i in range(0,len(Runden)):
	ueberschrift1 = (ueberschrift1 + "Runde %d;;;;;;" % (i+1))
ueberschrift2 = ("Datum;Strecke;Rad;Start;Ges.-km;av;Ges.zeit;max;kCal;Puls;Leistung;Kad;hm;tss;stress;" + (((str(raeder)).replace(',',';')).replace('(','')).replace(')','') + ";Pausenzeit;TB0;TB1;TB2;TB3;TB4;Anm.;Rad - rep;")
for i in range(0,len(Runden)):
	ueberschrift2 = (ueberschrift2 + "km;av;Zeit;Puls;Power;hm;max;")

if (print_csv == 1):
	#csvdatei = ("%s.csv" % (startzeit.strftime("%y%m%d%H%M")))
	file = open(csvdatei,"w")
	#file.write("\"sep=;\"\r\n")
	file.write(ueberschrift1 + "\r\n")
	file.write(ueberschrift2 + "\r\n")
	file.write(rstr)
	file.close

############## Plots:
try:
	cad = np.array(cad)
	cad[cad > 130] = None
	cad[cad < 30] = None
	gnd = min(alt) - min(alt)%50
except:
	print("Keine Kadenz verfuegbar")

stretch_speed = 1
if max(speed) > 0:
	while max(speed)*stretch_speed < max_hf/2*1.1:
		stretch_speed = stretch_speed*2

print("stretch_speed: " + str(stretch_speed))
print("Fuer die Korrektur: ")
print(strZonen)
print(">")

fen1.destroy()

################# Nach Weg: ###########################################################################

if plot_weg == 1:
	plt.xkcd()
	fig = plt.figure()
	ax = fig.add_subplot(1, 1, 1)
	ax.set_prop_cycle(cycler('color', ['c', 'b', 'r', 'm', 'k']))
	ax.set_title("%s on %s" % (sport,startzeit.strftime("%A, %b. %d, %Y")))
	ax.set_ylim([0,max_hf])
	ax.grid(color='k', linestyle=':', linewidth=1)
	plt.xlabel('Distance (km)')
	plt.ylabel('Cadence, Speed, HF')
	ax2 = ax.twinx()
	ax2.set_prop_cycle(cycler('color', ['k']))
	ax2.set_ylabel('Altitude')

	plt.rc('lines', linewidth=2)

	for i in range(0,len(Runden)):
	  ax.text(np.mean([Runden[i].s_linie,Runden[i].e_linie]), 170,("Runde %d"%(i+1)),color='y')
	  ax.text(np.mean([Runden[i].s_linie,Runden[i].e_linie]), 161,("%d km"%(Runden[i].x/1000)),color='y')
	  ax.text(np.mean([Runden[i].s_linie,Runden[i].e_linie]), 152,("%d km/h"%(round(Runden[i].speed))),color='y')
	  ax.text(np.mean([Runden[i].s_linie,Runden[i].e_linie]), 143,("%d HS"%(Runden[i].HF)),color='y')
	  ax.text(np.mean([Runden[i].s_linie,Runden[i].e_linie]), 134,("%d W"%(Runden[i].power)),color='y')
	  ax.text(np.mean([Runden[i].s_linie,Runden[i].e_linie]), 125,("%02d:%02d:%02d" % (Runden[i].h,Runden[i].m,Runden[i].s)),color='y')
	  ax.vlines(Runden[i].s_linie,[0],[200],lw=2,color='y')
	  ax.vlines(Runden[i].e_linie,[0],[200],lw=2,color='y')
	# if len(Runden) > 0:
	#     ax.text(np.mean([Runden[i].e_linie,sum(Runden[i].x)/1000]), 170,("Runde %d"%(i+1)),color='y')
	#     ax.text(np.mean([Runden[i].e_linie,sum(Runden[i].x)/1000]), 161,("%d km/h"%(Runden[i].speed)),color='y')
	#     ax.text(np.mean([Runden[i].e_linie,sum(Runden[i].x)/1000]), 152,("%d HS"%(Runden[i].HF)),color='y')
	#     ax.text(np.mean([Runden[i].e_linie,sum(Runden[i].x)/1000]), 143,("%d km"%(Runden[i].x/1000)),color='y')
	#     ax.text(np.mean([Runden[i].e_linie,sum(Runden[i].x)/1000]), 134,("%02d:%02d:%02d" % (Runden[i].h,Runden[i].m,Runden[i].s)),color='y')
	for i in range(0,len(Zwischen)):
		ax.text(np.mean([Zwischen[i].x_start,Zwischen[i].x_end])/1000, 170,("Zwischen %d"%(i+1)),color='y')
		ax.text(np.mean([Zwischen[i].x_start,Zwischen[i].x_end])/1000, 161,("%d km"%(Zwischen[i].x/1000)),color='y')
		ax.text(np.mean([Zwischen[i].x_start,Zwischen[i].x_end])/1000, 152,("%d km/h"%(round(Zwischen[i].speed))),color='y')
		ax.text(np.mean([Zwischen[i].x_start,Zwischen[i].x_end])/1000, 143,("%d HS"%(Zwischen[i].HF)),color='y')
		ax.text(np.mean([Zwischen[i].x_start,Zwischen[i].x_end])/1000, 134,("%d W"%(Zwischen[i].power)),color='y')
		ax.text(np.mean([Zwischen[i].x_start,Zwischen[i].x_end])/1000, 125,("%02d:%02d:%02d" % (Zwischen[i].h,Zwischen[i].m,Zwischen[i].s)),color='y')

	ax.plot(np.divide(xcad,1000),cad,lw=0.5, label = "Cadence")
	ax.plot(np.divide(xspeed,1000),np.multiply(speed,stretch_speed), label='Speed$\cdot$'+str(stretch_speed))
	ax.plot(np.divide(xhf,1000),hf, label="HF")
	ax.plot(np.divide(xpow,1000),np.multiply(Pprint,stretch_power), label='Power$\cdot$'+str(stretch_power),lw=1)
	ax.plot([-1,-1],[0, 1],lw=1,label = 'Altitude')
	ax.hlines(zonen,[0],[max(x)/1000],lw=1,colors='r')
	ax.hlines(tbPow*stretch_power,[0],[max(x)/1000],lw=1,colors='m')
	if plot_hoehe == 1:
	    ax2.plot(np.divide(xalt,1000),alt,lw=1)
	ax2.set_xlim([0,max(x)/1000])

	ax.legend(loc='best')
	#ax.legend(('Cadence','Speed$\cdot$'+str(stretch_speed),'HF','Altitude'),'best')

	labels = 'TB0','TB1','TB2','TB3','TB4'
	TB = TB[0:5]
	explode = (0.05, 0.05, 0.05, 0.5,1)
	colors = ['lightskyblue', 'yellowgreen', 'yellow', 'orange', 'lightcoral']
	axins = inset_axes(ax,
			  width=1.5,  # width = 30% of parent_bbox
			  height=1.5,  # height : 1 inch
			  loc=3)
	patches, texts, autotexts = plt.pie(TB, explode=explode, colors=colors, labels=labels, startangle=90,
		autopct='%.0f%%', shadow=True, radius=1)
	# Make the labels on the small plot easier to read.
	for te in texts:
	    te.set_size('smaller')
	for te in autotexts:
	    te.set_size('x-small')
	autotexts[0].set_color('y')

	fig.patch.set_alpha(0)
	ax2.patch.set_alpha(0.5)
	axins.patch.set_alpha(1)

	plt.show()

################# Nach Zeit (ohne Pausen): ###########################################################################

if plot_zeit == 1:
	plt.xkcd()

	fig = plt.figure()
	ax = fig.add_subplot(1, 1, 1)
	ax.set_prop_cycle(cycler('color', ['c', 'b', 'r', 'm', 'k']))
	ax.set_title("%s on %s" % (sport,startzeit.strftime("%A, %b. %d, %Y")))
	ax.set_ylim([0,max_hf])
	ax.grid(color='k', linestyle=':', linewidth=1)
	ax.hlines(zonen,[0],[totalzeit],lw=1)
	#ax.vlines(np.divide(pos,3600),[0],[200],lw=2,color='y')
	#pos = (totalzeit))
	#for i in range(1,len(Runden)+1):
	  #ax.text(np.mean([pos[i-1],pos[i]])/3600, 170,("Runde %d"%(i)),color='y')
	#if len(Runden) > 0:
	  #ax.text(np.mean([pos[i]/3600,sum(Runden[i].zeit)/3600]), 170,("Runde %d"%(i+1)),color='y')
	for i in range(0,len(Runden)):
	  ax.text(np.mean([Runden[i].s_zeitlinie,Runden[i].e_zeitlinie]), 170,("Runde %d"%(i+1)),color='y')
	  ax.text(np.mean([Runden[i].s_zeitlinie,Runden[i].e_zeitlinie]), 161,("%d km"%(Runden[i].speed)),color='y')
	  ax.text(np.mean([Runden[i].s_zeitlinie,Runden[i].e_zeitlinie]), 152,("%02d:%02d:%02d" % (Runden[i].h,Runden[i].m,Runden[i].s)),color='y')
	  ax.vlines(Runden[i].s_zeitlinie,[0],[200],lw=2,color='y')
	  ax.vlines(Runden[i].e_zeitlinie,[0],[200],lw=2,color='y')
	for i in range(0,len(Zwischen)):
		ax.text(np.mean([Zwischen[i].z_start,Zwischen[i].z_end])/3600, 170,("Zwischen %d"%(i+1)),color='y')
		ax.text(np.mean([Zwischen[i].z_start,Zwischen[i].z_end])/3600, 161,("%d km"%(Zwischen[i].x/1000)),color='y')
		ax.text(np.mean([Zwischen[i].z_start,Zwischen[i].z_end])/3600, 152,("%02d:%02d:%02d" % (Zwischen[i].h,Zwischen[i].m,Zwischen[i].s)),color='y')

	plt.xlabel('Time (h)')
	plt.ylabel('Cadence, Speed, HF')
	ax2 = ax.twinx()
	ax2.set_prop_cycle(cycler('color', ['k']))
	ax2.set_ylabel('Altitude')

	plt.rc('lines', linewidth=2)

	ax.plot(np.linspace(0,len(T)/3600,len(T)),np.multiply(T,stretch_T),lw=0.2, color="orange", label = "Temperature$\cdot$"+str(stretch_T))
	ax.plot(np.linspace(0,len(cad)/3600,len(cad)),cad,lw=0.5, label = "Cadence")
	ax.plot(np.linspace(0,len(speed)/3600,len(speed)),np.multiply(speed,stretch_speed), label='Speed$\cdot$'+str(stretch_speed))
	ax.plot(np.linspace(0,len(hf)/3600,len(hf)),hf, label="HF")
	ax.plot(np.linspace(0,len(Pprint)/3600,len(Pprint)),np.multiply(Pprint,stretch_power), label='Power$\cdot$'+str(stretch_power),lw=1)
	ax.plot([-1,-1],[0, 1],lw=1,label = 'Altitude')
	if plot_hoehe == 1:
	    ax2.plot(np.linspace(0,len(alt)/3600,len(alt)),alt,lw=1)
	ax.set_xlim([0,len(speed)/3600])

	ax.legend(loc='best')
	#ax.legend(('Cadence','Speed$\cdot$'+str(stretch_speed),'HF','Altitude'),'best')

	plt.show()

################# Nach Uhrzeit: ###########################################################################

if plot_pause == 1:
	plt.xkcd()

	fig = plt.figure()
	ax = fig.add_subplot(1, 1, 1)
	ax.set_prop_cycle(cycler('color', ['c', 'b', 'r', 'm', 'k']))
	ax.set_title("%s on %s" % (sport,startzeit.strftime("%A, %b. %d, %Y")))
	ax.set_ylim([0,max_hf])
	ax.grid(color='k', linestyle=':', linewidth=1)
	ax.hlines(zonen,[t[0]/3600],[t[-1]/3600],lw=1)
	# ax.vlines(ereignis,[0],[200],lw=2,color='g')
	for i in range(0,len(Runden)):
		ax.vlines(Runden[i].s_pauslinie,[0],[200],lw=2,color='y')
		ax.vlines(Runden[i].e_pauslinie,[0],[200],lw=2,color='y')
		ax.text(np.mean([Runden[i].s_pauslinie,Runden[i].e_pauslinie]), 170,("Runde %d"%(i+1)),color='y')
	for i in range(0,len(Zwischen)):
		ax.text(np.mean([Zwischen[i].t_start,Zwischen[i].t_end])/3600, 170,("Zwischen %d"%(i+1)),color='y')
	plt.xlabel('Time (h)')
	plt.ylabel('Cadence, Speed, HF')
	ax2 = ax.twinx()
	ax2.set_prop_cycle(cycler('color', ['k']))
	ax2.set_ylabel('Altitude')

	plt.rc('lines', linewidth=2)

	#ax.plot(np.linspace(0,len(cad)/3600,len(cad)),cad,lw=0.5, label = "Cadence")
	ax.plot(tcad,cadt,lw=0.5, label = "Cadence")
	ax.plot(tspeed,np.multiply(speedt,stretch_speed), label='Speed$\cdot$'+str(stretch_speed))
	#ax.plot(np.linspace(0,len(thf)/3600,len(hft)),hft, label="HF")
	ax.plot(thf,hft, label="HF")
	ax.plot(tpow,np.multiply(powt,stretch_power), label='Power$\cdot$'+str(stretch_power),lw=1)
	ax.plot([-1,-1],[0, 1],lw=1,label = 'Altitude')
	#ax2.plot(np.linspace(0,len(alt)/3600,len(alt)),alt,lw=1)
	if plot_hoehe == 1:
	    ax2.plot(talt,altt,lw=1)
	ax.set_xlim([t[0]/3600,t[-1]/3600])

	ax.legend(loc='best')
	#ax.legend(('Cadence','Speed$\cdot$'+str(stretch_speed),'HF','Altitude'),'best')

	plt.show()

# Critical Power:
if CP == 1:
	steps = 30
	max_interval = 300*60
	step_size = int(max_interval/steps)
	Int   = [0]*int(max(power))
	Pint  = [0]*int(max(power))
	Int2  = [0]*len(range(1,steps+1))
	Pint2 = [0]*len(range(1,steps+1))
	# Methode 1: schau, wie viele Sekunden über bestimmter Leistung waren, unabhängig, ob zusammenhängendes Intervall
	for i in range(lower_Plimit,len(Pint)):
		Int[i] = i
		Pint[i] = len(power[power > i])
	# Methode 2: smoothen über Intervalllänge, nimm maximum, d.h. nur zusammenhängende Intervalle werden genommen, aber Durchnitt
	Int2[0] = max(P30)
	Pint2[0] = 30 # Vergrößere Intervalle um je 5 min (sonst dauerts extrem lange)
	for i in range(1,steps):
		print('Berechne max. Leistung für %d min (bis %d)...' % (i*step_size/60, max_interval/60), end='\r')
		Psmooth = smooth(power,i*step_size)
		Int2[i] = max(Psmooth)
		Pint2[i] = i*step_size# Vergrößere Intervalle um je 5 min (sonst dauerts extrem lange)
	print('\nFertig!')

	plt.xkcd()
	fig = plt.figure()
	ax = fig.add_subplot(1, 1, 1)
	ax.grid(color='k', linestyle=':', linewidth=1)
	plt.xlabel('Intervall (min)')
	plt.ylabel('Leistung (W)')
	# ax.plot(np.divide(Pint[lower_Plimit:-1],60),np.linspace((lower_Plimit + 1),len(Pint)-(lower_Plimit + 1),len(Pint)-(lower_Plimit + 1))+(lower_Plimit + 1),lw=2, color="blue", label = "Critical Power")
	ax.plot(np.divide(Pint[lower_Plimit:-1],60),Int[lower_Plimit:-1],lw=2, color="blue", label = "Critical Power, Method 1")
	ax.plot(np.divide(Pint2,60),Int2,lw=2, color="green", label = "Critical Power, Method 2")
	ax.legend(loc='best')

	plt.show()
