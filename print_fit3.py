#!/usr/bin/env python3
#
# Author: Gerhard Schmid
# License: MIT
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
raeder = ('MTB','2er','Poison','Sab','Leihrad') # Bike names
#[0.81,0.9,0.94,1,1.03,1.07]
#tbPow = np.multiply([0,0.53,0.71,0.86,1],float(FTP))
tbPow = np.multiply([0,0.55,0.75,0.9,1.05],float(FTP)) # Power zones
smooth_pow_print = 600 # 
smooth_pow_zonen = 30
max_hf = 180 # for scaling the plots

print_alles = 0 # show all records for debugging purposes
print_csv   = 0 # generate .csv file with result
plot_weg    = 1 # plot data vs. distance
plot_time   = 1 # plot data vs. time
plot_pause  = 1 # plot data vs. time including pauses (plot vs. Uhrzeit)
plot_hoehe  = 1 # plot altitude profile
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
name= filedialog.askopenfilename(filetypes=[("Fit files","*.fit")],initialfile=latest_file)
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
speed = []
speedt= []
xspeed= []
tspeed= []
hf    = []
hft   = []
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
	for record_data in record:
		if record_data.name == "timestamp":
			zs   = datetime_to_local(record_data.value)
			temp = zs.second + zs.minute*60 + zs.hour*3600
			try:
				if temp < t[-1]:
					temp = temp + 24*3600
				t.append(temp)
			except:
				t = [temp]
		if record_data.name == "distance":
			x.append((record_data.value))
		if (record_data.name == "enhanced_speed") and (record_data.value != None) :
			speedt.append((record_data.value*3.6))
			try:
				tspeed.append((t[-1]/float(3600)))
			except:
				del speedt[-1]
			if (record_data.value != 0):
			  speed.append((record_data.value*3.6))
			  xspeed.append((x[-1]))
		if record_data.name == "heart_rate":
			hft.append((record_data.value))
			try:
				thf.append((t[-1]/float(3600)))
			except:
				del hft[-1]
			try:
			  if (speedt[-1] != 0):
			    hf.append((record_data.value))
			    xhf.append((x[-1]))
			except:
			  pass
			  #print("no speed found for this (first?) point")

		if (record_data.name == "power"):# and (record_data.value != None):
			powt.append((record_data.value))
			try:
				tpow.append((t[-1]/float(3600)))
			except:
				del powt[-1]
			try:
			  if (speedt[-1] != 0):
			    power.append((record_data.value))
			    xpow.append((x[-1]))
			except:
			  pass
			  #print("no speed found for this (first?) point")

		if record_data.name == "enhanced_altitude":
#			if record_data.value > 0:
			altt.append((record_data.value))
			try:
				talt.append((t[-1]/float(3600)))
			except:
				del altt[-1]
			try:
			  if (speedt[-1] != 0):
			    alt.append((record_data.value))
			    xalt.append((x[-1]))
			except:
			  pass

		if record_data.name == "temperature":
			T.append((record_data.value))

		if record_data.name == "cadence":
			#if (((record_data.value == None) or (record_data.value == 0)) and (cad != [])):
				#cad.append((cad[-1]))
			#else:
			cadt.append((record_data.value))
			try:
				tcad.append((t[-1]/float(3600)))
			except:
				del cadt[-1]
			try:
			  if (speedt[-1] != 0):
			    cad.append((record_data.value))
			    xcad.append((x[-1]))
			except:
			  pass
			    
		if print_alles == 1:
			if record_data.units:
				print(" * %s: %s %s" % (record_data.name, record_data.value, record_data.units))
			# Print the records name and value (and units if it has any)
			else:
				print(" * %s: %s" % (record_data.name, record_data.value))
	if print_alles == 1:
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
	x_start = 0
	x_end   = 0
	t_start = 0
	t_end   = 0
	z_start = 0
	z_end   = 0
	strecke = 0
	avspeed = 0
	zeit    = 0
	gzeit   = 0
	avHR    = 0
	power   = 0
	anstieg = 0
	v_max   = 0

runde     = 0
Runden = []

