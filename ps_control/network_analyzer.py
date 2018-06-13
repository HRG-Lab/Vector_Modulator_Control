import ps_control.SCPI as SCPI

class network_analyzer(SCPI):

    def __init__(self,address):
        super().__init__(address)
        print(self.identify())

    def clear_calcs(self):
        self.send('CALC:PAR:DEL:ALL')

    def averaging_on(self,mode,count):
        self.send('SENS:AVER ON')
        self.send('SENS:AVER {0}'.format(mode))
        self.send('SENS:AVER:COUN {0}'.format(count))

    def clear_averages(self):
        self.send('SENS:AVER:CLE')

    def marker_on(self,num,freq,units):
        self.send('CALC:MARK{0} ON'.format(num))
        self.send('CALC:MARK{0}:X {1} {2}'.format(num,freq,units))

    def readMarker(self,num):
        self.clear_averages()

        self.send('CALC:PAR:SEL CH1_S12_{0}'.format(num))

        self.send('CALC:MARK{0}:Y?')
        self.receive(100)