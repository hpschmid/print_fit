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
import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1.inset_locator import inset_axes # , zoomed_inset_axes
from cycler import cycler

from Konstanten import *
from Ausfahrt import *
from Math import *
from Odometer import *

###################################### Settings ####################################################
const = Konstanten()
args = Argumente()
args.read_arguments(sys.argv)
fahrt = Ausfahrt()
fen1 = fahrt.get_filename(args)
fahrt.read_all_records()

if args.debug_print == 1:
    fahrt.debug_print()

fahrt.lese_runden()
fahrt.finde_zwischen_runden(const.schwelle_zwischen)
fahrt.lese_zusammenfassung()
fahrt.rechne_gesamtzeit()

odo = Odometer()
odo.lese_odometer(fahrt.fitfile)

# Replace all 'None' by 0s and calc. mean excluding zeros:
fahrt.hf    = np.array([e if e is not None else 0 for e in fahrt.hf])
af    = np.mean(fahrt.hf[fahrt.hf > 0])
if np.isnan(af):
    af = 0
fahrt.cad   = np.array([e if e is not None else 0 for e in fahrt.cad])
ac    = np.mean(fahrt.cad[fahrt.cad > 0])
if np.isnan(ac):
    ac = 0

fahrt.power = np.array([e if e is not None else 0 for e in fahrt.power])
fahrt.powt   = [e if e is not None else 0 for e in fahrt.powt]
fahrt.powt   = smooth(fahrt.powt, const.smooth_Pprint)
Pprint = smooth(fahrt.power, const.smooth_Pprint)
P30    = smooth(fahrt.power, const.smooth_P30)
if any(P30 > 0):
    NPcalc = int(np.sqrt(np.sqrt(np.mean(np.power(P30[P30 > 0],4)))))
    print("Normierte Leistung Gerät/Berechnet:  %d/%d W" % (fahrt.session.NP, NPcalc))

if fahrt.session.NP == 0:
    if af == 0:
        print("Keine Leistung und keine HF verfuegbar, schaetze TSS mit 80% Intensitaet")
        tss = int(fahrt.session.zeit / 3600 * 80)
    else:
        tss = int(fahrt.session.zeit / 3600 * af / const.zonen[4] * 100)
else:
    tss = (fahrt.session.NP / float(const.FTP) * fahrt.session.zeit / 3600 * 100)
print("TSS = %d" % tss)
if not('kCal' in locals()):
    if af > 0:
        print("Kein KCal Wert vom Gerät, schätze kCal aus avHF und Zeit")
        kCal = int(af * fahrt.session.zeit / 3600 * 4.431)
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
while max(fahrt.T)*stretch_T < (const.max_hf / 2 * 1.1):
    stretch_T = stretch_T*2
while max(fahrt.T)*stretch_T > (const.max_hf * 1.1):
    stretch_T = stretch_T/2
print ("stretch_temperature: " + str(stretch_T))

############## Plots:
try:
    fahrt.cad = np.array(fahrt.cad)
    fahrt.cad[fahrt.cad > 130] = None
    fahrt.cad[fahrt.cad < 30] = None
    gnd = min(fahrt.alt) - min(fahrt.alt) % 50
except:
    print("Keine Kadenz verfuegbar")

stretch_speed = 1
if max(fahrt.speed) > 0:
    while max(fahrt.speed)*stretch_speed < const.max_hf/2*1.1:
        stretch_speed = stretch_speed*2

print("stretch_speed: " + str(stretch_speed))

