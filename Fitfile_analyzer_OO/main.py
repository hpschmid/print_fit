#!/usr/bin/env python3
#
# Author: Gerhard Schmid
# License: MIT
# installiere Fitfileparser mit
#	pip3 install fitparse
# installiere Matplotlib mit
#	apt-get python3-matplotlib
###############################
# https://www.perplexity.ai/

from __future__ import division
from fitparse   import FitFile
import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1.inset_locator import inset_axes # , zoomed_inset_axes
# from mpl_toolkits.axes_grid1.anchored_artists import AnchoredSizeBar
import numpy as np
import sys
from cycler import cycler
from Konstanten import *
from Ausfahrt import *
from Math import *

###################################### Settings ####################################################
const = Konstanten()
args = Argumente()
args.read_arguments(sys.argv)
ausfahrt = Ausfahrt()
fen1 = ausfahrt.get_filename(args)
ausfahrt.read_all_records()

if args.debug_print == 1:
    ausfahrt.debug_print()

ausfahrt.lese_runden()
ausfahrt.finde_zwischen_runden(const.schwelle_zwischen)
ausfahrt.lese_zusammenfassung()

for file_id in ausfahrt.fitfile.get_messages('file_id'):
    for record_data in file_id:
        if record_data.name == "manufacturer":
            hersteller = record_data.value
            print('Hersteller erkannt: %s' % hersteller)

km = [0,0,0,0,0]
bike = "Default"
id_final = 1
args.bike_id = 1
if hersteller == "srm":
    for bike_profile in ausfahrt.fitfile.get_messages('bike_profile'):
        for record_data in bike_profile:
            if record_data.name == "name":
                bike = record_data.value
                args.bike_id = int(bike[-1])

                totfile = FitFile('Totals.fit')
                for totals in totfile.get_messages('unknown_65292'):
                    for record_data in totals:
                        if record_data.name == "unknown_0":
                            id_final = record_data.value
                            #print(" * %s: %s" % (record_data.name, record_data.value))
                        if record_data.name == "unknown_3":
                            km[id_final] = record_data.value / 1000
                bike = const.raeder[args.bike_id - 1]
                id_final = args.bike_id

# Bei Igpsport finde ich keinen Hinweise auf Radprofil, kann über Gewicht unterscheiden (alternativ Sensor-Id):
elif hersteller == "igpsport":
    totfile = FitFile('user.fit')
    for totals in totfile.get_messages('bike_profile'):
        for record_data in totals:
            if record_data.name == "bike_weight":
                bike_weight = record_data.value
                if bike_weight == 8:
                    args.bike_id = 1
                elif bike_weight == 6:
                    args.bike_id = 2
                elif bike_weight == 7:
                    args.bike_id = 3
                else:
                    args.bike_id = 4
                id_final = args.bike_id
                bike = const.raeder[args.bike_id - 1]
    for totals in totfile.get_messages('bike_profile'):
        for record_data in totals:
            if record_data.name == "odometer":
                km[args.bike_id] = record_data.value/1000

elif hersteller == "bryton":
    for bike_profile in ausfahrt.fitfile.get_messages('unknown_68'):
        for record_data in bike_profile:
            if record_data.name == "unknown_7":
                id_final = record_data.value
                args.bike_id = id_final
                bike = const.raeder[0]
                if id_final == 2:
                    args.bike_id = 3
                elif id_final == 0x10:
                    args.bike_id = 2
                elif id_final == 0x20:
                    args.bike_id = 4
                bike = const.raeder[args.bike_id - 1]
                #Beim Rider 450 ist 0x10 Rad 1 und 0x20 Rad 2, daher:
                if id_final > 2:
                    id_final = id_final >> 4

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
                trip2_str =('Trip2%d_km' % id_final)
                km[args.bike_id] = system[trip2_str]
elif hersteller == "garmin":
    for Summary in ausfahrt.fitfile.get_messages('session'):
        for record_data in Summary:
            if record_data.name == "unknown_110":
                bike = record_data.value
            if record_data.name == "unknown_178":
                km[args.bike_id] = record_data.value
else:
    print('Hersteller nicht implementiert, kann Odometer nicht lesen')

