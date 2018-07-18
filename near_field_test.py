import pandas as pd

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


print(rx1_phases_df.head())
print(rx2_phases_df.head())
print(rx3_phases_df.head())

print(tx1_phases_df.head())
print(tx2_phases_df.head())
print(tx3_phases_df.head())