TB = np.zeros(len(const.zonen)+1)
strZonen  = " "
#print(range(0,len(const.zonen)))
for i in range(0,(len(const.zonen))):
  if i == (len(const.zonen)-1):
    if fahrt.session.NP == 0:
      TB[i] = sum(j > const.zonen[i]  for j in list(filter(None, fahrt.hf)))
      messageZ = ("(HF >%2d Schläge) " % (const.zonen[i]))
    else:
      TB[i] = sum(j > const.tbPow[i]  for j in list(filter(None,P30)))
      messageZ = ("(>%2d W) " % (const.tbPow[i]))
  else:
    if fahrt.session.NP == 0:
      TB[i] = sum(((j > const.zonen[i]) and (j <= const.zonen[i+1])) for j in list(filter(None, fahrt.hf)))
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
    ax.set_title("%s on %s" % (fahrt.session.sport, fahrt.session.startzeit.strftime("%A, %b. %d, %Y")))
    ax.set_ylim([0,const.max_hf])
    ax.grid(color='k', linestyle=':', linewidth=1)
    plt.xlabel('Distance (km)')
    plt.ylabel('Cadence, Speed, HF')
    ax2 = ax.twinx()
    ax2.set_prop_cycle(cycler('color', ['k']))
    ax2.set_ylabel('Altitude')

    plt.rc('lines', linewidth=2)

    for i in range(0, len(fahrt.Runden)):
        ax.text(np.mean([fahrt.Runden[i].s_linie, fahrt.Runden[i].e_linie]), 170, ("Runde %d" % (i + 1)), color='y')
        ax.text(np.mean([fahrt.Runden[i].s_linie, fahrt.Runden[i].e_linie]), 161, ("%d km" % (fahrt.Runden[i].x / 1000)), color='y')
        ax.text(np.mean([fahrt.Runden[i].s_linie, fahrt.Runden[i].e_linie]), 152, ("%d km/h" % (round(fahrt.Runden[i].speed))), color='y')
        ax.text(np.mean([fahrt.Runden[i].s_linie, fahrt.Runden[i].e_linie]), 143, ("%d HS" % fahrt.Runden[i].HF), color='y')
        ax.text(np.mean([fahrt.Runden[i].s_linie, fahrt.Runden[i].e_linie]), 134, ("%d W" % fahrt.Runden[i].power), color='y')
        ax.text(np.mean([fahrt.Runden[i].s_linie, fahrt.Runden[i].e_linie]), 125, ("%02d:%02d:%02d" % (fahrt.Runden[i].h, fahrt.Runden[i].m, fahrt.Runden[i].s)), color='y')
        ax.vlines(fahrt.Runden[i].s_linie, [0], [200], lw=2, color='y')
        ax.vlines(fahrt.Runden[i].e_linie, [0], [200], lw=2, color='y')
    for i in range(0, len(fahrt.Zwischen)):
        ax.text(np.mean([fahrt.Zwischen[i].x_start, fahrt.Zwischen[i].x_end]) / 1000, 170, ("Zwischen %d" % (i + 1)), color='y')
        ax.text(np.mean([fahrt.Zwischen[i].x_start, fahrt.Zwischen[i].x_end]) / 1000, 161, ("%d km" % (fahrt.Zwischen[i].x / 1000)), color='y')
        ax.text(np.mean([fahrt.Zwischen[i].x_start, fahrt.Zwischen[i].x_end]) / 1000, 152, ("%d km/h" % (round(fahrt.Zwischen[i].speed))), color='y')
        ax.text(np.mean([fahrt.Zwischen[i].x_start, fahrt.Zwischen[i].x_end]) / 1000, 143, ("%d HS" % fahrt.Zwischen[i].HF), color='y')
        ax.text(np.mean([fahrt.Zwischen[i].x_start, fahrt.Zwischen[i].x_end]) / 1000, 134, ("%d W" % fahrt.Zwischen[i].power), color='y')
        ax.text(np.mean([fahrt.Zwischen[i].x_start, fahrt.Zwischen[i].x_end]) / 1000, 125, ("%02d:%02d:%02d" % (fahrt.Zwischen[i].h, fahrt.Zwischen[i].m, fahrt.Zwischen[i].s)), color='y')

    ax.plot(np.divide(fahrt.xcad, 1000), fahrt.cad, lw=0.5, label ="Cadence")
    ax.plot(np.divide(fahrt.xspeed, 1000), np.multiply(fahrt.speed, stretch_speed), label='Speed$\cdot$' + str(stretch_speed))
    ax.plot(np.divide(fahrt.xhf, 1000), fahrt.hf, label="HF")
    ax.plot(np.divide(fahrt.xpow, 1000), np.multiply(Pprint, stretch_power), label='Power$\cdot$' + str(stretch_power), lw=1)
    ax.plot([-1,-1],[0, 1],lw=1,label = 'Altitude')
    ax.hlines(const.zonen, [0], [max(fahrt.x) / 1000], lw=1, colors='r')
    ax.hlines(const.tbPow * stretch_power, [0], [max(fahrt.x) / 1000], lw=1, colors='m')
    if args.plot_hoehe == 1:
        ax2.plot(np.divide(fahrt.xalt, 1000), fahrt.alt, lw=1)
    ax2.set_xlim([0, max(fahrt.x) / 1000])

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
    ax.set_title("%s on %s" % (fahrt.session.sport, fahrt.session.startzeit.strftime("%A, %b. %d, %Y")))
    ax.set_ylim([0,const.max_hf])
    ax.grid(color='k', linestyle=':', linewidth=1)
    ax.hlines(const.zonen, [0], [fahrt.session.totalzeit], lw=1)
    for i in range(0, len(fahrt.Runden)):
      ax.text(np.mean([fahrt.Runden[i].s_zeitlinie, fahrt.Runden[i].e_zeitlinie]), 170, ("Runde %d" % (i + 1)), color='y')
      ax.text(np.mean([fahrt.Runden[i].s_zeitlinie, fahrt.Runden[i].e_zeitlinie]), 161, ("%d km/h" % fahrt.Runden[i].speed), color='y')
      ax.text(np.mean([fahrt.Runden[i].s_zeitlinie, fahrt.Runden[i].e_zeitlinie]), 152, ("%02d:%02d:%02d" % (fahrt.Runden[i].h, fahrt.Runden[i].m, fahrt.Runden[i].s)), color='y')
      ax.vlines(fahrt.Runden[i].s_zeitlinie, [0], [200], lw=2, color='y')
      ax.vlines(fahrt.Runden[i].e_zeitlinie, [0], [200], lw=2, color='y')
    for i in range(0, len(fahrt.Zwischen)):
        ax.text(np.mean([fahrt.Zwischen[i].z_start, fahrt.Zwischen[i].z_end]) / 3600, 170, ("Zwischen %d" % (i + 1)), color='y')
        ax.text(np.mean([fahrt.Zwischen[i].z_start, fahrt.Zwischen[i].z_end]) / 3600, 161, ("%d km/h" % fahrt.Zwischen[i].speed), color='y')
        ax.text(np.mean([fahrt.Zwischen[i].z_start, fahrt.Zwischen[i].z_end]) / 3600, 152, ("%02d:%02d:%02d" % (fahrt.Zwischen[i].h, fahrt.Zwischen[i].m, fahrt.Zwischen[i].s)), color='y')

    plt.xlabel('Time (h)')
    plt.ylabel('Cadence, Speed, HF')
    ax2 = ax.twinx()
    ax2.set_prop_cycle(cycler('color', ['k']))
    ax2.set_ylabel('Altitude')

    plt.rc('lines', linewidth=2)

    ax.plot(np.linspace(0, len(fahrt.T) / 3600, len(fahrt.T)), np.multiply(fahrt.T, stretch_T), lw=0.2, color="orange", label ="Temperature$\cdot$" + str(stretch_T))
    ax.plot(np.linspace(0, len(fahrt.cad) / 3600, len(fahrt.cad)), fahrt.cad, lw=0.5, label ="Cadence")
    ax.plot(np.linspace(0, len(fahrt.speed) / 3600, len(fahrt.speed)), np.multiply(fahrt.speed, stretch_speed), label='Speed$\cdot$' + str(stretch_speed))
    ax.plot(np.linspace(0, len(fahrt.hf) / 3600, len(fahrt.hf)), fahrt.hf, label="HF")
    ax.plot(np.linspace(0,len(Pprint)/3600,len(Pprint)),np.multiply(Pprint,stretch_power), label='Power$\cdot$'+str(stretch_power),lw=1)
    ax.plot([-1,-1],[0, 1],lw=1,label = 'Altitude')
    if args.plot_hoehe == 1:
        ax2.plot(np.linspace(0, len(fahrt.alt) / 3600, len(fahrt.alt)), fahrt.alt, lw=1)
    ax.set_xlim([0, len(fahrt.speed) / 3600])

    ax.legend(loc='best')
    #ax.legend(('Cadence','Speed$\cdot$'+str(stretch_speed),'HF','Altitude'),'best')

    plt.show()