kmstr = [' ;',' ;',' ;',' ;',' ;',' ;']
kmstr[args.bike_id] = ("%s;" % str(km[args.bike_id]))
kmstr = ('%s%s%s%s%s%s' % (kmstr[0],kmstr[1],kmstr[2],kmstr[3],kmstr[4],kmstr[5]))
print("Rad: %s  (id: %d), Kilometerstand: %s" % (bike, id_final, str(km[args.bike_id])))
print("===============")
print()

h = np.floor(ausfahrt.session.zeit/3600)
m = np.floor((ausfahrt.session.zeit - h*3600)/60)
s = ausfahrt.session.zeit - h*3600 - m*60
pausenzeit = ausfahrt.session.totalzeit - ausfahrt.session.zeit
hp = np.floor(pausenzeit/3600)
mp = np.floor((pausenzeit - hp*3600)/60)
sp = pausenzeit - hp*3600 - mp*60
#hf = list(map(add, hf, [args.Fitness]*len(hf)))

# Replace all 'None' by 0s and calc. mean excluding zeros:
ausfahrt.hf    = np.array([e if e is not None else 0 for e in ausfahrt.hf])
af    = np.mean(ausfahrt.hf[ausfahrt.hf > 0])
if np.isnan(af):
    af = 0
ausfahrt.cad   = np.array([e if e is not None else 0 for e in ausfahrt.cad])
ac    = np.mean(ausfahrt.cad[ausfahrt.cad > 0])
if np.isnan(ac):
    ac = 0

ausfahrt.power = np.array([e if e is not None else 0 for e in ausfahrt.power])
ausfahrt.powt   = [e if e is not None else 0 for e in ausfahrt.powt]
ausfahrt.powt   = smooth(ausfahrt.powt, const.smooth_Pprint)
Pprint = smooth(ausfahrt.power, const.smooth_Pprint)
P30    = smooth(ausfahrt.power, const.smooth_P30)
if any(P30 > 0):
    NPcalc = int(np.sqrt(np.sqrt(np.mean(np.power(P30[P30 > 0],4)))))
    print("Normierte Leistung Gerät/Berechnet:  %d/%d W" % (ausfahrt.session.NP, NPcalc))

if ausfahrt.session.NP == 0:
    if af == 0:
        print("Keine Leistung und keine HF verfuegbar, schaetze TSS mit 80% Intensitaet")
        tss = int(ausfahrt.session.zeit/3600*80)
    else:
        tss = int(ausfahrt.session.zeit/3600*af/const.zonen[4]*100)
else:
    tss = (ausfahrt.session.NP / float(const.FTP) * ausfahrt.session.zeit / 3600 * 100)
print("TSS = %d" % tss)
if not('kCal' in locals()):
    if af > 0:
        print("Kein KCal Wert vom Gerät, schätze kCal aus avHF und Zeit")
        kCal = int(af*ausfahrt.session.zeit/3600*4.431)
    else:
        print("Kein KCal und keine HF verfügbar Wert vom Gerät, schätze kCal aus tss")
        kCal = tss*7.623

stretch_power = 1
if max(Pprint) > 0:
    while max(Pprint)*stretch_power < (const.max_hf/2*1.1):
        stretch_power = stretch_power*2
    while max(Pprint)*stretch_power > (const.max_hf*1.1):
        stretch_power = stretch_power/2
    print ("stretch_power: " + str(stretch_power))

stretch_T = 10
while max(ausfahrt.T)*stretch_T < (const.max_hf / 2 * 1.1):
    stretch_T = stretch_T*2
while max(ausfahrt.T)*stretch_T > (const.max_hf * 1.1):
    stretch_T = stretch_T/2
print ("stretch_temperature: " + str(stretch_T))

############## Plots:
try:
    ausfahrt.cad = np.array(ausfahrt.cad)
    ausfahrt.cad[ausfahrt.cad > 130] = None
    ausfahrt.cad[ausfahrt.cad < 30] = None
    gnd = min(ausfahrt.alt) - min(ausfahrt.alt) % 50
except:
    print("Keine Kadenz verfuegbar")

stretch_speed = 1
if max(ausfahrt.speed) > 0:
    while max(ausfahrt.speed)*stretch_speed < const.max_hf/2*1.1:
        stretch_speed = stretch_speed*2

print("stretch_speed: " + str(stretch_speed))

