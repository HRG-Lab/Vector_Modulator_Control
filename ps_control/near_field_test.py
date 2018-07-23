import pandas as pd
from itertools import product
import numpy as np
import serial
import ps_control.network_analyzer as network_analyzer
from time import sleep



ps_bits = 1
phase_tolerance = 5

pna_address = ('10.0.0.3',5025)
serial_port = '/dev/ttyACM0'
baud_rate = 115200

freq = 2400
start = 2000
stop = 3000
freq_units = 'MHz'

# Initialize Serial Connection to Arduino
ser_connection = serial.Serial(serial_port,baud_rate)

# Initialize Network Analyzer
pna = network_analyzer.network_analyzer(pna_address,False) # Create pna object

s_param = "S12"
mag_name = "mag_trace"
mag_trace = 2
pna.clear_calcs()
pna.set_freq(start,stop,freq_units)
pna.init_s_measurement(1,mag_name,mag_trace,s_param,"MLOG",freq,freq_units)


### Generates the phase dictionary for a single antenna
def generate_phase_dict(phase_shifter_bits):
    bin_format = '{0:0' + str(phase_shifter_bits) + 'b}'
    num_states = 2 ** phase_shifter_bits
    states_list = []
    phase = 0#np.pi/4
    del_phase = 2 * np.pi / num_states
    print("Del phase",180*del_phase/np.pi)
    for state in range(num_states):
        states_list.append((bin_format.format(state), phase))
        phase += del_phase
        print(phase*180/np.pi)
    phase_map = dict(states_list)
    print(phase_map)
    return phase_map


## Expands a phase dictionary from a single antenna to cover code words for arbitrary numbers of antennas
def expand_phase_dictionary(single_antenna_phase_dict, num_antennas):
    new_dict_list = []
    keys = sorted(single_antenna_phase_dict.keys())
    print("Generating New Codebook")
    new_key_combinations = sorted(product(keys, repeat=num_antennas))

    print("\nAdding all ", len(new_key_combinations), " New codewords to List\n")
    for key_combo in new_key_combinations:
        value_list = []
        for key in key_combo:
            value_list.append(single_antenna_phase_dict[key])
        new_dict_list.append((''.join(key_combo), value_list))
    print("Creating Dict from new Codebook")
    return dict(new_dict_list)


# Parameters are an antenna to phase dictionary and a list of voltage dicts
# corresponding to each antenna in the array
def generate_voltage_codebook(antenna_phase_dict,voltage_dict_list):
    num_antennas = len(voltage_dict_list)
    keys = sorted(antenna_phase_dict.keys())
    new_key_combinations = sorted(product(keys,repeat=num_antennas))

    new_codeword_dict = {}
    for key_combo in new_key_combinations:

        # Generate next full codeword
        next_codeword = ''
        for key in key_combo:
            next_codeword += key

        next_voltage_list = []
        for i in range(num_antennas):
            key = key_combo[i]
            if key in voltage_dict_list[i]:
                next_voltage_list.append(voltage_dict_list[i][key])
            else:
                break

        if len(next_voltage_list) == num_antennas:
            new_codeword_dict[next_codeword] = next_voltage_list
    # for voltage_dict in voltage_dict_list:

    return new_codeword_dict


# Read in Cal file for every phase shifter
rx1_phases_df = pd.read_csv('Phase_Cal_rx_1.csv')
rx2_phases_df = pd.read_csv('Phase_Cal_rx_2.csv')
rx3_phases_df = pd.read_csv('Phase_Cal_rx_3.csv')
tx1_phases_df = pd.read_csv('Phase_Cal_tx_1.csv')
tx2_phases_df = pd.read_csv('Phase_Cal_tx_2.csv')
tx3_phases_df = pd.read_csv('Phase_Cal_tx_3.csv')

print(rx1_phases_df.head())

# Determine which min value should be used as zero phase
rx1_min = rx1_phases_df['rx_1'].iloc[0]
zero = rx1_min

print(zero)
rx2_min = rx2_phases_df['rx_2'].iloc[0]
if rx2_min > zero:
    zero = rx2_min

rx3_min = rx3_phases_df['rx_3'].iloc[0]
if rx3_min > zero:
    zero = rx3_min

tx1_min = tx1_phases_df['tx_1'].iloc[0]
if tx1_min > zero:
    zero = tx1_min

tx2_min = tx2_phases_df['tx_2'].iloc[0]
if tx2_min > zero:
    zero = tx2_min

tx3_min = tx3_phases_df['tx_3'].iloc[0]
if tx3_min > zero:
    zero = tx3_min