################# Nach Uhrzeit: ###########################################################################

if args.plot_pause == 1:
    plt.xkcd()
    fig = plt.figure(figsize=fenster)
    ax = fig.add_subplot(1, 1, 1)
    ax.set_prop_cycle(cycler('color', ['c', 'b', 'r', 'm', 'k']))
    ax.set_title("%s on %s" % (fahrt.session.sport, fahrt.session.startzeit.strftime("%A, %b. %d, %Y")))
    ax.set_ylim([0,const.max_hf])
    ax.grid(color='k', linestyle=':', linewidth=1)
    ax.hlines(const.zonen, [fahrt.t[0] / 3600], [fahrt.t[-1] / 3600], lw=1)
    # ax.vlines(ereignis,[0],[200],lw=2,color='g')
    for i in range(0, len(fahrt.Runden)):
        ax.vlines(fahrt.Runden[i].s_pauslinie, [0], [200], lw=2, color='y')
        ax.vlines(fahrt.Runden[i].e_pauslinie, [0], [200], lw=2, color='y')
        ax.text(np.mean([fahrt.Runden[i].s_pauslinie, fahrt.Runden[i].e_pauslinie]), 170, ("Runde %d" % (i + 1)), color='y')
    for i in range(0, len(fahrt.Zwischen)):
        ax.text(np.mean([fahrt.Zwischen[i].t_start, fahrt.Zwischen[i].t_end]) / 3600, 170, ("Zwischen %d" % (i + 1)), color='y')
    plt.xlabel('Time (h)')
    plt.ylabel('Cadence, Speed, HF')
    ax2 = ax.twinx()
    ax2.set_prop_cycle(cycler('color', ['k']))
    ax2.set_ylabel('Altitude')

    plt.rc('lines', linewidth=2)

    #ax.plot(np.linspace(0,len(cad)/3600,len(cad)),cad,lw=0.5, label = "Cadence")
    ax.plot(fahrt.tcad, fahrt.cadt, lw=0.5, label ="Cadence")
    ax.plot(fahrt.tspeed, np.multiply(fahrt.speedt, stretch_speed), label='Speed$\cdot$' + str(stretch_speed))
    #ax.plot(np.linspace(0,len(thf)/3600,len(hft)),hft, label="HF")
    ax.plot(fahrt.thf, fahrt.hft, label="HF")
    ax.plot(fahrt.tpow, np.multiply(fahrt.powt, stretch_power), label='Power$\cdot$' + str(stretch_power), lw=1)
    ax.plot([-1,-1],[0, 1],lw=1,label = 'Altitude')
    #ax2.plot(np.linspace(0,len(alt)/3600,len(alt)),alt,lw=1)
    if args.plot_hoehe == 1:
        ax2.plot(fahrt.talt, fahrt.altt, lw=1)
    ax.set_xlim([fahrt.t[0] / 3600, fahrt.t[-1] / 3600])

    ax.legend(loc='best')
    #ax.legend(('Cadence','Speed$\cdot$'+str(stretch_speed),'HF','Altitude'),'best')

    plt.show()