TB = np.zeros(len(const.zonen)+1)
strZonen  = " "
#print(range(0,len(const.zonen)))
for i in range(0,(len(const.zonen))):
  if i == (len(const.zonen)-1):
    if ausfahrt.session.NP == 0:
      TB[i] = sum(j > const.zonen[i]  for j in list(filter(None, ausfahrt.hf)))
      messageZ = ("(HF >%2d Schläge) " % (const.zonen[i]))
    else:
      TB[i] = sum(j > const.tbPow[i]  for j in list(filter(None,P30)))
      messageZ = ("(>%2d W) " % (const.tbPow[i]))
  else:
    if ausfahrt.session.NP == 0:
      TB[i] = sum(((j > const.zonen[i]) and (j <= const.zonen[i+1])) for j in list(filter(None, ausfahrt.hf)))
      messageZ = ("(HF %2d - %2d) " % (const.zonen[i],const.zonen[i+1]))
    else:
      TB[i] = sum(((j > const.tbPow[i]) and (j <= const.tbPow[i+1])) for j in list(filter(None,P30)))
      messageZ = ("(%2d - %2d W) " % (const.tbPow[i],const.tbPow[i+1]))

  hz = np.floor(TB[i]/3600)
  mz = np.floor((TB[i] - hz*3600)/60)
  sz = TB[i] - hz*3600 - mz*60
  print("Training in Zone %d: %02d:%02d:%02d " % (i,hz,mz,sz) + messageZ)
  strZonen = ("%s %2d:%2d:%2d;" % (strZonen,hz,mz,sz))

fen1.destroy()
################# Nach Weg: ###########################################################################
fenster = [19.5, 10]
if args.plot_weg == 1:
    plt.xkcd()
    fig = plt.figure(figsize=fenster)
    # manager = plt.get_current_fig_manager()
    # manager.window.maximize() # does not work??
    # mng = plt.get_current_fig_manager()
    # mng.resize(*mng.window.maximize()) # maximizes over all screens
    ax = fig.add_subplot(1, 1, 1)
    ax.set_prop_cycle(cycler('color', ['c', 'b', 'r', 'm', 'k']))
    ax.set_title("%s on %s" % (ausfahrt.session.sport, ausfahrt.session.startzeit.strftime("%A, %b. %d, %Y")))
    ax.set_ylim([0,const.max_hf])
    ax.grid(color='k', linestyle=':', linewidth=1)
    plt.xlabel('Distance (km)')
    plt.ylabel('Cadence, Speed, HF')
    ax2 = ax.twinx()
    ax2.set_prop_cycle(cycler('color', ['k']))
    ax2.set_ylabel('Altitude')

    plt.rc('lines', linewidth=2)

    for i in range(0,len(ausfahrt.Runden)):
        ax.text(np.mean([ausfahrt.Runden[i].s_linie, ausfahrt.Runden[i].e_linie]), 170, ("Runde %d" % (i + 1)), color='y')
        ax.text(np.mean([ausfahrt.Runden[i].s_linie, ausfahrt.Runden[i].e_linie]), 161, ("%d km" % (ausfahrt.Runden[i].x / 1000)), color='y')
        ax.text(np.mean([ausfahrt.Runden[i].s_linie, ausfahrt.Runden[i].e_linie]), 152, ("%d km/h" % (round(ausfahrt.Runden[i].speed))), color='y')
        ax.text(np.mean([ausfahrt.Runden[i].s_linie, ausfahrt.Runden[i].e_linie]), 143, ("%d HS" % ausfahrt.Runden[i].HF), color='y')
        ax.text(np.mean([ausfahrt.Runden[i].s_linie, ausfahrt.Runden[i].e_linie]), 134, ("%d W" % ausfahrt.Runden[i].power), color='y')
        ax.text(np.mean([ausfahrt.Runden[i].s_linie, ausfahrt.Runden[i].e_linie]), 125, ("%02d:%02d:%02d" % (ausfahrt.Runden[i].h, ausfahrt.Runden[i].m, ausfahrt.Runden[i].s)), color='y')
        ax.vlines(ausfahrt.Runden[i].s_linie, [0], [200], lw=2, color='y')
        ax.vlines(ausfahrt.Runden[i].e_linie, [0], [200], lw=2, color='y')
    for i in range(0, len(ausfahrt.Zwischen)):
        ax.text(np.mean([ausfahrt.Zwischen[i].x_start, ausfahrt.Zwischen[i].x_end]) / 1000, 170, ("Zwischen %d" % (i + 1)), color='y')
        ax.text(np.mean([ausfahrt.Zwischen[i].x_start, ausfahrt.Zwischen[i].x_end]) / 1000, 161, ("%d km" % (ausfahrt.Zwischen[i].x / 1000)), color='y')
        ax.text(np.mean([ausfahrt.Zwischen[i].x_start, ausfahrt.Zwischen[i].x_end]) / 1000, 152, ("%d km/h" % (round(ausfahrt.Zwischen[i].speed))), color='y')
        ax.text(np.mean([ausfahrt.Zwischen[i].x_start, ausfahrt.Zwischen[i].x_end]) / 1000, 143, ("%d HS" % ausfahrt.Zwischen[i].HF), color='y')
        ax.text(np.mean([ausfahrt.Zwischen[i].x_start, ausfahrt.Zwischen[i].x_end]) / 1000, 134, ("%d W" % ausfahrt.Zwischen[i].power), color='y')
        ax.text(np.mean([ausfahrt.Zwischen[i].x_start, ausfahrt.Zwischen[i].x_end]) / 1000, 125, ("%02d:%02d:%02d" % (ausfahrt.Zwischen[i].h, ausfahrt.Zwischen[i].m, ausfahrt.Zwischen[i].s)), color='y')

    ax.plot(np.divide(ausfahrt.xcad, 1000), ausfahrt.cad, lw=0.5, label ="Cadence")
    ax.plot(np.divide(ausfahrt.xspeed, 1000), np.multiply(ausfahrt.speed, stretch_speed), label='Speed$\cdot$' + str(stretch_speed))
    ax.plot(np.divide(ausfahrt.xhf, 1000), ausfahrt.hf, label="HF")
    ax.plot(np.divide(ausfahrt.xpow, 1000), np.multiply(Pprint, stretch_power), label='Power$\cdot$' + str(stretch_power), lw=1)
    ax.plot([-1,-1],[0, 1],lw=1,label = 'Altitude')
    ax.hlines(const.zonen, [0], [max(ausfahrt.x) / 1000], lw=1, colors='r')
    ax.hlines(const.tbPow * stretch_power, [0], [max(ausfahrt.x) / 1000], lw=1, colors='m')
    if args.plot_hoehe == 1:
        ax2.plot(np.divide(ausfahrt.xalt, 1000), ausfahrt.alt, lw=1)
    ax2.set_xlim([0, max(ausfahrt.x) / 1000])

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

