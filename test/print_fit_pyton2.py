#!/usr/bin/env python

from __future__ import division
from fitparse   import FitFile
from matplotlib import pyplot as plt
from mpl_toolkits.axes_grid1.inset_locator import inset_axes, zoomed_inset_axes
from mpl_toolkits.axes_grid1.anchored_artists import AnchoredSizeBar
from datetime   import datetime
import time
import numpy as np
import sys
import os
from Tkinter import *
from tkFileDialog   import askopenfilename      
from cycler import cycler
import glob

def smooth(y, box_pts):
    box = np.ones(box_pts)/box_pts
    y_smooth = np.convolve(y, box, mode='same')
    return y_smooth

print_alles = 0
print_csv   = 0
plot_weg    = 1
plot_time   = 1
plot_pause  = 0
plot_hoehe  = 1

zonen = [0,138,149,160,170]
FTP   = 245
#[0.81,0.9,0.94,1,1.03,1.07]
#tbPow = np.multiply([0,0.53,0.71,0.86,1],float(FTP))
tbPow = np.multiply([0,0.55,0.75,0.9,1.05],float(FTP))
smooth_pow_print = 600
smooth_pow_zonen = 30

list_of_files = glob.glob('*.fit') # * means all if need specific format then *.csv
latest_file = max(list_of_files, key=os.path.getctime)
print ("Neueste Ausfahrt: %s" % (latest_file))

fen1 = Tk()                              # Create window
fen1.title("FitFileParser")
T = Text(fen1, height=5, width=40)
T.pack()
T.insert(END, "Asking for filename\n\n")
name= askopenfilename(filetypes=[("Fit files","*.fit")],initialfile=latest_file)
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
#fitfile = FitFile('171119181215.fit')

def datetime_to_local(utc_datetime):
    now_timestamp = time.time()
    offset = datetime.fromtimestamp(now_timestamp) - datetime.utcfromtimestamp(now_timestamp)
    return utc_datetime + offset

t = [0]
t.append((0))
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
# Get all data messages that are of type record
for record in fitfile.get_messages('record'):

	# Go through all the data entries in this record
	for record_data in record:
		if record_data.name == "timestamp":
			zs   = record_data.value
			temp = zs.second + zs.minute*60 + zs.hour*3600
			t.append((t[-1] + (temp - t[-1])))
		if record_data.name == "distance":
			x.append((record_data.value))
		if (record_data.name == "enhanced_speed") and (record_data.value != None) :
			speedt.append((record_data.value*3.6))
			tspeed.append(((t[-1] - t[1])/float(3600)))
			if (record_data.value != 0):
			  speed.append((record_data.value*3.6))
			  xspeed.append((x[-1]))
		if record_data.name == "heart_rate":
			hft.append((record_data.value))
			thf.append(((t[-1] - t[1])/float(3600)))
			try:
			  if (speedt[-1] != 0):
			    hf.append((record_data.value))
			    xhf.append((x[-1]))
			except:
			  pass
			  #print("no speed found for this (first?) point")

		if (record_data.name == "power"):# and (record_data.value != None):
			powt.append((record_data.value))
			tpow.append(((t[-1] - t[1])/float(3600)))
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
				talt.append(((t[-1] - t[1])/float(3600)))
				try:
				  if (speedt[-1] != 0):
				    alt.append((record_data.value))
				    xalt.append((x[-1]))
				except:
				  pass

		if record_data.name == "cadence":
			#if (((record_data.value == None) or (record_data.value == 0)) and (cad != [])):
				#cad.append((cad[-1]))
			#else:
			cadt.append((record_data.value))
			tcad.append(((t[-1] - t[1])/float(3600)))
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
	
runde     = 0
rstrecken = []
ravspeed  = []
rzeiten   = []
rgzeiten  = []
ravHR     = []
rpower    = []
ranstiege = []
rv_max    = []
for Laps in fitfile.get_messages('lap'):
	runde = runde + 1
	print("Runde " + str(runde))
	for record_data in Laps:
		if record_data.name == "total_distance":
			rstrecken.append((record_data.value))
		if record_data.name == "avg_speed":
			ravspeed.append((record_data.value*3.6))
		if record_data.name == "total_moving_time":
			rzeiten.append((record_data.value))
		if record_data.name == "total_elapsed_time":
			rgzeiten.append((record_data.value))
		if record_data.name == "avg_heart_rate":
			ravHR.append((record_data.value))
		if record_data.name == "avg_power":
			rpower.append((record_data.value))
		if record_data.name == "total_ascent":
			ranstiege.append((record_data.value))
		if record_data.name == "max_speed":
			rv_max.append((record_data.value*3.6))
		if record_data.units:
			print(" * %s: %s %s" % (record_data.name, record_data.value, record_data.units))
		else:
			print(" * %s: %s" % (record_data.name, record_data.value))
	print()

