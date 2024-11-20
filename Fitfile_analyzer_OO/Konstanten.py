import numpy as np
import sys

class Konstanten:
    def __init__(self):
        self.zonen = [0, 138, 149, 160, 170]  # HF zone limits
        self.FTP = 255
        self.lower_Plimit = int(self.FTP / 2)
        self.raeder = ('MTB', '2er', 'Poison', 'Sab', 'Leihrad')  # Bike names
        self.tbPow = np.multiply([0, 0.55, 0.75, 0.9, 1.05], float(self.FTP))  # Power zones
        self.smooth_Pprint = 600  #
        self.smooth_P30 = 30
        self.max_hf = 180  # for scaling the plots
        self.schwelle_zwischen = 3000

class Argumente:
    def __init__(self):
        self.debug_print = 0  # show all records for debugging purposes
        self.plot_weg = 1  # plot data vs. distance
        self.plot_zeit = 1  # plot data vs. time
        self.plot_pause = 1  # plot data vs. time including pauses (plot vs. Uhrzeit)
        self.plot_hoehe = 1  # plot altitude profile
        self.CP = 1  # calculate critical power?
        self.plot_bar = 1  # Runden-Barplot?
        self.print_csv = 0  # generate .csv file with result
        self.Fitness = 0  # correction of heart rate (for bad days)
        self.bike_id = 1  # default bike profile in case it can't be read from file

    ################ check arguments: #################################################################
    def read_arguments(self, argv):
        if len(argv) > 1:
            self.plot_weg    = int(sys.argv[1])
            if len(sys.argv) > 2:
                self.plot_zeit   = int(sys.argv[2])
                if len(sys.argv) > 3:
                    self.plot_pause  = int(sys.argv[3])
                    if len(sys.argv) > 4:
                        self.CP  = int(sys.argv[4])
                        if len(sys.argv) > 5:
                            self.plot_bar  = int(sys.argv[5])
                            if len(sys.argv) > 6:
                                self.print_csv = int(sys.argv[6])
