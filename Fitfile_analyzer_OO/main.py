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
################# Nach Weg: #############################################################
if args.plot_weg == 1:
    zeichnungen.wegplot(args, const, skala, fahrt)
    plt.show()

################# Nach Zeit (ohne Pausen): ##############################################
if args.plot_zeit == 1:
    zeichnungen.zeitplot(args, const, skala, fahrt)
    plt.show()

################# Nach Uhrzeit: ########################################################
if args.plot_pause == 1:
    zeichnungen.uhrzeitplot(args, const, skala, fahrt)
    plt.show()

############### Critical Power:  ######################################################
fenster = [19.5, 10]
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
