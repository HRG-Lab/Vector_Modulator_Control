import ps_control.network_analyzer as network_analyzer
import serial
import numpy as np
import pandas as pd
from time import sleep


pna_address = ('10.0.0.3',5025)
serial_port = '/dev/ttyACM0'
baud_rate = 115200

freq = 2400
start = 2000
stop = 3000
freq_units = 'MHz'

avg_count = 2

AntennaNum = 4
Type = 'I'
Voltage = 1.5

# Initialize Network Analyzer
pna = network_analyzer.network_analyzer(pna_address,False) # Create pna object

# The following commands replace the initialize() function from the old calibration code:
# Prepare the vna to read the phases from the markers

# Marker num corresponds to trace num in this program
s_param = "S12"
mag_name = "mag_trace"
mag_trace = 1

phase_trace = 2
phase_name = "phase_trace"

window = 1


pna.clear_calcs()

pna.set_freq(start,stop,freq_units)

pna.init_s_measurement(window,mag_name,mag_trace,s_param,"MLOG",freq,freq_units)
pna.init_s_measurement(window, phase_name, phase_trace, s_param, "UPH", freq, freq_units, 500)


# Initialize Serial Connection to Arduino
ser_connection = serial.Serial(serial_port,baud_rate)


# After initialization, loop through different voltages to read phases

Voltage_List = []
for i in range(5000):
    # Dividing by 10 makes the floating point magic work out
    Voltage_List.append(i/1000)

print(Voltage_List)

array_list = ['tx','rx']
antenna_list = [1,2,3]



phase_dict = {'Voltage':Voltage_List}
for array in array_list:
    for antenna in antenna_list:
        # Initialize a new measurements list for each antenna
        measurements = []
        for Voltage in Voltage_List:
            input("Switch the feed to {0}_{1}, and press enter to calibrate.".format(array,antenna))


            # Write the voltages to the Arduino
            ser_connection.write(str(AntennaNum).encode())
            ser_connection.write(str(Type).encode())
            ser_connection.write(str(Voltage).encode())

            # Set I voltage; 2 Seconds should be safe
            sleep(2)

            # Read marker phase value from network analyzer
            phase = pna.readMarker(phase_name,phase_trace)

            # Append the latest phase to the measurements list
            measurements.append(phase)

            print(Voltage," Volts ", phase," Deg")

        # Add entry in dictionary mapping label to measurements list
        label = "{0}_{1}".format(array, antenna)
        phase_dict[label] = measurements

df = pd.DataFrame.from_dict(phase_dict)

df.to_csv('Phase_Cal.csv')