for Laps in fitfile.get_messages('lap'):
	runde = runde + 1
	Runden.append(rstruct())
	print("Runde " + str(runde))
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
			Runden[-1].strecke = record_data.value
		if record_data.name == "avg_speed":
			Runden[-1].avspeed = record_data.value*3.6/1000
		if record_data.name == "total_timer_time":
			Runden[-1].zeit = record_data.value
		if record_data.name == "total_elapsed_time":
			Runden[-1].gzeit = record_data.value
		if record_data.name == "avg_heart_rate":
			Runden[-1].avHR = record_data.value
			if Runden[-1].avHR == None:
				Runden[-1].avHR = 0
		if record_data.name == "avg_power":
			Runden[-1].power = record_data.value
			if Runden[-1].power == None:
				Runden[-1].power = 0
		if record_data.name == "total_ascent":
			Runden[-1].anstieg = record_data.value
		if record_data.name == "max_speed":
			Runden[-1].v_max = record_data.value*3.6/1000
		if record_data.units:
			print(" * %s: %s %s" % (record_data.name, record_data.value, record_data.units))
		else:
			print(" * %s: %s" % (record_data.name, record_data.value))
	print()

# Check, ob zwischen den Runden > 5 km sind, dann mach eine zusätzliche Runde draus:
zwischen = 0
x_zw_start = [] # Distanz Zwischen Start
x_zw_end   = [] # Distanz Zwischen Ende
z_zw_start = [] # Zeit Zwischen Start
z_zw_end   = []
t_zw_start = [] # Uhrzeit Zwischen Start, etc.
t_zw_end   = []
x_zw       = []
z_zw       = []
i = 0
if runde > 0:
	if (Runden[0].x_start - x[0]) > 5000:
		zwischen = zwischen + 1
		x_zw_start.append(x[0])
		x_zw_end.append(Runden[0].x_start)
		z_zw_start.append(0)
		z_zw_end.append(Runden[0].z_start)
		t_zw_start.append(t[0])
		t_zw_end.append(Runden[0].t_start)
		x_zw.append(Runden[0].x_start)
		z_zw.append(Runden[0].z_start)
	if runde > 1:
		for i in range(1,runde):
			if (Runden[i].x_start - Runden[i-1].x_end) > 5000:
				zwischen = zwischen + 1
				x_zw.append(Runden[i].x_start - Runden[i-1].x_end)
				z_zw.append(Runden[i].z_start - Runden[i-1].z_end)
				z_zw_start.append(Runden[i-1].z_end)
				z_zw_end.append(Runden[i].z_start)
				t_zw_start.append(Runden[i-1].t_end)
				t_zw_end.append(Runden[i].t_start)
				x_zw_start.append(Runden[i-1].x_end)
				x_zw_end.append(Runden[i].x_start)
	if (x[-1] - Runden[-1].x_end) > 5000:
		zwischen = zwischen + 1
		x_zw.append(x[-1] - Runden[-1].x_end)
		z_zw_start.append(Runden[i-1].z_end)
		z_zw_end.append(len(hf))
		t_zw_start.append(Runden[i-1].t_end)
		t_zw_end.append(t[-1])
		z_zw.append(len(tspeed) - Runden[i-1].z_end)
		x_zw_start.append(Runden[-1].x_end)
		x_zw_end.append(x[-1])

zh     = [0]*zwischen
zm     = [0]*zwischen
zs     = [0]*zwischen
v_zw   = [0]*zwischen
hf_zw  = [0]*zwischen
pow_zw = [0]*zwischen
for i in range(0,zwischen):
	v_zw[i] = x_zw[i]/z_zw[i]
	zh[i] = np.floor(z_zw[i]/3600)
	zm[i] = np.floor((z_zw[i] - zh[-1]*3600)/60)
	zs[i] = z_zw[i] - zh[-1]*3600 - zm[-1]*60
	try:
		hfz = np.array(hf[z_zw_start[i]:z_zw_end[i]])
		hfz = list(filter(None,hfz))
		hf_zw[i] = sum(hfz)/len(hfz)
	except:
		print("Keine HF für Zwischenstrecke verfuegbar")
	try:
		pz = np.array(power[z_zw_start[i]:z_zw_end[i]])
		pz = list(filter(None,pz))
		pow_zw[i] = sum(pz)/len(pz)
	except:
		print("Keine Leistung für Zwischenstrecke verfuegbar")


for Summary in fitfile.get_messages('session'):
	print("Zusammenfassung")
	print("===============")
	for record_data in Summary:
		if record_data.name == "total_distance":
			strecke = record_data.value
		if record_data.name == "avg_speed":
			avspeed = record_data.value*3.6/1000
		if record_data.name == "total_timer_time":
			zeit = record_data.value
		if record_data.name == "avg_heart_rate":
			avHR = record_data.value
		if record_data.name == "normalized_power":
			avPower = record_data.value
		if record_data.name == "total_ascent":
			anstieg = record_data.value
		if record_data.name == "total_discent":
			abstieg = record_data.value
		if record_data.name == "max_speed":
			v_max = record_data.value*3.6/1000
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