############### Critical Power:  ######################################################
args.CP30 = 0
if (args.CP == 1) and any(fahrt.power > 0):
    steps = 30
    Int   = [0]*int(max(fahrt.power))
    Pint  = [0]*int(max(fahrt.power))
    # Methode 1: schau, wie viele Sekunden über bestimmter Leistung waren, unabhängig, ob zusammenhängendes Intervall
    for i in range(const.lower_Plimit,len(Pint)):
        Int[i] = i
        Pint[i] = len(fahrt.power[fahrt.power > i])
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
        Psmooth = smooth(fahrt.power, i * step_size)
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
if (len(fahrt.Runden) > 0) & (args.plot_bar == 1):
    bar_r = np.zeros(len(fahrt.Alle))
    bar_x = np.zeros(len(fahrt.Alle))
    bar_v = np.zeros(len(fahrt.Alle))
    bar_p = np.zeros(len(fahrt.Alle))
    bar_h = np.zeros(len(fahrt.Alle))
    for i in range(0, len(fahrt.Alle)):
        bar_r[i] = i+1
        bar_x[i] = fahrt.Alle[i].x / 1000
        bar_v[i] = fahrt.Alle[i].speed
        bar_p[i] = fahrt.Alle[i].power
        bar_h[i] = fahrt.Alle[i].anstieg

    plt.xkcd()
    fig = plt.figure(figsize=fenster)
    ax = fig.add_subplot(1, 1, 1)
    ax.grid(color='k', linestyle=':', linewidth=1)
    plt.xlabel('Runde')
    plt.ylabel('km, km/h')
    ax.bar(bar_r-0.3,bar_x,0.2,lw=2, color="orange", label = "km")
    ax.bar(bar_r-0.1,bar_v,0.2,lw=2, color="blue", label = "km/h")
    ax.bar(bar_r + 0.1, np.zeros(len(fahrt.Alle)), 0.2, lw=2, color="m", label ="Leistung")
    ax.bar(bar_r + 0.3, np.zeros(len(fahrt.Alle)), 0.2, lw=2, color="grey", label ="Anstieg")
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

