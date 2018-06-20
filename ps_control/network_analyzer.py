import ps_control.SCPI as SCPI

class network_analyzer(SCPI.SCPI):

    def __init__(self,address,reset):
        super().__init__(address,reset)
        print(self.identify())

    def clear_calcs(self):
        self.send('CALC:PAR:DEL:ALL')
        self.OPC()

    def calc_s_par(self,name,s_parameter):
        self.send('CALC:PAR \'{0}\', {1}'.format(name,s_parameter))
        self.OPC()


    # MLOG for log mag, PHAS for Phase, UPH for Unwrapped Phase
    # MLIN for linear mag, IMAG for imaginary, REAL for real, POL for polar
    # SMIT for smith chart, SADM for smith admittance, SWR for VSWR
    def format_calc(self,name,form):
        self.send('CALC:PAR:SEL \'{0}\''.format(name))
        self.send('CALC:FORM {0}'.format(form))
        self.OPC()

    def display_trace(self,window,trace,name):
        self.send('DISP:WIND{0}:TRAC{1}:FEED \'{2}\''.format(window,trace,name))
        self.OPC()

    def averaging_on(self,mode,count):
        self.send('SENS:AVER ON')
        self.send('SENS:AVER {0}'.format(mode))
        self.send('SENS:AVER:COUN {0}'.format(count))
        self.OPC()

    def clear_averages(self):
        self.send('SENS:AVER:CLE')
        self.OPC()

    def marker_on(self,num,freq,units):
        self.send('CALC:MARK{0} ON'.format(num))
        self.send('CALC:MARK{0}:X {1} {2}'.format(num,freq,units))
        self.OPC()

    def readMarker(self,trace_name,num):
        self.clear_averages()
        self.send('CALC:PAR:SEL \'{0}\''.format(trace_name))
        self.OPC()

        self.send('CALC:MARK{0}:Y?'.format(num))
        return float(self.receive(100)[0])

    def scaleY(self,window,trace,position,rlevel,pdiv):
        self.send('DISP:WIND{0}:TRAC{1}:Y:RPOS {2}'.format(window,trace,position))
        self.send('DISP:WIND{0}:TRAC{1}:Y:RLEV {2}'.format(window,trace,rlevel))
        self.send('DISP:WIND{0}:TRAC{1}:Y:PDIV {2}'.format(window,trace,pdiv))
        self.OPC()

    def set_freq(self,start,stop,units):
        self.send('SENS:FREQ:STAR {0} {1}'.format(start,units))
        self.send('SENS:FREQ:STOP {0} {1}'.format(stop,units))
        self.OPC()

    def init_s_measurement(self,window, name,trace,param,form,fo, f_units,div=10):
        self.calc_s_par(name, param)
        self.display_trace(window, trace, name)
        self.format_calc(name, form)
        self.scaleY(window, trace, 'MAX', 0, div)
        self.marker_on(trace, fo, f_units)