# Subtract off zero phase from all dataframes
rx1_phases_df['rx_1'] -= zero
rx2_phases_df['rx_2'] -= zero
rx3_phases_df['rx_3'] -= zero
tx1_phases_df['tx_1'] -= zero
tx2_phases_df['tx_2'] -= zero
tx3_phases_df['tx_3'] -= zero


# Function Looks up the voltage key corresponding to the closest phase to parametre
def get_voltage_key(desired_phase,dataframe,phase_key):
    phase_series = dataframe[phase_key] # Get phases from dataframe
    diff_series = abs(phase_series - desired_phase) # Calculate the difference between phases and desired phase
    min_diff = diff_series.min() # Get minimum difference

    if min_diff > phase_tolerance:
        # If difference is greater than 3 degrees return -1
        # To signal voltage not found
        return (-1,min_diff)
    else:
        # Get index of closest phase values
        index = diff_series[diff_series==min_diff].index[0]
        # Return voltage closest to desired phase value
        return (dataframe['Voltage'].iloc[index], dataframe[phase_key].iloc[index])

# Create Empty dicts for codeword/voltage maps
rx1_voltage_map = {}
rx2_voltage_map = {}
rx3_voltage_map = {}
tx1_voltage_map = {}
tx2_voltage_map = {}
tx3_voltage_map = {}

# Use Generate Phase dict to map codewords to
phase_dict = generate_phase_dict(ps_bits)

# Iterate through codeword-phase dict
for key, value in phase_dict.items():
    degrees = value*180/np.pi
    # print('x,',degrees)

    (rx1_v,rx1_phase) = get_voltage_key(degrees,rx1_phases_df,'rx_1')
    (rx2_v,rx2_phase) = get_voltage_key(degrees,rx2_phases_df,'rx_2')
    (rx3_v,rx3_phase) = get_voltage_key(degrees,rx3_phases_df,'rx_3')

    (tx1_v,tx1_phase) = get_voltage_key(degrees,tx1_phases_df,'tx_1')
    (tx2_v,tx2_phase) = get_voltage_key(degrees,tx2_phases_df,'tx_2')
    (tx3_v,tx3_phase) = get_voltage_key(degrees,tx3_phases_df,'tx_3')

    if not (rx1_v< 0):
        rx1_voltage_map[key] = rx1_v
    if not (rx2_v< 0):
        rx2_voltage_map[key] = rx2_v
    if not (rx3_v< 0):
        rx3_voltage_map[key] = rx3_v

    if not (tx1_v< 0):
        tx1_voltage_map[key] = tx1_v
    if not (tx2_v< 0):
        tx2_voltage_map[key] = tx2_v
    if not (tx3_v< 0):
        tx3_voltage_map[key] = tx3_v



print('rx1 voltages:',rx1_voltage_map)
print('rx2 voltages:',rx2_voltage_map)
print('rx3 voltages:',rx3_voltage_map,'\n')

print('tx1 voltages:',tx1_voltage_map)
print('tx2 voltages:',tx2_voltage_map)
print('tx3 voltages:',tx3_voltage_map)


rx_codebook = generate_voltage_codebook(phase_dict,[rx1_voltage_map,rx2_voltage_map,rx3_voltage_map])
tx_codebook = generate_voltage_codebook(phase_dict,[tx1_voltage_map,tx2_voltage_map,tx3_voltage_map])




for rx_codeword in rx_codebook.keys():
    rx_voltages = rx_codebook[rx_codeword]

    # Set voltages for rx codeword
    rx_antenna_list = [1,5,9]
    for i in range(3):
        antenna_num = rx_antenna_list[i]
        ser_connection.write(str(i+1).encode())
        ser_connection.write('Q'.encode())
        ser_connection.write(str(rx_voltages[i]).encode())

        # Reads most recent state from Arduino
        raw = ser_connection.read_until('\n'.encode())  # .decode()
        print(raw)
        sleep(1) # Wait one second for phase to change

    for tx_codeword in tx_codebook.keys():
        tx_voltages = tx_codebook[tx_codeword]
        tx_antenna_list = [4,8,12]
        # Set voltages for tx codeword
        for i in range(3):
            antenna_num = tx_antenna_list[i]
            ser_connection.write(str(antenna_num).encode())
            ser_connection.write('I'.encode())
            ser_connection.write(str(tx_voltages[i]).encode())

            # Reads most recent state from Arduino
            raw = ser_connection.read_until('\n'.encode())  # .decode()
            print(raw)
            sleep(1)  # Wait one second for phase to change

        sleep(1) # Wait one more second before measurement
        S21 = pna.readMarker(mag_name,mag_trace)