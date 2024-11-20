from tkinter import *
from tkinter import filedialog
from fitparse import FitFile
import glob
import os

class Ausfahrt:
    def __init__(self):
        self.fitfile = None
        self.csvdatei = None
        self.Runden = None
        self.x     = []
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