if args.plot_zeit == 1:
    plt.xkcd()
    fig = plt.figure(figsize=fenster)
    ax = fig.add_subplot(1, 1, 1)
    ax.set_prop_cycle(cycler('color', ['c', 'b', 'r', 'm', 'k']))
    ax.set_title("%s on %s" % (ausfahrt.session.sport, ausfahrt.session.startzeit.strftime("%A, %b. %d, %Y")))
    ax.set_ylim([0,const.max_hf])
    ax.grid(color='k', linestyle=':', linewidth=1)
    ax.hlines(const.zonen, [0], [ausfahrt.session.totalzeit], lw=1)
    for i in range(0, len(ausfahrt.Runden)):
      ax.text(np.mean([ausfahrt.Runden[i].s_zeitlinie, ausfahrt.Runden[i].e_zeitlinie]), 170, ("Runde %d" % (i + 1)), color='y')
      ax.text(np.mean([ausfahrt.Runden[i].s_zeitlinie, ausfahrt.Runden[i].e_zeitlinie]), 161, ("%d km/h" % ausfahrt.Runden[i].speed), color='y')
      ax.text(np.mean([ausfahrt.Runden[i].s_zeitlinie, ausfahrt.Runden[i].e_zeitlinie]), 152, ("%02d:%02d:%02d" % (ausfahrt.Runden[i].h, ausfahrt.Runden[i].m, ausfahrt.Runden[i].s)), color='y')
      ax.vlines(ausfahrt.Runden[i].s_zeitlinie, [0], [200], lw=2, color='y')
      ax.vlines(ausfahrt.Runden[i].e_zeitlinie, [0], [200], lw=2, color='y')
    for i in range(0, len(ausfahrt.Zwischen)):
        ax.text(np.mean([ausfahrt.Zwischen[i].z_start, ausfahrt.Zwischen[i].z_end]) / 3600, 170, ("Zwischen %d" % (i + 1)), color='y')
        ax.text(np.mean([ausfahrt.Zwischen[i].z_start, ausfahrt.Zwischen[i].z_end]) / 3600, 161, ("%d km/h" % ausfahrt.Zwischen[i].speed), color='y')
        ax.text(np.mean([ausfahrt.Zwischen[i].z_start, ausfahrt.Zwischen[i].z_end]) / 3600, 152, ("%02d:%02d:%02d" % (ausfahrt.Zwischen[i].h, ausfahrt.Zwischen[i].m, ausfahrt.Zwischen[i].s)), color='y')

    plt.xlabel('Time (h)')
    plt.ylabel('Cadence, Speed, HF')
    ax2 = ax.twinx()
    ax2.set_prop_cycle(cycler('color', ['k']))
    ax2.set_ylabel('Altitude')

    plt.rc('lines', linewidth=2)

    ax.plot(np.linspace(0, len(ausfahrt.T) / 3600, len(ausfahrt.T)), np.multiply(ausfahrt.T, stretch_T), lw=0.2, color="orange", label ="Temperature$\cdot$" + str(stretch_T))
    ax.plot(np.linspace(0, len(ausfahrt.cad) / 3600, len(ausfahrt.cad)), ausfahrt.cad, lw=0.5, label ="Cadence")
    ax.plot(np.linspace(0, len(ausfahrt.speed) / 3600, len(ausfahrt.speed)), np.multiply(ausfahrt.speed, stretch_speed), label='Speed$\cdot$' + str(stretch_speed))
    ax.plot(np.linspace(0, len(ausfahrt.hf) / 3600, len(ausfahrt.hf)), ausfahrt.hf, label="HF")
    ax.plot(np.linspace(0,len(Pprint)/3600,len(Pprint)),np.multiply(Pprint,stretch_power), label='Power$\cdot$'+str(stretch_power),lw=1)
    ax.plot([-1,-1],[0, 1],lw=1,label = 'Altitude')
    if args.plot_hoehe == 1:
        ax2.plot(np.linspace(0, len(ausfahrt.alt) / 3600, len(ausfahrt.alt)), ausfahrt.alt, lw=1)
    ax.set_xlim([0, len(ausfahrt.speed) / 3600])

    ax.legend(loc='best')
    #ax.legend(('Cadence','Speed$\cdot$'+str(stretch_speed),'HF','Altitude'),'best')

    plt.show()

