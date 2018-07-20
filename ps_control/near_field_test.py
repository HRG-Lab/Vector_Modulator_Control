import pandas as pd
from itertools import product
import numpy as np


ps_bits = 3
phase_tolerance = 5



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
    # bar = progressbar.ProgressBar(maxval=len(new_key_combinations), widgets=[progressbar.Bar('=', '[', ']'), ' ',
    #                                                                          progressbar.Percentage()])
    # bar.start()
    for key_combo in new_key_combinations:
        # bar.update(new_key_combinations.index(key_combo))
        value_list = []
        # print(key_combo)
        for key in key_combo:
            value_list.append(single_antenna_phase_dict[key])
        new_dict_list.append((''.join(key_combo), value_list))
    # bar.finish()
    print("Creating Dict from new Codebook")
    return dict(new_dict_list)





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

# Use Generate Phase dict to map codewords to
x = generate_phase_dict(ps_bits)

# Looks up the voltage key corresponding to the closest phase to parametre
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

# Iterate through codeword-phase dict
for key, value in x.items():
    degrees = value*180/np.pi
    # print('x,',degrees)

    (rx1_v,rx1_phase) = get_voltage_key(degrees,rx1_phases_df,'rx_1')
    print(key,rx1_v,degrees,rx1_phase)
    # print(rx1_phases_df)