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
from Konstanten import *
from Ausfahrt import *
from Math import *
from Odometer import *
from Plots import *
import os
os.chdir("..")

###################################### Settings ####################################################
const = Konstanten()
args = Argumente()
args.read_arguments(sys.argv)
fahrt = Ausfahrt()
fen1 = fahrt.get_filename(args)

###################################### Files lesen ####################################################
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
    zeichnungen.crit_power_plot(const, CP)
    plt.show()

############### Barplot:            ######################################################
if (len(fahrt.Runden) > 0) & (args.plot_bar == 1):
    zeichnungen.barplot(fahrt.Alle)
    plt.show()

zeile = Text()
zeile.print_text_f_tabelle(fahrt.session, odo, CP, fahrt.Alle, fahrt.Runden, args.print_csv, fahrt.csvdatei)
