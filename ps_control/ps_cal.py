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
for i in range(1,501,1):
    # Dividing by 10 makes the floating point magic work out
    Voltage_List.append(i/100)

print(Voltage_List)

array_list = ['rx']
antenna_list = [1,2,3]

i = 0
# AntennaNum_List = [4,8,12] # TX
AntennaNum_List = [1,5,9] # RX

# Type_List = ['I','I','I']
Type_List = ['Q','Q','Q'] # RX





for array in array_list:
    for antenna in antenna_list:
        # Initialize a new measurements list for each antenna
        measurements = []
        input("\nSwitch the feed to {0}_{1}, and press enter to calibrate.".format(array, antenna))

        AntennaNum = AntennaNum_List[i]
        Type = Type_List[i]

        print('To Arduino: ',AntennaNum,Type)

        phase_dict = {'Voltage': Voltage_List}
        for Voltage in Voltage_List:
            # Write the voltages to the Arduino
            ser_connection.write(str(AntennaNum).encode())
            ser_connection.write(str(Type).encode())
            ser_connection.write(str(Voltage).encode())

            raw = ser_connection.read_until('\n'.encode())#.decode()
            print(raw)

            # Set I voltage; 2 Seconds should be safe
            sleep(1)

            # Read marker phase value from network analyzer
            phase = pna.readMarker(phase_name,phase_trace)

            # Append the latest phase to the measurements list
            measurements.append(phase)

            print(Voltage," Volts ", phase," Deg")

        # Add entry in dictionary mapping label to measurements list
        label = "{0}_{1}".format(array, antenna)
        phase_dict[label] = measurements
        i += 1
        print(phase_dict)

        df = pd.DataFrame.from_dict(phase_dict)

        df.to_csv('Phase_Cal_{0}.csv'.format(label))