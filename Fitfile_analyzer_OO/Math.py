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


class CriticalPower:
    def __init__(self,power):
        self.CP30 = 0
        self.steps = 15
        self.Int   = [0]*int(max(power))
        self.Pint  = [0]*int(max(power))
        self.max_interval = 150*60
        self.step_size = int(self.max_interval/self.steps)
        self.Int2  = [0]*len(range(1,self.steps+1))
        self.Pint2 = [0]*len(range(1,self.steps+1))


    def berechne_kritische_leistung(self, const, power, P30):
        # Methode 1: schau, wie viele Sekunden über bestimmter Leistung waren, unabhängig, ob zusammenhängendes Intervall
        for i in range(const.lower_Plimit,len(self.Pint)):
            self.Int[i] = i
            self.Pint[i] = len(power[power > i])
        # Methode 2: smoothen über Intervalllänge, nimm maximum, d.h. nur zusammenhängende Intervalle werden genommen, aber Durchschnitt
        self.Int2[0] = max(P30)
        self.Pint2[0] = 30 # Vergrößere Intervalle um je 5 min (sonst dauerts extrem lange)
        for i in range(1,self.steps):
            print('Berechne max. Leistung für %d min (bis %d)...' % (i*self.step_size/60, self.max_interval/60), end='\r')
            Psmooth = smooth(power, i * self.step_size)
            self.Int2[i] = max(Psmooth)
            self.Pint2[i] = i*self.step_size# Vergrößere Intervalle um je 5 min (sonst dauerts extrem lange)
        print('\nFertig!\n')
        self.CP30 = self.Int2[3-1]
        print('CP30 = %d' % self.CP30)

