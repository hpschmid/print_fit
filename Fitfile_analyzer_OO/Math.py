import numpy as np
from datetime import timezone

def smooth(y, box_pts):
    box = np.ones(box_pts)/box_pts
    y_smooth = np.convolve(y, box, mode='same')
    return y_smooth

def datetime_to_local(utc_datetime):
    offset = utc_datetime.replace(tzinfo=timezone.utc) - utc_datetime.astimezone(timezone.utc)
    return utc_datetime + offset

def berechne_trainingsbereiche(const, fahrt):
    intens_zonen = np.zeros(len(const.zonen)+1) # Intensitätszonen (Trainingsbereiche)
    text_zonen  = " "
    for i in range(0,(len(const.zonen))):
        if i == (len(const.zonen)-1):
            if fahrt.session.NP == 0:
                intens_zonen[i] = sum(j > const.zonen[i]  for j in list(filter(None, fahrt.hf)))
                message = ("(HF >%2d Schläge) " % (const.zonen[i]))
            else:
                intens_zonen[i] = sum(j > const.tbPow[i]  for j in list(filter(None,fahrt.P30)))
                message = ("(>%2d W) " % (const.tbPow[i]))
        else:
            if fahrt.session.NP == 0:
                intens_zonen[i] = sum(((j > const.zonen[i]) and (j <= const.zonen[i+1])) for j in list(filter(None, fahrt.hf)))
                message = ("(HF %2d - %2d) " % (const.zonen[i],const.zonen[i+1]))
            else:
                intens_zonen[i] = sum(((j > const.tbPow[i]) and (j <= const.tbPow[i+1])) for j in list(filter(None,fahrt.P30)))
                message = ("(%2d - %2d W) " % (const.tbPow[i],const.tbPow[i+1]))

        hz = np.floor(intens_zonen[i]/3600)
        mz = np.floor((intens_zonen[i] - hz*3600)/60)
        sz = intens_zonen[i] - hz*3600 - mz*60
        print("Training in Zone %d: %02d:%02d:%02d " % (i,hz,mz,sz) + message)
        text_zonen = ("%s %2d:%2d:%2d;" % (text_zonen,hz,mz,sz))

    return  intens_zonen, text_zonen

class Skalen:
    def __init__(self):
        self.speed = 1
        self.power = 1
        self.temp = 10

    def finde_skalierung(self, fahrt, const, power_print):
        if max(power_print) > 0:
            while max(power_print)*self.power < (const.max_hf / 2 * 1.1):
                self.power = self.power * 2
            while max(power_print)*self.power > (const.max_hf * 1.1):
                self.power = self.power / 2
            print ("stretch_power: " + str(self.power))

        while max(fahrt.T)*self.temp < (const.max_hf / 2 * 1.1):
            self.temp = self.temp * 2
        while max(fahrt.T)*self.temp > (const.max_hf * 1.1):
            self.temp = self.temp / 2
        print ("stretch_temperature: " + str(self.temp))

        if max(fahrt.speed) > 0:
            while max(fahrt.speed)*self.speed < const.max_hf/2*1.1:
                self.speed = self.speed * 2

        print("stretch_speed: " + str(self.speed))