if (avPower == None):
  avPower = 0

startzeit  = datetime_to_local(startzeit)

h = np.floor(zeit/3600)
m = np.floor((zeit - h*3600)/60)
s = zeit - h*3600 - m*60

pausenzeit = totalzeit - zeit
hp = np.floor(pausenzeit/3600)
mp = np.floor((pausenzeit - hp*3600)/60)
sp = pausenzeit - hp*3600 - mp*60
#hf = list(map(add, hf, [Fitness]*len(hf)))

try:
	af = np.array(hf)
	af = list(filter(None,hf))
	af = sum(af)/len(af)
except:
	af = 0
	print("Keine HF verfuegbar")
try:
	ac = np.array(cad)
	ac = list(filter(None,ac))
	#ac = ac(ac != 0)
	ac = sum(ac)/len(ac)
except:
	ac = 0
	print("Keine Kadenz verfuegbar")

if (avPower == 0):
	if (af == 0):
		print("Keine Leistung und keine HF verfuegbar, schaetze TSS mit 75% Intensitaet")
		tss = zeit/3600*80
	else:
		tss = zeit/3600*af/zonen[4]*100
else:
    tss = avPower/float(FTP)*zeit/3600*100

print("TSS = %d" % (tss))

stretch_power = 1
try:	#
	power  = [e if e != None else 0 for e in power]
	powt   = [e if e != None else 0 for e in powt]
	powt   = smooth(powt,smooth_pow_print)
	power  = np.array(smooth(power,smooth_pow_print))
	powerZ = np.array(smooth(power,smooth_pow_zonen))
	if max(power) > 0:
		while max(power)*stretch_power < (max_hf/2*1.1):
			stretch_power = stretch_power*2
		while max(power)*stretch_power > (max_hf*1.1):
			stretch_power = stretch_power/2
		print ("stretch_power: " + str(stretch_power))
except:
	ap = 0
	print("Keine Leistung verfuegbar")

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
    if (avPower == 0):
      TB[i] = sum(j > zonen[i]  for j in list(filter(None,hf)))
      messageZ = ("(HF >%2d Schläge) " % (zonen[i])) 
    else:
      TB[i] = sum(j > tbPow[i]  for j in list(filter(None,powerZ)))
      messageZ = ("(>%2d W) " % (tbPow[i]))
  else:
    if (avPower == 0):
      TB[i] = sum(((j > zonen[i]) and (j <= zonen[i+1])) for j in list(filter(None,hf)))
      messageZ = ("(HF %2d - %2d) " % (zonen[i],zonen[i+1])) 
    else:
      TB[i] = sum(((j > tbPow[i]) and (j <= tbPow[i+1])) for j in list(filter(None,powerZ)))
      messageZ = ("(%2d - %2d W) " % (tbPow[i],tbPow[i+1]))

  hz = np.floor(TB[i]/3600)
  mz = np.floor((TB[i] - hz*3600)/60)
  sz = TB[i] - hz*3600 - mz*60
  print("Training in Zone %d: %02d:%02d:%02d " % (i,hz,mz,sz) + messageZ)
  strZonen = ("%s %2d:%2d:%2d;" % (strZonen,hz,mz,sz))

rstr = ("%0.2f; %0.1f; %02d:%02d:%02d; %0.1f; %02d" % (strecke/1000,avspeed,h,m,s,v_max,kCal))
rstr = ("%s ; %02d; %02d; %02d; %02d; %02d; %s %02d:%02d:%02d; %s;;" % (rstr,af,avPower,ac,anstieg,tss,kmstr,hp,mp,sp,strZonen))

rh           = []
rm           = []
rs           = []
pos          = []
s_linien     = []
s_zeitlinien = []
s_pauslinien = []
e_linien     = []
e_zeitlinien = []
e_pauslinien = []
  
for i in range(0,runde):
	rh.append(np.floor(Runden[i].zeit/3600))
	rm.append(np.floor((Runden[i].zeit - rh[-1]*3600)/60))
	rs.append(Runden[i].zeit - rh[-1]*3600 - rm[-1]*60)
	rstr = (rstr+" %0.2f; %0.2f; %02d:%02d:%02d; %02d; %02d; %02d; %0.1f;" % (Runden[i].strecke/1000, Runden[i].avspeed,rh[-1],rm[-1],rs[-1],Runden[i].avHR,Runden[i].power,Runden[i].anstieg,Runden[i].v_max))
	#linien.append((sum(rstrecken[0:i])/1000))
	s_linien.append(Runden[i].x_start/1000)
	s_zeitlinien.append(Runden[i].z_start/3600)
	s_pauslinien.append(Runden[i].t_start/3600)
	e_linien.append(Runden[i].x_end/1000)
	e_zeitlinien.append(Runden[i].z_end/3600)
	e_pauslinien.append(Runden[i].t_end/3600)
	pos.append(( (np.abs(np.array(xspeed) - e_linien[-1]*1000)).argmin() ))