################# Nach Uhrzeit: ###########################################################################

if args.plot_pause == 1:
    plt.xkcd()
    fig = plt.figure(figsize=fenster)
    ax = fig.add_subplot(1, 1, 1)
    ax.set_prop_cycle(cycler('color', ['c', 'b', 'r', 'm', 'k']))
    ax.set_title("%s on %s" % (ausfahrt.session.sport, ausfahrt.session.startzeit.strftime("%A, %b. %d, %Y")))
    ax.set_ylim([0,const.max_hf])
    ax.grid(color='k', linestyle=':', linewidth=1)
    ax.hlines(const.zonen, [ausfahrt.t[0] / 3600], [ausfahrt.t[-1] / 3600], lw=1)
    # ax.vlines(ereignis,[0],[200],lw=2,color='g')
    for i in range(0, len(ausfahrt.Runden)):
        ax.vlines(ausfahrt.Runden[i].s_pauslinie, [0], [200], lw=2, color='y')
        ax.vlines(ausfahrt.Runden[i].e_pauslinie, [0], [200], lw=2, color='y')
        ax.text(np.mean([ausfahrt.Runden[i].s_pauslinie, ausfahrt.Runden[i].e_pauslinie]), 170, ("Runde %d" % (i + 1)), color='y')
    for i in range(0, len(ausfahrt.Zwischen)):
        ax.text(np.mean([ausfahrt.Zwischen[i].t_start, ausfahrt.Zwischen[i].t_end]) / 3600, 170, ("Zwischen %d" % (i + 1)), color='y')
    plt.xlabel('Time (h)')
    plt.ylabel('Cadence, Speed, HF')
    ax2 = ax.twinx()
    ax2.set_prop_cycle(cycler('color', ['k']))
    ax2.set_ylabel('Altitude')

    plt.rc('lines', linewidth=2)

    #ax.plot(np.linspace(0,len(cad)/3600,len(cad)),cad,lw=0.5, label = "Cadence")
    ax.plot(ausfahrt.tcad, ausfahrt.cadt, lw=0.5, label ="Cadence")
    ax.plot(ausfahrt.tspeed, np.multiply(ausfahrt.speedt, stretch_speed), label='Speed$\cdot$' + str(stretch_speed))
    #ax.plot(np.linspace(0,len(thf)/3600,len(hft)),hft, label="HF")
    ax.plot(ausfahrt.thf, ausfahrt.hft, label="HF")
    ax.plot(ausfahrt.tpow, np.multiply(ausfahrt.powt, stretch_power), label='Power$\cdot$' + str(stretch_power), lw=1)
    ax.plot([-1,-1],[0, 1],lw=1,label = 'Altitude')
    #ax2.plot(np.linspace(0,len(alt)/3600,len(alt)),alt,lw=1)
    if args.plot_hoehe == 1:
        ax2.plot(ausfahrt.talt, ausfahrt.altt, lw=1)
    ax.set_xlim([ausfahrt.t[0] / 3600, ausfahrt.t[-1] / 3600])

    ax.legend(loc='best')
    #ax.legend(('Cadence','Speed$\cdot$'+str(stretch_speed),'HF','Altitude'),'best')

    plt.show()

