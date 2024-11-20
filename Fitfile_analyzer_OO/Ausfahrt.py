from tkinter import *
from tkinter import filedialog
from fitparse import FitFile
import glob
import os
from Math import *

class Ausfahrt:
    def __init__(self):
        self.fitfile = None
        self.csvdatei = None
        self.Runden = []
        self.Zwischen = []
        self.session = Zusammenfassung()
        self.Alle  = []
        self.x     = []
        self.t     = []
        self.speed = [] # Geschwindigkeit vs. Fahrzeit
        self.speedt= [] # Geschwindigkeit vs. Uhrzeit
        self.xspeed= [] # Weg Achse für Geschwindigkeit
        self.tspeed= [] # Uhrzeit Achse für Geschwindigkeit
        self.hf    = [] # Herzfrequnez vs. Fahrzeit
        self.hft   = [] # etc.
        self.xhf   = []
        self.thf   = []
        self.power = []
        self.powt  = []
        self.xpow  = []
        self.tpow  = []
        self.cad   = []
        self.cadt  = []
        self.xcad  = []
        self.tcad  = []
        self.alt   = []
        self.altt  = []
        self.xalt  = []
        self.talt  = []
        self.T     = [] # Temperatur
        self.tT    = []

    def get_filename(self,args):
        list_of_files = glob.glob('[0-9]*.fit') # Search for newest Fitfile beginning with a number
        latest_file = max(list_of_files, key=os.path.getctime)
        print ("Neueste Ausfahrt: %s" % latest_file)

        fen1 = Tk()                              # Create window
        fen1.title("FitFileParser")
        T = Text(fen1, height=5, width=40)
        T.pack()
        T.insert(END, "Asking for filename\n\n")
        name = filedialog.askopenfilename(filetypes=[("Fit files","*.fit")],initialfile=latest_file)
        self.fitfile = FitFile(name)
        self.csvdatei = name.replace('fit','csv')
        T.insert(END, "Parsing %s\n" % (os.path.basename(name)))
        if args.print_csv == 1:
            T.insert(END, "Will create %s\n" % (os.path.basename(self.csvdatei)))
        else:
            T.insert(END, "\n")
        T.insert(END, "Wait a moment...\n")
        fen1.update()

        return fen1

    def read_all_records(self):
        # Get all data messages that are of type record
        for record in self.fitfile.get_messages('record'):
            # Go through all the data entries in this record
            if record.get_value('distance') is not None:
                self.x.append(record.get_value('distance'))
            else:
                self.x.append(self.x[-1])
            self.T.append(record.get_value('temperature'))
            zs = datetime_to_local(record.get_value('timestamp'))
            temp = zs.second + zs.minute*60 + zs.hour*3600
            try:
                if temp < self.t[-1]:
                    temp = temp + 24*3600
                self.t.append(temp)
            except:
                self.t = [temp]
            temp = record.get_value('enhanced_speed')
            if temp is not None:
                self.speedt.append(temp * 3.6)
                self.tspeed.append((self.t[-1] / float(3600)))
                self.speed.append(temp * 3.6)
                self.xspeed.append(self.x[-1])
            self.hft.append(record.get_value('heart_rate'))
            try:
                self.thf.append(self.t[-1] / float(3600))
            except:
                del self.hft[-1]
            try:
              if self.speedt[-1] != 0:
                self.hf.append(self.hft[-1])
                self.xhf.append((self.x[-1]))
            except:
              pass
            self.powt.append(record.get_value('power'))
            try:
                self.tpow.append(self.t[-1] / float(3600))
            except:
                del self.powt[-1]
            try:
              if self.speedt[-1] != 0:
                self.power.append(self.powt[-1])
                self.xpow.append(self.x[-1])
            except:
                pass

            self.altt.append(record.get_value('enhanced_altitude'))
            try:
                self.talt.append(self.t[-1] / float(3600))
            except:
                del self.altt[-1]
            try:
              if self.speedt[-1] != 0:
                self.alt.append(self.altt[-1])
                self.xalt.append(self.x[-1])
            except:
              pass
            self.cadt.append(record.get_value('cadence'))
            try:
                self.tcad.append(self.t[-1] / float(3600))
            except:
                del self.cadt[-1]
            try:
              if self.speedt[-1] != 0:
                self.cad.append(self.cadt[-1])
                self.xcad.append(self.x[-1])
            except:
              pass

    def debug_print(self):
        for record in self.fitfile.get_messages('record'):
            for record_data in record:
                if record_data.units:
                    print(" * %s: %s %s" % (record_data.name, record_data.value, record_data.units))
                # Print the records name and value (and units if it has any)
                else:
                    print(" * %s: %s" % (record_data.name, record_data.value))
            print()

        for record in self.fitfile.get_messages('event'):
            for record_data in record:
                if record_data.units:
                    print(" * %s: %s %s" % (record_data.name, record_data.value, record_data.units))
                # Print the records name and value (and units if it has any)
                else:
                    print(" * %s: %s" % (record_data.name, record_data.value))
            print()
            
    def lese_runden(self):
        for Laps in self.fitfile.get_messages('lap'):
            self.Runden.append(Runde())
            print("Runde " + str(len(self.Runden)))
            for record_data in Laps:
                if record_data.name == "start_time":
                    zs   = datetime_to_local(record_data.value)
                    temp = zs.second + zs.minute*60 + zs.hour*3600
                    self.Runden[-1].t_start = temp
                    idx = (np.abs(np.asarray(self.t) - temp)).argmin()
                    self.Runden[-1].z_start = idx
                    self.Runden[-1].x_start = self.x[idx]
                if record_data.name == "timestamp":
                    zs   = datetime_to_local(record_data.value)
                    temp = zs.second + zs.minute*60 + zs.hour*3600
                    self.Runden[-1].t_end = temp
                    idx = (np.abs(np.asarray(self.t) - temp)).argmin()
                    self.Runden[-1].z_end = idx
                    self.Runden[-1].zeit = self.Runden[-1].z_end - self.Runden[-1].z_start
                    self.Runden[-1].x_end = self.x[idx]
                if record_data.name == "total_distance":
                    self.Runden[-1].x = record_data.value
                if record_data.name == "avg_speed":
                    self.Runden[-1].speed = record_data.value*3.6
                if record_data.name == "total_elapsed_time":
                    self.Runden[-1].gzeit = record_data.value
                if record_data.name == "avg_heart_rate":
                    self.Runden[-1].HF = record_data.value
                    if self.Runden[-1].HF is None:
                        self.Runden[-1].HF = 0
                if record_data.name == "avg_power":
                    self.Runden[-1].power = record_data.value
                    if self.Runden[-1].power is None:
                        self.Runden[-1].power = 0
                if record_data.name == "total_ascent":
                    self.Runden[-1].anstieg = record_data.value
                if record_data.name == "max_speed":
                    self.Runden[-1].v_max = record_data.value*3.6
                if record_data.units:
                    print(" * %s: %s %s" % (record_data.name, record_data.value, record_data.units))
                else:
                    print(" * %s: %s" % (record_data.name, record_data.value))
                self.Runden[-1].h = np.floor(self.Runden[-1].zeit/3600)
                self.Runden[-1].m = np.floor((self.Runden[-1].zeit - self.Runden[-1].h*3600)/60)
                self.Runden[-1].s = self.Runden[-1].zeit - self.Runden[-1].h*3600 - self.Runden[-1].m*60
                self.Runden[-1].s_linie = self.Runden[-1].x_start/1000
                self.Runden[-1].s_zeitlinie = self.Runden[-1].z_start/3600
                self.Runden[-1].s_pauslinie = self.Runden[-1].t_start/3600
                self.Runden[-1].e_linie = self.Runden[-1].x_end/1000
                self.Runden[-1].e_zeitlinie = self.Runden[-1].z_end/3600
                self.Runden[-1].e_pauslinie = self.Runden[-1].t_end/3600
                self.Runden[-1].pos = ((np.abs(np.array(self.xspeed) - self.Runden[-1].e_linie * 1000)).argmin())
            print()

    def finde_zwischen_runden(self, schwelle):
        # Check, ob zwischen den Runden > 5 km sind, dann mach eine zusätzliche Runde draus:
        self.Alle     = self.Runden[:]
        i = 0
        a = 0
        if len(self.Runden) > 0:
            if (self.Runden[0].x_start - self.x[0]) > schwelle:
                self.Zwischen.append(Runde())
                self.Zwischen[-1].x_start = self.x[0]
                self.Zwischen[-1].x_end = self.Runden[0].x_start
                self.Zwischen[-1].z_start = 0
                self.Zwischen[-1].z_end = self.Runden[0].z_start
                self.Zwischen[-1].t_start = self.t[0]
                self.Zwischen[-1].t_end = self.Runden[0].t_start
                self.Zwischen[-1].x = self.Runden[0].x_start
                self.Zwischen[-1].zeit = self.Runden[0].z_start
                self.Alle.insert(0,self.Zwischen[-1])
                a = 1
            if len(self.Runden) > 1:
                for i in range(1,len(self.Runden)):
                    if (self.Runden[i].x_start - self.Runden[i-1].x_end) > schwelle:
                        self.Zwischen.append(Runde())
                        self.Zwischen[-1].x = self.Runden[i].x_start - self.Runden[i-1].x_end
                        self.Zwischen[-1].zeit = self.Runden[i].z_start - self.Runden[i-1].z_end
                        self.Zwischen[-1].z_start = self.Runden[i-1].z_end
                        self.Zwischen[-1].z_end = self.Runden[i].z_start
                        self.Zwischen[-1].t_start = self.Runden[i-1].t_end
                        self.Zwischen[-1].t_end = self.Runden[i].t_start
                        self.Zwischen[-1].x_start = self.Runden[i-1].x_end
                        self.Zwischen[-1].x_end = self.Runden[i].x_start
                        self.Alle.insert(i + a,self.Zwischen[-1])
                        a = a + 1
            if (self.x[-1] - self.Runden[-1].x_end) > schwelle:
                self.Zwischen.append(Runde())
                self.Zwischen[-1].x = self.x[-1] - self.Runden[-1].x_end
                self.Zwischen[-1].z_start = self.Runden[-1].z_end
                self.Zwischen[-1].z_end = len(self.tspeed) # =len(hf)???
                self.Zwischen[-1].t_start = self.Runden[-1].t_end
                self.Zwischen[-1].t_end = self.t[-1]
                self.Zwischen[-1].zeit = len(self.tspeed) - self.Runden[-1].z_end
                self.Zwischen[-1].x_start = self.Runden[-1].x_end
                self.Zwischen[-1].x_end = self.x[-1]
                self.Alle.append(self.Zwischen[-1])

        for i in range(0,len(self.Zwischen)):
            self.Zwischen[i].h = np.floor(self.Zwischen[i].zeit/3600)
            self.Zwischen[i].m = np.floor((self.Zwischen[i].zeit - self.Zwischen[i].h*3600)/60)
            self.Zwischen[i].s = self.Zwischen[i].zeit - self.Zwischen[i].h*3600 - self.Zwischen[i].m*60
            self.Zwischen[i].speed = self.Zwischen[i].x/self.Zwischen[i].zeit*3.6
            self.Zwischen[i].v_max = max(self.speed[self.Zwischen[i].z_start:self.Zwischen[i].z_end])
            auf = np.diff(self.alt[self.Zwischen[i].z_start:self.Zwischen[i].z_end])
            auf[auf < 0] = 0
            self.Zwischen[i].anstieg = sum(auf)
            try:
                hfz = np.array(self.hf[self.Zwischen[i].z_start:self.Zwischen[i].z_end])
                hfz = list(filter(None,hfz))
                self.Zwischen[i].HF = sum(hfz)/len(hfz)
            except:
                print("Keine HF für Zwischenstrecke verfuegbar")
            try:
                pz = np.array(self.power[self.Zwischen[i].z_start:self.Zwischen[i].z_end])
                pz = list(filter(None,pz))
                self.Zwischen[i].power = sum(pz)/len(pz)
            except:
                print("Keine Leistung für Zwischenstrecke verfuegbar")

    def lese_zusammenfassung(self):
        for Summary in self.fitfile.get_messages('session'):
            print("Zusammenfassung")
            print("===============")
            for record_data in Summary:
                if record_data.name == "total_distance":
                    self.session.strecke = record_data.value
                if record_data.name == "avg_speed":
                    self.session.avspeed = record_data.value*3.6
                if record_data.name == "total_timer_time":
                    self.session.zeit = record_data.value
                if record_data.name == "avg_heart_rate":
                    self.session.HF = record_data.value
                if record_data.name == "normalized_power":
                    self.session.NP = record_data.value
                if record_data.name == "total_ascent":
                    self.session.anstieg = record_data.value
                if record_data.name == "total_discent":
                    self.session.abstieg = record_data.value
                if record_data.name == "max_speed":
                    self.session.v_max = record_data.value*3.6
                if record_data.name == "total_calories":
                    self.session.kCal = record_data.value
                if record_data.name == "total_work":
                    if record_data.value is not None:
                        if record_data.value > 0:
                            self.session.kCal = record_data.value/1000
                if record_data.name == "total_elapsed_time":
                    self.session.totalzeit = record_data.value
                if record_data.name == "avg_cadence":
                    self.session.kadenz = record_data.value
                if record_data.name == "start_time":
                    self.session.startzeit = datetime_to_local(record_data.value)
                if record_data.name == "sport":
                    self.session.sport = record_data.value
                if record_data.units:
                    print(" * %s: %s %s" % (record_data.name, record_data.value, record_data.units))
                else:
                    print(" * %s: %s" % (record_data.name, record_data.value))
            print()


class Runde:
    def __init__(self):
        self.x = 0
        self.x_start = 0
        self.x_end = 0
        self.zeit = 0  # Fahrzeit
        self.t_start = 0  # t = Uhrzeit
        self.t_end = 0
        self.z_start = 0
        self.z_end = 0
        self.speed = 0
        self.h = 0
        self.m = 0
        self.s = 0
        self.gzeit = 0  # Gesamtzeit
        self.HF = 0
        self.power = 0
        self.anstieg = 0
        self.v_max = 0
        self.pos = 0
        self.s_linie = 0
        self.s_zeitlinie = 0
        self.s_pauslinie = 0
        self.e_linie = 0
        self.e_zeitlinie = 0
        self.e_pauslinie = 0

class Zusammenfassung:
    def __init__(self):
        self.strecke = 0
        self.avspeed = 0
        self.zeit = 0
        self.HF = 0
        self.NP = 0
        self.anstieg = 0
        self.abstieg = 0
        self.v_max = 0
        self.kCal = 0
        self.totalzeit = 0
        self.kadenz = 0
        self.startzeit = 0
        self.sport = 0