rstr = rstr.replace('.',',')
rstr = ("%d.%d.; ;%d;%2d:%2d:%2d;%s" % (startzeit.day,startzeit.month,bike_id,startzeit.hour,startzeit.minute,startzeit.second,rstr))

print("Markiere diese Zeile inklusive \">\" und kopiere sie in die Tabelle: ")
print(rstr)
print(">")

ueberschrift1 = "Allgemein;;;;;Zusammenfassung;;;;;;;;;;km-Stand;;;;;;Trainingsbereiche;;;;;;;"
for i in range(0,runde):
	ueberschrift1 = (ueberschrift1 + "Runde %d;;;;;;" % (i+1))
ueberschrift2 = ("Datum;Strecke;Rad;Start;Ges.-km;av;Ges.zeit;max;kCal;Puls;Leistung;Kad;hm;tss;stress;" + (((str(raeder)).replace(',',';')).replace('(','')).replace(')','') + ";Pausenzeit;TB0;TB1;TB2;TB3;TB4;Anm.;Rad - rep;")
for i in range(0,runde):
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

################# Nach Weg:

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

	for i in range(0,runde):
	  ax.text(np.mean([s_linien[i],e_linien[i]]), 170,("Runde %d"%(i+1)),color='y')
	  ax.text(np.mean([s_linien[i],e_linien[i]]), 161,("%d km"%(Runden[i].strecke/1000)),color='y')
	  ax.text(np.mean([s_linien[i],e_linien[i]]), 152,("%d km/h"%(round(Runden[i].avspeed))),color='y')
	  ax.text(np.mean([s_linien[i],e_linien[i]]), 143,("%d HS"%(Runden[i].avHR)),color='y')
	  ax.text(np.mean([s_linien[i],e_linien[i]]), 134,("%d W"%(Runden[i].power)),color='y')
	  ax.text(np.mean([s_linien[i],e_linien[i]]), 125,("%02d:%02d:%02d" % (rh[i],rm[i],rs[i])),color='y')
	# if runde > 0:
	#     ax.text(np.mean([e_linien[i],sum(rstrecken)/1000]), 170,("Runde %d"%(i+1)),color='y')
	#     ax.text(np.mean([e_linien[i],sum(rstrecken)/1000]), 161,("%d km/h"%(Runden[i].avspeed)),color='y')
	#     ax.text(np.mean([e_linien[i],sum(rstrecken)/1000]), 152,("%d HS"%(Runden[i].avHR)),color='y')
	#     ax.text(np.mean([e_linien[i],sum(rstrecken)/1000]), 143,("%d km"%(Runden[i].strecke/1000)),color='y')
	#     ax.text(np.mean([e_linien[i],sum(rstrecken)/1000]), 134,("%02d:%02d:%02d" % (rh[i],rm[i],rs[i])),color='y')
	for i in range(0,zwischen):
		ax.text(np.mean([x_zw_start[i],x_zw_end[i]])/1000, 170,("Zwischen %d"%(i+1)),color='y')
		ax.text(np.mean([x_zw_start[i],x_zw_end[i]])/1000, 161,("%d km"%(x_zw[i]/1000)),color='y')
		ax.text(np.mean([x_zw_start[i],x_zw_end[i]])/1000, 152,("%d km/h"%(round(v_zw[i]*3.6))),color='y')
		ax.text(np.mean([x_zw_start[i],x_zw_end[i]])/1000, 143,("%d HS"%(hf_zw[i])),color='y')
		ax.text(np.mean([x_zw_start[i],x_zw_end[i]])/1000, 134,("%d W"%(pow_zw[i])),color='y')
		ax.text(np.mean([x_zw_start[i],x_zw_end[i]])/1000, 125,("%02d:%02d:%02d" % (zh[i],zm[i],zs[i])),color='y')

	ax.plot(np.divide(xcad,1000),cad,lw=0.5, label = "Cadence")
	ax.plot(np.divide(xspeed,1000),np.multiply(speed,stretch_speed), label='Speed$\cdot$'+str(stretch_speed))
	ax.plot(np.divide(xhf,1000),hf, label="HF")
	ax.plot(np.divide(xpow,1000),np.multiply(power,stretch_power), label='Power$\cdot$'+str(stretch_power),lw=1)
	ax.plot([-1,-1],[0, 1],lw=1,label = 'Altitude')
	ax.hlines(zonen,[0],[max(x)/1000],lw=1,colors='r')
	ax.hlines(tbPow*stretch_power,[0],[max(x)/1000],lw=1,colors='m')
	ax.vlines(s_linien,[0],[200],lw=2,color='y')
	ax.vlines(e_linien,[0],[200],lw=2,color='y')
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

