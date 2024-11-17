import numpy as np

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
        