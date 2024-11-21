import matplotlib.pyplot as plt
import numpy as np

class Text:
    def __init__(self):
        pass

    def print_text_f_tabelle(self, session, odo, CP, Alle, Runden, print_csv, csvdatei):
        rstr = ("%0.2f; %0.1f; %02d:%02d:%02d; %0.1f; %02d" % (session.strecke / 1000, session.avspeed, session.h, session.m, session.s, session.v_max, session.kCal))
        rstr = ("%s ; %02d; %02d; %02d; %02d; %02d; %02d; %s %02d:%02d:%02d; %s;;" % (rstr, session.av_hf, session.NP, CP.CP30, session.av_cad, session.anstieg, session.tss, odo.kmstr, session.hp, session.mp, session.sp, session.strZonen))
        for i in range(0, len(Alle)):
            rstr = (rstr +" %0.2f; %0.2f; %02d:%02d:%02d; %02d; %02d; %02d; %0.1f;" % (Alle[i].x / 1000, Alle[i].speed, Alle[i].h, Alle[i].m, Alle[i].s, Alle[i].HF, Alle[i].power, Alle[i].anstieg, Alle[i].v_max))
        rstr = rstr.replace('.',',')
        rstr = ("%d.%d.; ;%d;%2d:%2d:%2d;%s" % (session.startzeit.day, session.startzeit.month, odo.bike_id, session.startzeit.hour, session.startzeit.minute, session.startzeit.second, rstr))

        print("Markiere diese Zeile inklusive \">\" und kopiere sie in die Tabelle: ")
        print(rstr)
        print(">")

        ueberschrift1 = "Allgemein;;;;;Zusammenfassung;;;;;;;;;;;km-Stand;;;;;;Trainingsbereiche;;;;;;;"
        for i in range(0, len(Runden)):
            ueberschrift1 = (ueberschrift1 + "Runde %d;;;;;;" % (i+1))
        ueberschrift2 = ("Datum;Strecke;Rad;Start;Ges.-km;av;Ges.zeit;max;kCal;Puls;Leistung;CP30;Kad;hm;tss;stress;" + (((str(odo.raeder)).replace(',',';')).replace('(','')).replace(')','') + ";Pausenzeit;TB0;TB1;TB2;TB3;TB4;Anm.;Rad - rep;")
        for i in range(0, len(Runden)):
            ueberschrift2 = (ueberschrift2 + "km;av;Zeit;Puls;Power;hm;max;")

        if print_csv == 1:
            file = open(csvdatei, "w")
            file.write(ueberschrift1 + "\r\n")
            file.write(ueberschrift2 + "\r\n")
            file.write(rstr)
            file.close()
class Plots:
    def __init__(self):
        self.fenster = [19.5, 10]

    def barplot(self, alle):
        bar_r = np.zeros(len(alle))
        bar_x = np.zeros(len(alle))
        bar_v = np.zeros(len(alle))
        bar_p = np.zeros(len(alle))
        bar_h = np.zeros(len(alle))
        for i in range(0, len(alle)):
            bar_r[i] = i+1
            bar_x[i] = alle[i].x / 1000
            bar_v[i] = alle[i].speed
            bar_p[i] = alle[i].power
            bar_h[i] = alle[i].anstieg

        plt.xkcd()
        fig = plt.figure(figsize=self.fenster)
        ax = fig.add_subplot(1, 1, 1)
        ax.grid(color='k', linestyle=':', linewidth=1)
        plt.xlabel('Runde')
        plt.ylabel('km, km/h')
        ax.bar(bar_r-0.3,bar_x,0.2,lw=2, color="orange", label = "km")
        ax.bar(bar_r-0.1,bar_v,0.2,lw=2, color="blue", label = "km/h")
        ax.bar(bar_r + 0.1, np.zeros(len(alle)), 0.2, lw=2, color="m", label ="Leistung")
        ax.bar(bar_r + 0.3, np.zeros(len(alle)), 0.2, lw=2, color="grey", label ="Anstieg")
        plt.xticks(bar_r)
        ax.legend(loc='best')

        ax2 = ax.twinx()
        # ax2.set_prop_cycle(cycler('color', ['k']))
        ax2.set_ylabel('W, hm')
        ax2.bar(bar_r+0.1,bar_p,0.2,lw=2, color="m", label = "Leistung")
        ax2.bar(bar_r+0.3,bar_h,0.2,lw=2, color="grey", label = "Anstieg")
        ax.legend(loc='best')

        plt.show()