################# Nach Zeit ohne Pausen:

if plot_time == 1:
	plt.xkcd()

	fig = plt.figure()
	ax = fig.add_subplot(1, 1, 1)
	ax.set_prop_cycle(cycler('color', ['c', 'b', 'r', 'm', 'k']))
	ax.set_title("%s on %s" % (sport,startzeit.strftime("%A, %b. %d, %Y")))
	ax.set_ylim([0,max_hf])
	ax.grid(color='k', linestyle=':', linewidth=1)
	ax.hlines(zonen,[0],[totalzeit],lw=1)
	#ax.vlines(np.divide(pos,3600),[0],[200],lw=2,color='y')
	#pos.append((totalzeit))
	#for i in range(1,runde+1):
	  #ax.text(np.mean([pos[i-1],pos[i]])/3600, 170,("Runde %d"%(i)),color='y')
	#if runde > 0:
	  #ax.text(np.mean([pos[i]/3600,sum(Runden[i].zeit)/3600]), 170,("Runde %d"%(i+1)),color='y')
	ax.vlines(s_zeitlinien,[0],[200],lw=2,color='y')
	ax.vlines(e_zeitlinien,[0],[200],lw=2,color='y')
	for i in range(0,runde):
	  ax.text(np.mean([s_zeitlinien[i],e_zeitlinien[i]]), 170,("Runde %d"%(i+1)),color='y')
	  ax.text(np.mean([s_zeitlinien[i],e_zeitlinien[i]]), 161,("%d km"%(Runden[i].avspeed)),color='y')
	  ax.text(np.mean([s_zeitlinien[i],e_zeitlinien[i]]), 152,("%02d:%02d:%02d" % (rh[i],rm[i],rs[i])),color='y')
	for i in range(0,zwischen):
		ax.text(np.mean([z_zw_start[i],z_zw_end[i]])/3600, 170,("Zwischen %d"%(i+1)),color='y')
		ax.text(np.mean([z_zw_start[i],z_zw_end[i]])/3600, 161,("%d km"%(x_zw[i]/1000)),color='y')
		ax.text(np.mean([z_zw_start[i],z_zw_end[i]])/3600, 152,("%02d:%02d:%02d" % (zh[i],zm[i],zs[i])),color='y')

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
	ax.plot(np.linspace(0,len(power)/3600,len(power)),np.multiply(power,stretch_power), label='Power$\cdot$'+str(stretch_power),lw=1)
	ax.plot([-1,-1],[0, 1],lw=1,label = 'Altitude')
	if plot_hoehe == 1:
	    ax2.plot(np.linspace(0,len(alt)/3600,len(alt)),alt,lw=1)
	ax.set_xlim([0,len(speed)/3600])

	ax.legend(loc='best')
	#ax.legend(('Cadence','Speed$\cdot$'+str(stretch_speed),'HF','Altitude'),'best')

	plt.show()


################# Nach Uhrzeit:

if plot_pause == 1:
	plt.xkcd()

	fig = plt.figure()
	ax = fig.add_subplot(1, 1, 1)
	ax.set_prop_cycle(cycler('color', ['c', 'b', 'r', 'm', 'k']))
	ax.set_title("%s on %s" % (sport,startzeit.strftime("%A, %b. %d, %Y")))
	ax.set_ylim([0,max_hf])
	ax.grid(color='k', linestyle=':', linewidth=1)
	ax.hlines(zonen,[t[0]/3600],[t[-1]/3600],lw=1)
	ax.vlines(s_pauslinien,[0],[200],lw=2,color='y')
	ax.vlines(e_pauslinien,[0],[200],lw=2,color='y')
	# ax.vlines(ereignis,[0],[200],lw=2,color='g')
	for i in range(0,runde):
	  ax.text(np.mean([s_pauslinien[i],e_pauslinien[i]]), 170,("Runde %d"%(i+1)),color='y')
	for i in range(0,zwischen):
		ax.text(np.mean([t_zw_start[i],t_zw_end[i]])/3600, 170,("Zwischen %d"%(i+1)),color='y')
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
