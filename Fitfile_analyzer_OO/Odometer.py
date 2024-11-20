from fitparse import FitFile

class Odometer:
    def __init__(self):
        self.hersteller = "Default"
        self.bike = "Default"
        self.raeder = ('MTB', '2er', 'Poison', 'Sab', 'Leihrad')  # Bike names
        self.bike_id = 1  # default bike profile in case it can't be read from file
        self.id_final = 1
        self.km = [0,0,0,0,0]
        self.kmstr = [' ;',' ;',' ;',' ;',' ;',' ;']

    def lese_odometer(self, fitfile):
        for file_id in fitfile.get_messages('file_id'):
            for record_data in file_id:
                if record_data.name == "manufacturer":
                    hersteller = record_data.value
                    print('Hersteller erkannt: %s' % self.hersteller)

        if self.hersteller == "srm":
            for bike_profile in fitfile.get_messages('bike_profile'):
                for record_data in bike_profile:
                    if record_data.name == "name":
                        self.bike = record_data.value
                        self.bike_id = int(self.bike[-1])

                        totfile = FitFile('Totals.fit')
                        for totals in totfile.get_messages('unknown_65292'):
                            for record_data1 in totals:
                                if record_data1.name == "unknown_0":
                                    self.id_final = record_data1.value
                                    #print(" * %s: %s" % (record_data.name, record_data.value))
                                if record_data1.name == "unknown_3":
                                    self.km[self.id_final] = record_data1.value / 1000
                        self.bike = self.raeder[self.bike_id - 1]
                        self.id_final = self.bike_id

        # Bei Igpsport finde ich keinen Hinweise auf Radprofil, kann über Gewicht unterscheiden (alternativ Sensor-Id):
        elif self.hersteller == "igpsport":
            totfile = FitFile('user.fit')
            for totals in totfile.get_messages('bike_profile'):
                for record_data in totals:
                    if record_data.name == "bike_weight":
                        bike_weight = record_data.value
                        if bike_weight == 8:
                            self.bike_id = 1
                        elif bike_weight == 6:
                            self.bike_id = 2
                        elif bike_weight == 7:
                            self.bike_id = 3
                        else:
                            self.bike_id = 4
                        self.id_final = self.bike_id
                        self.bike = self.raeder[self.bike_id - 1]
            for totals in totfile.get_messages('bike_profile'):
                for record_data in totals:
                    if record_data.name == "odometer":
                        self.km[self.bike_id] = record_data.value/1000

        elif self.hersteller == "bryton":
            for bike_profile in fitfile.get_messages('unknown_68'):
                for record_data in bike_profile:
                    if record_data.name == "unknown_7":
                        self.id_final = record_data.value
                        self.bike_id = self.id_final
                        self.bike = self.raeder[0]
                        if self.id_final == 2:
                            self.bike_id = 3
                        elif self.id_final == 0x10:
                            self.bike_id = 2
                        elif self.id_final == 0x20:
                            self.bike_id = 4
                        self.bike = self.raeder[self.bike_id - 1]
                        #Beim Rider 450 ist 0x10 Rad 1 und 0x20 Rad 2, daher:
                        if self.id_final > 2:
                            self.id_final = self.id_final >> 4

                        #Remove \x00 at the end of the file (Korean coding?)
                        fileObject = open("System.ini", "r")
                        data = fileObject.read()
                        data = data.rstrip('\x00')
                        fileObject.close()
                        fileObject = open("System.ini", "w")
                        fileObject.write(data)
                        fileObject.close()
                        import configparser
                        config = configparser.ConfigParser()
                        config.read	("System.ini")
                        system = config['System']
                        trip2_str =('Trip2%d_km' % self.id_final)
                        self.km[self.bike_id] = system[trip2_str]
        elif self.hersteller == "garmin":
            for Summary in fitfile.get_messages('session'):
                for record_data in Summary:
                    if record_data.name == "unknown_110":
                        self.bike = record_data.value
                    if record_data.name == "unknown_178":
                        self.km[self.bike_id] = record_data.value
        else:
            print('Hersteller nicht implementiert, kann Odometer nicht lesen')

        self.kmstr[self.bike_id] = ("%s;" % str(self.km[self.bike_id]))
        self.kmstr = ('%s%s%s%s%s%s' % (self.kmstr[0],self.kmstr[1],self.kmstr[2],self.kmstr[3],self.kmstr[4],self.kmstr[5]))
        print("Rad: %s  (id: %d), Kilometerstand: %s" % (self.bike, self.id_final, str(self.km[self.bike_id])))
        print("===============")
        print()