rstr = ("%0.2f; %0.1f; %02d:%02d:%02d; %0.1f; %02d" % (fahrt.session.strecke / 1000, fahrt.session.avspeed, fahrt.h, fahrt.m, fahrt.s, fahrt.session.v_max, kCal))
rstr = ("%s ; %02d; %02d; %02d; %02d; %02d; %02d; %s %02d:%02d:%02d; %s;;" % (rstr, af, fahrt.session.NP, args.CP30, ac, fahrt.session.anstieg, tss, odo.kmstr, fahrt.hp, fahrt.mp, fahrt.sp, strZonen))
for i in range(0, len(fahrt.Alle)):
    rstr = (rstr +" %0.2f; %0.2f; %02d:%02d:%02d; %02d; %02d; %02d; %0.1f;" % (fahrt.Alle[i].x / 1000, fahrt.Alle[i].speed, fahrt.Alle[i].h, fahrt.Alle[i].m, fahrt.Alle[i].s, fahrt.Alle[i].HF, fahrt.Alle[i].power, fahrt.Alle[i].anstieg, fahrt.Alle[i].v_max))
rstr = rstr.replace('.',',')
rstr = ("%d.%d.; ;%d;%2d:%2d:%2d;%s" % (fahrt.session.startzeit.day, fahrt.session.startzeit.month, odo.bike_id, fahrt.session.startzeit.hour, fahrt.session.startzeit.minute, fahrt.session.startzeit.second, rstr))

print("Markiere diese Zeile inklusive \">\" und kopiere sie in die Tabelle: ")
print(rstr)
print(">")

ueberschrift1 = "Allgemein;;;;;Zusammenfassung;;;;;;;;;;;km-Stand;;;;;;Trainingsbereiche;;;;;;;"
for i in range(0, len(fahrt.Runden)):
    ueberschrift1 = (ueberschrift1 + "Runde %d;;;;;;" % (i+1))
ueberschrift2 = ("Datum;Strecke;Rad;Start;Ges.-km;av;Ges.zeit;max;kCal;Puls;Leistung;CP30;Kad;hm;tss;stress;" + (((str(odo.raeder)).replace(',',';')).replace('(','')).replace(')','') + ";Pausenzeit;TB0;TB1;TB2;TB3;TB4;Anm.;Rad - rep;")
for i in range(0, len(fahrt.Runden)):
    ueberschrift2 = (ueberschrift2 + "km;av;Zeit;Puls;Power;hm;max;")

if args.print_csv == 1:
    file = open(fahrt.csvdatei, "w")
    file.write(ueberschrift1 + "\r\n")
    file.write(ueberschrift2 + "\r\n")
    file.write(rstr)
    file.close()