for Summary in fitfile.get_messages('session'):
	print("Zusammenfassung")
	print("===============")
	for record_data in Summary:
		if record_data.name == "total_distance":
			strecke = record_data.value
		if record_data.name == "avg_speed":
			avspeed = record_data.value*3.6
		if record_data.name == "total_moving_time":
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
			v_max = record_data.value*3.6
		if record_data.name == "total_calories":
			kCal = record_data.value
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

try:
	af = np.array(hf)
	af = filter(None,hf)
	af = sum(af)/len(af)
except:
	af = 0
	print("Keine HF verfuegbar")
try:
	ac = np.array(cad)
	ac = filter(None,ac)
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
		while max(power)*stretch_power < 100:
			stretch_power = stretch_power*2
		while max(power)*stretch_power > 200:
			stretch_power = stretch_power/2
		print ("stretch_power: " + str(stretch_power))
except:
	ap = 0
	print("Keine Leistung verfuegbar")


TB = np.zeros(len(zonen)+1)
strZonen  = " "
#print(range(0,len(zonen)))
for i in range(0,(len(zonen))):
  if i == (len(zonen)-1):
    if (avPower == 0):
      TB[i] = sum(j > zonen[i]  for j in hf)
    else:
      TB[i] = sum(j > tbPow[i]  for j in powerZ)
  else:
    if (avPower == 0):
      TB[i] = sum(((j > zonen[i]) and (j <= zonen[i+1])) for j in hf)
    else:
      TB[i] = sum(((j > tbPow[i]) and (j <= tbPow[i+1])) for j in powerZ)

  hz = np.floor(TB[i]/3600)
  mz = np.floor((TB[i] - hz*3600)/60)
  sz = TB[i] - hz*3600 - mz*60
  print("Training in Zone %d: %02d:%02d:%02d " % (i,hz,mz,sz))
  strZonen = ("%s %2d:%2d:%2d;" % (strZonen,hz,mz,sz))

rstr = ("%0.2f; %0.1f; %02d:%02d:%02d; %0.1f; %02d" % (strecke/1000,avspeed,h,m,s,v_max,kCal))
rstr = ("%s ; %02d; %02d; %02d; %02d; %02d; ; ; ; ; ; %02d:%02d:%02d; %s;;" % (rstr,af,avPower,ac,anstieg,tss,hp,mp,sp,strZonen))

rh         = []
rm         = []
rs         = []
pos        = []
linien     = []
zeitlinien = []
pauslinien = []
if (rpower == []):
  rpower = np.zeros(runde+1)
  
for i in range(0,runde):
	rh.append(np.floor(rzeiten[i]/3600))
	rm.append(np.floor((rzeiten[i] - rh[-1]*3600)/60))
	rs.append(rzeiten[i] - rh[-1]*3600 - rm[-1]*60)
	rstr = (rstr+" %0.2f; %0.2f; %02d:%02d:%02d; %02d; %02d; %02d; %0.1f;" % (rstrecken[i]/1000, ravspeed[i],rh[-1],rm[-1],rs[-1],ravHR[i],rpower[i],ranstiege[i],rv_max[i]))
	linien.append((sum(rstrecken[0:i])/1000))
	zeitlinien.append(sum(rzeiten[0:i])/3600)
	pauslinien.append(sum(rgzeiten[0:i])/3600)
	pos.append(( (np.abs(np.array(xspeed) - linien[-1]*1000)).argmin() ))

rstr = rstr.replace('.',',')
rstr = ("%d.%d.; ; ;%2d:%2d:%2d;%s" % (startzeit.day,startzeit.month,startzeit.hour,startzeit.minute,startzeit.second,rstr))

print("Fuer die Tabelle: ")
print(rstr)
print(">")

ueberschrift1 = "Allgemein;;;;;Zusammenfassung;;;;;;;;;;km-Stand;;;;;Trainingsbereiche;;;;;;;"
for i in range(0,runde):
	ueberschrift1 = (ueberschrift1 + "Runde %d;;;;;;" % (i+1))
