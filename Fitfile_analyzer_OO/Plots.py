import matplotlib.pyplot as plt
import numpy as np
from cycler import cycler
from mpl_toolkits.axes_grid1.inset_locator import inset_axes # , zoomed_inset_axes

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

    def wegplot(self, args, const, skala, fahrt):
        plt.xkcd()
        fig = plt.figure(figsize=self.fenster)
        # manager = plt.get_current_fig_manager()
        # manager.window.maximize() # does not work??
        # mng = plt.get_current_fig_manager()
        # mng.resize(*mng.window.maximize()) # maximizes over all screens
        ax = fig.add_subplot(1, 1, 1)
        ax.set_prop_cycle(cycler('color', ['c', 'b', 'r', 'm', 'k']))
        ax.set_title("%s on %s" % (fahrt.session.sport, fahrt.session.startzeit.strftime("%A, %b. %d, %Y")))
        ax.set_ylim([0,const.max_hf])
        ax.grid(color='k', linestyle=':', linewidth=1)
        plt.xlabel('Distance (km)')
        plt.ylabel('Cadence, Speed, HF')
        ax2 = ax.twinx()
        ax2.set_prop_cycle(cycler('color', ['k']))
        ax2.set_ylabel('Altitude')

        plt.rc('lines', linewidth=2)

        for i in range(0, len(fahrt.Runden)):
            ax.text(np.mean([fahrt.Runden[i].s_linie, fahrt.Runden[i].e_linie]), 170, ("Runde %d" % (i + 1)), color='y')
            ax.text(np.mean([fahrt.Runden[i].s_linie, fahrt.Runden[i].e_linie]), 161, ("%d km" % (fahrt.Runden[i].x / 1000)), color='y')
            ax.text(np.mean([fahrt.Runden[i].s_linie, fahrt.Runden[i].e_linie]), 152, ("%d km/h" % (round(fahrt.Runden[i].speed))), color='y')
            ax.text(np.mean([fahrt.Runden[i].s_linie, fahrt.Runden[i].e_linie]), 143, ("%d HS" % fahrt.Runden[i].HF), color='y')
            ax.text(np.mean([fahrt.Runden[i].s_linie, fahrt.Runden[i].e_linie]), 134, ("%d W" % fahrt.Runden[i].power), color='y')
            ax.text(np.mean([fahrt.Runden[i].s_linie, fahrt.Runden[i].e_linie]), 125, ("%02d:%02d:%02d" % (fahrt.Runden[i].h, fahrt.Runden[i].m, fahrt.Runden[i].s)), color='y')
            ax.vlines(fahrt.Runden[i].s_linie, [0], [200], lw=2, color='y')
            ax.vlines(fahrt.Runden[i].e_linie, [0], [200], lw=2, color='y')
        for i in range(0, len(fahrt.Zwischen)):
            ax.text(np.mean([fahrt.Zwischen[i].x_start, fahrt.Zwischen[i].x_end]) / 1000, 170, ("Zwischen %d" % (i + 1)), color='y')
            ax.text(np.mean([fahrt.Zwischen[i].x_start, fahrt.Zwischen[i].x_end]) / 1000, 161, ("%d km" % (fahrt.Zwischen[i].x / 1000)), color='y')
            ax.text(np.mean([fahrt.Zwischen[i].x_start, fahrt.Zwischen[i].x_end]) / 1000, 152, ("%d km/h" % (round(fahrt.Zwischen[i].speed))), color='y')
            ax.text(np.mean([fahrt.Zwischen[i].x_start, fahrt.Zwischen[i].x_end]) / 1000, 143, ("%d HS" % fahrt.Zwischen[i].HF), color='y')
            ax.text(np.mean([fahrt.Zwischen[i].x_start, fahrt.Zwischen[i].x_end]) / 1000, 134, ("%d W" % fahrt.Zwischen[i].power), color='y')
            ax.text(np.mean([fahrt.Zwischen[i].x_start, fahrt.Zwischen[i].x_end]) / 1000, 125, ("%02d:%02d:%02d" % (fahrt.Zwischen[i].h, fahrt.Zwischen[i].m, fahrt.Zwischen[i].s)), color='y')

        ax.plot(np.divide(fahrt.x_cad, 1000), fahrt.cad, lw=0.5, label ="Cadence")
        ax.plot(np.divide(fahrt.x_speed, 1000), np.multiply(fahrt.speed, skala.speed), label='Speed$\cdot$' + str(skala.speed))
        ax.plot(np.divide(fahrt.xhf, 1000), fahrt.hf, label="HF")
        ax.plot(np.divide(fahrt.x_pow, 1000), np.multiply(fahrt.Pprint, skala.power), label='Power$\cdot$' + str(skala.power), lw=1)
        ax.plot([-1,-1],[0, 1],lw=1,label = 'Altitude')
        ax.hlines(const.zonen, [0], [max(fahrt.x) / 1000], lw=1, colors='r')
        ax.hlines(const.tbPow * skala.power, [0], [max(fahrt.x) / 1000], lw=1, colors='m')
        if args.plot_hoehe == 1:
            ax2.plot(np.divide(fahrt.x_alt, 1000), fahrt.alt, lw=1)
        ax2.set_xlim([0, max(fahrt.x) / 1000])

        ax.legend(loc='best')
        #ax.legend(('Cadence','Speed$\cdot$'+str(skala.speed),'HF','Altitude'),'best')

        if not all(fahrt.session.TB[0:5] == 0):
            labels = 'TB0','TB1','TB2','TB3','TB4'
            tb = fahrt.session.TB[0:5]
            explode = (0.05, 0.05, 0.05, 0.5,1)
            colors = ['lightskyblue', 'yellowgreen', 'yellow', 'orange', 'lightcoral']
            axins = inset_axes(ax,
                      width=1.5,  # width = 30% of parent_bbox
                      height=1.5,  # height : 1 inch
                      loc=3)
            patches, texts, autotexts = plt.pie(tb, explode=explode, colors=colors, labels=labels, startangle=90,
                autopct='%.0f%%', shadow=True, radius=1)
            # Make the labels on the small plot easier to read.
            for te in texts:
                te.set_size('smaller')
            for te in autotexts:
                te.set_size('x-small')
            autotexts[0].set_color('y')

            fig.patch.set_alpha(0)
            ax2.patch.set_alpha(0.5)
            axins.patch.set_alpha(1)

    def zeitplot(self, args, const, skala, fahrt):
        plt.xkcd()
        fig = plt.figure(figsize=self.fenster)
        ax = fig.add_subplot(1, 1, 1)
        ax.set_prop_cycle(cycler('color', ['c', 'b', 'r', 'm', 'k']))
        ax.set_title("%s on %s" % (fahrt.session.sport, fahrt.session.startzeit.strftime("%A, %b. %d, %Y")))
        ax.set_ylim([0,const.max_hf])
        ax.grid(color='k', linestyle=':', linewidth=1)
        ax.hlines(const.zonen, [0], [fahrt.session.totalzeit], lw=1)
        for i in range(0, len(fahrt.Runden)):
          ax.text(np.mean([fahrt.Runden[i].s_zeitlinie, fahrt.Runden[i].e_zeitlinie]), 170, ("Runde %d" % (i + 1)), color='y')
          ax.text(np.mean([fahrt.Runden[i].s_zeitlinie, fahrt.Runden[i].e_zeitlinie]), 161, ("%d km/h" % fahrt.Runden[i].speed), color='y')
          ax.text(np.mean([fahrt.Runden[i].s_zeitlinie, fahrt.Runden[i].e_zeitlinie]), 152, ("%02d:%02d:%02d" % (fahrt.Runden[i].h, fahrt.Runden[i].m, fahrt.Runden[i].s)), color='y')
          ax.vlines(fahrt.Runden[i].s_zeitlinie, [0], [200], lw=2, color='y')
          ax.vlines(fahrt.Runden[i].e_zeitlinie, [0], [200], lw=2, color='y')
        for i in range(0, len(fahrt.Zwischen)):
            ax.text(np.mean([fahrt.Zwischen[i].z_start, fahrt.Zwischen[i].z_end]) / 3600, 170, ("Zwischen %d" % (i + 1)), color='y')
            ax.text(np.mean([fahrt.Zwischen[i].z_start, fahrt.Zwischen[i].z_end]) / 3600, 161, ("%d km/h" % fahrt.Zwischen[i].speed), color='y')
            ax.text(np.mean([fahrt.Zwischen[i].z_start, fahrt.Zwischen[i].z_end]) / 3600, 152, ("%02d:%02d:%02d" % (fahrt.Zwischen[i].h, fahrt.Zwischen[i].m, fahrt.Zwischen[i].s)), color='y')

        plt.xlabel('Time (h)')
        plt.ylabel('Cadence, Speed, HF')
        ax2 = ax.twinx()
        ax2.set_prop_cycle(cycler('color', ['k']))
        ax2.set_ylabel('Altitude')

        plt.rc('lines', linewidth=2)

        ax.plot(np.linspace(0, len(fahrt.T) / 3600, len(fahrt.T)), np.multiply(fahrt.T, skala.temp), lw=0.2, color="orange", label ="Temperature$\cdot$" + str(skala.temp))
        ax.plot(np.linspace(0, len(fahrt.cad) / 3600, len(fahrt.cad)), fahrt.cad, lw=0.5, label ="Cadence")
        ax.plot(np.linspace(0, len(fahrt.speed) / 3600, len(fahrt.speed)), np.multiply(fahrt.speed, skala.speed), label='Speed$\cdot$' + str(skala.speed))
        ax.plot(np.linspace(0, len(fahrt.hf) / 3600, len(fahrt.hf)), fahrt.hf, label="HF")
        ax.plot(np.linspace(0,len(fahrt.Pprint)/3600,len(fahrt.Pprint)),np.multiply(fahrt.Pprint,skala.power), label='Power$\cdot$'+str(skala.power),lw=1)
        ax.plot([-1,-1],[0, 1],lw=1,label = 'Altitude')
        if args.plot_hoehe == 1:
            ax2.plot(np.linspace(0, len(fahrt.alt) / 3600, len(fahrt.alt)), fahrt.alt, lw=1)
        ax.set_xlim([0, len(fahrt.speed) / 3600])
        ax.legend(loc='best')

    def uhrzeitplot(self, args, const, skala, fahrt):
        plt.xkcd()
        fig = plt.figure(figsize=self.fenster)
        ax = fig.add_subplot(1, 1, 1)
        ax.set_prop_cycle(cycler('color', ['c', 'b', 'r', 'm', 'k']))
        ax.set_title("%s on %s" % (fahrt.session.sport, fahrt.session.startzeit.strftime("%A, %b. %d, %Y")))
        ax.set_ylim([0,const.max_hf])
        ax.grid(color='k', linestyle=':', linewidth=1)
        ax.hlines(const.zonen, [fahrt.t[0] / 3600], [fahrt.t[-1] / 3600], lw=1)
        for i in range(0, len(fahrt.Runden)):
            ax.vlines(fahrt.Runden[i].s_pauslinie, [0], [200], lw=2, color='y')
            ax.vlines(fahrt.Runden[i].e_pauslinie, [0], [200], lw=2, color='y')
            ax.text(np.mean([fahrt.Runden[i].s_pauslinie, fahrt.Runden[i].e_pauslinie]), 170, ("Runde %d" % (i + 1)), color='y')
        for i in range(0, len(fahrt.Zwischen)):
            ax.text(np.mean([fahrt.Zwischen[i].t_start, fahrt.Zwischen[i].t_end]) / 3600, 170, ("Zwischen %d" % (i + 1)), color='y')
        plt.xlabel('Time (h)')
        plt.ylabel('Cadence, Speed, HF')
        ax2 = ax.twinx()
        ax2.set_prop_cycle(cycler('color', ['k']))
        ax2.set_ylabel('Altitude')

        plt.rc('lines', linewidth=2)
        ax.plot(fahrt.t_cad, fahrt.cad_t, lw=0.5, label ="Cadence")
        ax.plot(fahrt.t_speed, np.multiply(fahrt.speed_t, skala.speed), label='Speed$\cdot$' + str(skala.speed))
        ax.plot(fahrt.thf, fahrt.hft, label="HF")
        ax.plot(fahrt.t_pow, np.multiply(fahrt.pow_t, skala.power), label='Power$\cdot$' + str(skala.power), lw=1)
        ax.plot([-1,-1],[0, 1],lw=1,label = 'Altitude')
        if args.plot_hoehe == 1:
            ax2.plot(fahrt.t_alt, fahrt.alt_t, lw=1)
        ax.set_xlim([fahrt.t[0] / 3600, fahrt.t[-1] / 3600])

        ax.legend(loc='best')

    def crit_power_plot(self, const, CP):
        plt.xkcd()
        fig = plt.figure(figsize=self.fenster)
        ax = fig.add_subplot(1, 1, 1)
        ax.grid(color='k', linestyle=':', linewidth=1)
        plt.xlabel('Intervall (min)')
        plt.ylabel('Leistung (W)')
        # ax.plot(np.divide(Pint[const.lower_Plimit:-1],60),np.linspace((const.lower_Plimit + 1),len(Pint)-(const.lower_Plimit + 1),len(Pint)-(const.lower_Plimit + 1))+(const.lower_Plimit + 1),lw=2, color="blue", label = "Critical Power")
        ax.plot(np.divide(CP.Pint[const.lower_Plimit:-1],60),CP.Int[const.lower_Plimit:-1],lw=2, color="blue", label = "Critical Power, Method 1")
        ax.plot(np.divide(CP.Pint2,60),CP.Int2,lw=2, color="green", marker='x', label = "Critical Power, Method 2")
        ax.legend(loc='best')


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
