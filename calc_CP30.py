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
FTP   = 255
lower_Plimit = int(FTP/2)
tbPow = np.multiply([0,0.55,0.75,0.9,1.05],float(FTP)) # Power zones
smooth_Pprint = 600 # 
smooth_P30 = 30
max_hf = 180 # for scaling the plots
schwelle_zwischen =  3000


def smooth(y, box_pts):
    box = np.ones(box_pts)/box_pts
    y_smooth = np.convolve(y, box, mode='same')
    return y_smooth

list_of_files = glob.glob('[0-9]*.fit') # Search for newest Fitfile beginning with a number
# latest_file = max(list_of_files, key=os.path.getctime)

for name in list_of_files:
	fitfile = FitFile(name)

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
		if (record.get_value('distance') != None):
			x.append(record.get_value('distance'))
		else:
			x.append(x[-1])
		T.append(record.get_value('temperature'))
		#if type(record.get_value('timestamp')) == int:
		#	zs = datetime_to_local(datetime.fromtimestamp(record.get_value('timestamp')))
		#else:
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

	for Summary in fitfile.get_messages('session'):
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

	bike_id = 1

	if (NP == None):
	  NP = 0

	startzeit  = datetime_to_local(startzeit)

	h = np.floor(zeit/3600)
	m = np.floor((zeit - h*3600)/60)
	s = zeit - h*3600 - m*60

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
	if any(P30 > 0):
		NPcalc = int(np.sqrt(np.sqrt(np.mean(np.power(P30[P30 > 0],4)))))


	############### Critical Power:  ######################################################
	CP30 = 0
	if any(power > 0):
		steps = 30
		Int   = [0]*int(max(power))
		Pint  = [0]*int(max(power))
		# Methode 1: schau, wie viele Sekunden über bestimmter Leistung waren, unabhängig, ob zusammenhängendes Intervall
		for i in range(lower_Plimit,len(Pint)):
			Int[i] = i
			Pint[i] = len(power[power > i])
		# Methode 2: smoothen über Intervalllänge, nimm maximum, d.h. nur zusammenhängende Intervalle werden genommen, aber Durchnitt
		steps = 15
		max_interval = 150*60
		step_size = int(max_interval/steps)
		Int2  = [0]*len(range(1,steps+1))
		Pint2 = [0]*len(range(1,steps+1))
		Int2[0] = max(P30)
		Pint2[0] = 30 # Vergrößere Intervalle um je 5 min (sonst dauerts extrem lange)
		for i in range(1,steps):
			Psmooth = smooth(power,i*step_size)
			Int2[i] = max(Psmooth)
			Pint2[i] = i*step_size# Vergrößere Intervalle um je 5 min (sonst dauerts extrem lange)
		CP30 = Int2[3-1]
		# print('CP30 = %d' % (CP30))


	rstr = ("%0.2f; %0.1f; %02d:%02d:%02d; %0.1f; %02d" % (strecke/1000,avspeed,h,m,s,v_max,kCal))
	rstr = ("%s ; %02d; %02d; %02d; " % (rstr,af,NP,CP30))
	rstr = rstr.replace('.',',')
	rstr = ("%d.%d.; ;%d;%2d:%2d:%2d;%s" % (startzeit.day,startzeit.month,bike_id,startzeit.hour,startzeit.minute,startzeit.second,rstr))

	# print("Markiere diese Zeile inklusive \">\" und kopiere sie in die Tabelle: ")
	print(rstr)
