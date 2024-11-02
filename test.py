#!/usr/bin/env python3

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

bike_id = 3
km = [0,0,0,0,0]
totfile = FitFile('Totals.fit')
for totals in totfile.get_messages('unknown_65292'):
	for record_data in totals:
		if (record_data.name == "unknown_0"): 
			id = record_data.value	
			print(" * %s: %s" % (record_data.name, record_data.value))
		if record_data.name == "unknown_3":	
			km[id] = record_data.value
print("Kilometerstand: %s" % str(km[bike_id]/1000))
kmstr = [' ;',' ;',' ;',' ;',' ;']
kmstr[bike_id] = ("%s;" % str(km[bike_id]/1000))
kmstr = ('%s%s%s%s%s' % (kmstr[0],kmstr[1],kmstr[2],kmstr[3],kmstr[4]))
print("===============")
print()

