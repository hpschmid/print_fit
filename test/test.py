from fitparse import FitFile
from matplotlib import pyplot as plt
from datetime import datetime
import numpy as np
import sys
from Tkinter import *
from tkFileDialog   import askopenfilename      

#def callback():
#name= askopenfilename() 
#print name
    
#errmsg = 'Error!'
#Button(text='File Open', command=callback).pack(fill=X)
#mainloop()

#fitfile = FitFile('171018171857.fit')
#fitfile = FitFile('171031085304.sum')
#fitfile = FitFile('171028094355.sum')
#fitfile = FitFile('171015211446.sum')
#fitfile = FitFile('171018171857.fit')
fitfile = FitFile('171028094355.fit')
#fitfile = FitFile(sys.argv[1])
#fitfile = FitFile(name)
zonen = [139,149,160,171]


runde   = 0
strecke = []
avspeed = []
zeit    = []
avHR	= []
anstieg = []
abstieg = []
v_max   = []

kCal    = []
kadenz  = []
uhrzeit = []

for Laps in fitfile.get_messages('session'):
	runde = runde + 1
	print("Runde " + str(runde))
	for record_data in Laps:
		if record_data.name == "total_distance":
			strecke.append((record_data.value))
		if record_data.name == "avg_speed":
			avspeed.append((record_data.value*3.6))
		if record_data.name == "total_moving_time":
			zeit.append((record_data.value))
		if record_data.name == "avg_heart_rate":
			avHR.append((record_data.value))
		if record_data.name == "total_ascent":
			anstieg.append((record_data.value))
		if record_data.name == "total_discent":
			abstieg.append((record_data.value))
		if record_data.name == "max_speed":
			v_max.append((record_data.value))
		if record_data.name == "total_calories":
			kCal.append((record_data.value))
		if record_data.name == "timestamp":
			uhrzeit.append((record_data.value))

		if record_data.units:
			print(" * %s: %s %s" % (record_data.name, record_data.value, record_data.units))
		else:
			print(" * %s: %s" % (record_data.name, record_data.value))
	print()