############### Critical Power:  ######################################################
args.CP30 = 0
if (args.CP == 1) and any(ausfahrt.power > 0):
    steps = 30
    Int   = [0]*int(max(ausfahrt.power))
    Pint  = [0]*int(max(ausfahrt.power))
    # Methode 1: schau, wie viele Sekunden über bestimmter Leistung waren, unabhängig, ob zusammenhängendes Intervall
    for i in range(const.lower_Plimit,len(Pint)):
        Int[i] = i
        Pint[i] = len(ausfahrt.power[ausfahrt.power > i])
    # Methode 2: smoothen über Intervalllänge, nimm maximum, d.h. nur zusammenhängende Intervalle werden genommen, aber Durchnitt
    steps = 15
    max_interval = 150*60
    step_size = int(max_interval/steps)
    Int2  = [0]*len(range(1,steps+1))
    Pint2 = [0]*len(range(1,steps+1))
    Int2[0] = max(P30)
    Pint2[0] = 30 # Vergrößere Intervalle um je 5 min (sonst dauerts extrem lange)
    for i in range(1,steps):
        print('Berechne max. Leistung für %d min (bis %d)...' % (i*step_size/60, max_interval/60), end='\r')
        Psmooth = smooth(ausfahrt.power, i * step_size)
        Int2[i] = max(Psmooth)
        Pint2[i] = i*step_size# Vergrößere Intervalle um je 5 min (sonst dauerts extrem lange)
    print('\nFertig!\n')
    args.CP30 = Int2[3-1]
    print('CP30 = %d' % args.CP30)

    plt.xkcd()
    fig = plt.figure(figsize=fenster)
    ax = fig.add_subplot(1, 1, 1)
    ax.grid(color='k', linestyle=':', linewidth=1)
    plt.xlabel('Intervall (min)')
    plt.ylabel('Leistung (W)')
    # ax.plot(np.divide(Pint[const.lower_Plimit:-1],60),np.linspace((const.lower_Plimit + 1),len(Pint)-(const.lower_Plimit + 1),len(Pint)-(const.lower_Plimit + 1))+(const.lower_Plimit + 1),lw=2, color="blue", label = "Critical Power")
    ax.plot(np.divide(Pint[const.lower_Plimit:-1],60),Int[const.lower_Plimit:-1],lw=2, color="blue", label = "Critical Power, Method 1")
    ax.plot(np.divide(Pint2,60),Int2,lw=2, color="green", marker='x', label = "Critical Power, Method 2")
    ax.legend(loc='best')

    plt.show()

