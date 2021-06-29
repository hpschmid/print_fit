# print_fit
Python skript to analyze *.fit training files
Python3
Author: Gerhard Schmid

Requirements:
Fitfileparser
Tkinter
Matplotlib

Wie es funktioniert:

- print_fit3.py ausführen
- fit-Datei wählen (default ist neueste Datei)
- Plot-Zeile(n) kopieren und in Tabelle "AllRad" von ...Training.ods einfügen (siehe Koieren.png und Einfuegen.png)
	- Alternativ: .csv-Datei erstellen (setze print_csv   = 1) und von dort kopieren
- Spaß haben

Odometerstände werden ausgelesen, ist für Bryton, SRM und Igpsport implementiert. Bei Bryton System.ini von Gerät kopieren, bei SRM Totals.fit, bei Igpsport user.fit.
