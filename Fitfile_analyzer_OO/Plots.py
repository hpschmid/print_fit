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