############### Barplot:            ######################################################
if (len(ausfahrt.Runden) > 0) & (args.plot_bar == 1):
    bar_r = np.zeros(len(ausfahrt.Alle))
    bar_x = np.zeros(len(ausfahrt.Alle))
    bar_v = np.zeros(len(ausfahrt.Alle))
    bar_p = np.zeros(len(ausfahrt.Alle))
    bar_h = np.zeros(len(ausfahrt.Alle))
    for i in range(0, len(ausfahrt.Alle)):
        bar_r[i] = i+1
        bar_x[i] = ausfahrt.Alle[i].x / 1000
        bar_v[i] = ausfahrt.Alle[i].speed
        bar_p[i] = ausfahrt.Alle[i].power
        bar_h[i] = ausfahrt.Alle[i].anstieg

    plt.xkcd()
    fig = plt.figure(figsize=fenster)
    ax = fig.add_subplot(1, 1, 1)
    ax.grid(color='k', linestyle=':', linewidth=1)
    plt.xlabel('Runde')
    plt.ylabel('km, km/h')
    ax.bar(bar_r-0.3,bar_x,0.2,lw=2, color="orange", label = "km")
    ax.bar(bar_r-0.1,bar_v,0.2,lw=2, color="blue", label = "km/h")
    ax.bar(bar_r + 0.1, np.zeros(len(ausfahrt.Alle)), 0.2, lw=2, color="m", label ="Leistung")
    ax.bar(bar_r + 0.3, np.zeros(len(ausfahrt.Alle)), 0.2, lw=2, color="grey", label ="Anstieg")
    plt.xticks(bar_r)
    ax.legend(loc='best')

    ax2 = ax.twinx()
    # ax2.set_prop_cycle(cycler('color', ['k']))
    ax2.set_ylabel('W, hm')
    ax2.bar(bar_r+0.1,bar_p,0.2,lw=2, color="m", label = "Leistung")
    ax2.bar(bar_r+0.3,bar_h,0.2,lw=2, color="grey", label = "Anstieg")
    ax.legend(loc='best')

    plt.show()

############### Print für Tabelle:  ######################################################

rstr = ("%0.2f; %0.1f; %02d:%02d:%02d; %0.1f; %02d" % (ausfahrt.session.strecke / 1000, ausfahrt.session.avspeed, h, m, s, ausfahrt.session.v_max, kCal))
rstr = ("%s ; %02d; %02d; %02d; %02d; %02d; %02d; %s %02d:%02d:%02d; %s;;" % (rstr, af, ausfahrt.session.NP, args.CP30, ac, ausfahrt.session.anstieg, tss, kmstr, hp, mp, sp, strZonen))
for i in range(0, len(ausfahrt.Alle)):
    rstr = (rstr +" %0.2f; %0.2f; %02d:%02d:%02d; %02d; %02d; %02d; %0.1f;" % (ausfahrt.Alle[i].x / 1000, ausfahrt.Alle[i].speed, ausfahrt.Alle[i].h, ausfahrt.Alle[i].m, ausfahrt.Alle[i].s, ausfahrt.Alle[i].HF, ausfahrt.Alle[i].power, ausfahrt.Alle[i].anstieg, ausfahrt.Alle[i].v_max))
rstr = rstr.replace('.',',')
rstr = ("%d.%d.; ;%d;%2d:%2d:%2d;%s" % (ausfahrt.session.startzeit.day, ausfahrt.session.startzeit.month, args.bike_id, ausfahrt.session.startzeit.hour, ausfahrt.session.startzeit.minute, ausfahrt.session.startzeit.second, rstr))

print("Markiere diese Zeile inklusive \">\" und kopiere sie in die Tabelle: ")
print(rstr)
print(">")

ueberschrift1 = "Allgemein;;;;;Zusammenfassung;;;;;;;;;;;km-Stand;;;;;;Trainingsbereiche;;;;;;;"
for i in range(0, len(ausfahrt.Runden)):
    ueberschrift1 = (ueberschrift1 + "Runde %d;;;;;;" % (i+1))
ueberschrift2 = ("Datum;Strecke;Rad;Start;Ges.-km;av;Ges.zeit;max;kCal;Puls;Leistung;CP30;Kad;hm;tss;stress;" + (((str(const.raeder)).replace(',',';')).replace('(','')).replace(')','') + ";Pausenzeit;TB0;TB1;TB2;TB3;TB4;Anm.;Rad - rep;")
for i in range(0, len(ausfahrt.Runden)):
    ueberschrift2 = (ueberschrift2 + "km;av;Zeit;Puls;Power;hm;max;")

if args.print_csv == 1:
    file = open(ausfahrt.csvdatei,"w")
    file.write(ueberschrift1 + "\r\n")
    file.write(ueberschrift2 + "\r\n")
    file.write(rstr)
    file.close()