ueberschrift2 = ("Datum;Strecke;Rad;Start;Ges.-km;av;Ges.zeit;max;kCal;Puls;Leistung;Kad;hm;tss;stress;MTB;2er_Rad;Rennrad;Pausenzeit;TB0;TB1;TB2;TB3;TB4;Anm.;Rad - rep;")
for i in range(0,runde):
	ueberschrift2 = (ueberschrift2 + "km;av;Zeit;Puls;hm;max;")

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
	while max(speed)*stretch_speed < 100:
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
	ax.set_ylim([0,180])
	ax.grid(color='k', linestyle=':', linewidth=1)
	plt.xlabel('Distance (km)')
	plt.ylabel('Cadence, Speed, HF')
	ax2 = ax.twinx()
	ax2.set_prop_cycle(cycler('color', ['k']))
	ax2.set_ylabel('Altitude')

	plt.rc('lines', linewidth=2)

	for i in range(1,runde):
	    ax.text(np.mean([linien[i-1],linien[i]]), 170,("Runde %d"%(i)),color='y')
	    ax.text(np.mean([linien[i-1],linien[i]]), 161,("%d km/h"%(ravspeed[i-1])),color='y')
	    ax.text(np.mean([linien[i-1],linien[i]]), 152,("%d HS"%(ravHR[i-1])),color='y')
	    ax.text(np.mean([linien[i-1],linien[i]]), 143,("%d km"%(rstrecken[i-1]/1000)),color='y')
	    ax.text(np.mean([linien[i-1],linien[i]]), 134,("%02d:%02d:%02d" % (rh[i-1],rm[i-1],rs[i-1])),color='y')
	if runde > 0:
	    ax.text(np.mean([linien[i],sum(rstrecken)/1000]), 170,("Runde %d"%(i+1)),color='y')
	    ax.text(np.mean([linien[i],sum(rstrecken)/1000]), 161,("%d km/h"%(ravspeed[i])),color='y')
	    ax.text(np.mean([linien[i],sum(rstrecken)/1000]), 152,("%d HS"%(ravHR[i])),color='y')
	    ax.text(np.mean([linien[i],sum(rstrecken)/1000]), 143,("%d km"%(rstrecken[i]/1000)),color='y')
	    ax.text(np.mean([linien[i],sum(rstrecken)/1000]), 134,("%02d:%02d:%02d" % (rh[i],rm[i],rs[i])),color='y')

	ax.plot(np.divide(xcad,1000),cad,lw=0.5, label = "Cadence")
	ax.plot(np.divide(xspeed,1000),np.multiply(speed,stretch_speed), label='Speed$\cdot$'+str(stretch_speed))
	ax.plot(np.divide(xhf,1000),hf, label="HF")
	ax.plot(np.divide(xpow,1000),np.multiply(power,stretch_power), label='Power$\cdot$'+str(stretch_power),lw=1)
	ax.plot([-1,-1],[0, 1],lw=1,label = 'Altitude')
	ax.hlines(zonen,[0],[max(x)/1000],lw=1,colors='r')
	ax.hlines(tbPow*stretch_power,[0],[max(x)/1000],lw=1,colors='m')
	ax.vlines(linien,[0],[200],lw=2,color='y')
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
	ax.set_ylim([0,180])
	ax.grid(color='k', linestyle=':', linewidth=1)
	ax.hlines(zonen,[0],[totalzeit],lw=1)
	#ax.vlines(np.divide(pos,3600),[0],[200],lw=2,color='y')
	#pos.append((totalzeit))
	#for i in range(1,runde+1):
	  #ax.text(np.mean([pos[i-1],pos[i]])/3600, 170,("Runde %d"%(i)),color='y')
	#if runde > 0:
	  #ax.text(np.mean([pos[i]/3600,sum(rzeiten)/3600]), 170,("Runde %d"%(i+1)),color='y')
	ax.vlines(zeitlinien,[0],[200],lw=2,color='y')
	zeitlinien.append((totalzeit/3600))
	for i in range(1,runde):
	  ax.text(np.mean([zeitlinien[i-1],zeitlinien[i]]), 170,("Runde %d"%(i)),color='y')
	  ax.text(np.mean([zeitlinien[i-1],zeitlinien[i]]), 160,("%d km/h"%(ravspeed[i-1])),color='y')
	if runde > 0:
	  ax.text(np.mean([zeitlinien[i],sum(rzeiten)/3600]), 170,("Runde %d"%(i+1)),color='y')
	  ax.text(np.mean([zeitlinien[i],sum(rzeiten)/3600]), 160,("%d km/h"%(ravspeed[i])),color='y')

	plt.xlabel('Time (h)')
	plt.ylabel('Cadence, Speed, HF')
	ax2 = ax.twinx()
	ax2.set_prop_cycle(cycler('color', ['k']))
	ax2.set_ylabel('Altitude')

	plt.rc('lines', linewidth=2)

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


################# Nach Zeit mit Pausen:

if plot_pause == 1:
	plt.xkcd()

	fig = plt.figure()
	ax = fig.add_subplot(1, 1, 1)
	ax.set_prop_cycle(cycler('color', ['c', 'b', 'r', 'm', 'k']))
	ax.set_title("%s on %s" % (sport,startzeit.strftime("%A, %b. %d, %Y")))
	ax.set_ylim([0,180])
	ax.grid(color='k', linestyle=':', linewidth=1)
	ax.hlines(zonen,[0],[totalzeit],lw=1)
	ax.vlines(pauslinien,[0],[200],lw=2,color='y')
	pauslinien.append((totalzeit/3600))
	for i in range(1,runde+1):
	  ax.text(np.mean([pauslinien[i-1],pauslinien[i]]), 170,("Runde %d"%(i)),color='y')
	if runde > 0:
	  ax.text(np.mean([pauslinien[i],sum(rzeiten)/3600]), 170,("Runde %d"%(i+1)),color='y')
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
	ax.set_xlim([0,totalzeit/3600])

	ax.legend(loc='best')
	#ax.legend(('Cadence','Speed$\cdot$'+str(stretch_speed),'HF','Altitude'),'best')

	plt.show()


