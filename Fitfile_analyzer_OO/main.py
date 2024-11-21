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
from cycler import cycler

from Konstanten import *
from Ausfahrt import *
from Math import *
from Odometer import *
from Plots import *

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
fahrt.session.lese_zusammenfassung(fahrt.fitfile)
fahrt.session.rechne_gesamtzeit()
fahrt.filtere_werte(const)

odo = Odometer()
odo.lese_odometer(fahrt.fitfile)

fahrt.session.TB, fahrt.session.strZonen = berechne_trainingsbereiche(const, fahrt)
skala = Skalen()
skala.finde_skalierung(fahrt, const, fahrt.Pprint)

fen1.destroy()

zeichnungen = Plots()
################# Nach Weg: ###########################################################################
if args.plot_weg == 1:
    zeichnungen.wegplot(args, const, skala, fahrt)
    plt.show()

################# Nach Zeit (ohne Pausen): ###########################################################################
fenster = [19.5, 10]

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

    ax.plot(np.linspace(0, len(fahrt.T) / 3600, len(fahrt.T)), np.multiply(fahrt.T, skala.temp), lw=0.2, color="orange", label ="Temperature$\cdot$" + str(skala.temp))
    ax.plot(np.linspace(0, len(fahrt.cad) / 3600, len(fahrt.cad)), fahrt.cad, lw=0.5, label ="Cadence")
    ax.plot(np.linspace(0, len(fahrt.speed) / 3600, len(fahrt.speed)), np.multiply(fahrt.speed, skala.speed), label='Speed$\cdot$' + str(skala.speed))
    ax.plot(np.linspace(0, len(fahrt.hf) / 3600, len(fahrt.hf)), fahrt.hf, label="HF")
    ax.plot(np.linspace(0,len(fahrt.Pprint)/3600,len(fahrt.Pprint)),np.multiply(fahrt.Pprint,skala.power), label='Power$\cdot$'+str(skala.power),lw=1)
    ax.plot([-1,-1],[0, 1],lw=1,label = 'Altitude')
    if args.plot_hoehe == 1:
        ax2.plot(np.linspace(0, len(fahrt.alt) / 3600, len(fahrt.alt)), fahrt.alt, lw=1)
    ax.set_xlim([0, len(fahrt.speed) / 3600])
    ax.legend(loc='best')

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
    ax.plot(fahrt.t_cad, fahrt.cad_t, lw=0.5, label ="Cadence")
    ax.plot(fahrt.t_speed, np.multiply(fahrt.speed_t, skala.speed), label='Speed$\cdot$' + str(skala.speed))
    ax.plot(fahrt.thf, fahrt.hft, label="HF")
    ax.plot(fahrt.t_pow, np.multiply(fahrt.pow_t, skala.power), label='Power$\cdot$' + str(skala.power), lw=1)
    ax.plot([-1,-1],[0, 1],lw=1,label = 'Altitude')
    if args.plot_hoehe == 1:
        ax2.plot(fahrt.t_alt, fahrt.alt_t, lw=1)
    ax.set_xlim([fahrt.t[0] / 3600, fahrt.t[-1] / 3600])

    ax.legend(loc='best')

    plt.show()

############### Critical Power:  ######################################################
CP = CriticalPower(fahrt.power)
if (args.CP == 1) and any(fahrt.power > 0):

    CP.berechne_kritische_leistung(const, fahrt.power, fahrt.P30)

    plt.xkcd()
    fig = plt.figure(figsize=fenster)
    ax = fig.add_subplot(1, 1, 1)
    ax.grid(color='k', linestyle=':', linewidth=1)
    plt.xlabel('Intervall (min)')
    plt.ylabel('Leistung (W)')
    # ax.plot(np.divide(Pint[const.lower_Plimit:-1],60),np.linspace((const.lower_Plimit + 1),len(Pint)-(const.lower_Plimit + 1),len(Pint)-(const.lower_Plimit + 1))+(const.lower_Plimit + 1),lw=2, color="blue", label = "Critical Power")
    ax.plot(np.divide(CP.Pint[const.lower_Plimit:-1],60),CP.Int[const.lower_Plimit:-1],lw=2, color="blue", label = "Critical Power, Method 1")
    ax.plot(np.divide(CP.Pint2,60),CP.Int2,lw=2, color="green", marker='x', label = "Critical Power, Method 2")
    ax.legend(loc='best')

    plt.show()

############### Barplot:            ######################################################
if (len(fahrt.Runden) > 0) & (args.plot_bar == 1):
    zeichnungen.barplot(fahrt.Alle)

zeile = Text()
zeile.print_text_f_tabelle(fahrt.session, odo, CP, fahrt.Alle, fahrt.Runden, args.print_csv, fahrt.csvdatei)
