import pandas as pd
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

test_df = pd.read_csv('Test_Data_2_bit_ps.csv')


rx = []
tx = []
s21 = []
for index,row in test_df.iterrows():
    rx_bin = str(test_df['rx_codewords'].iloc[index])
    rx_int = int(rx_bin,2)
    rx.append(rx_int)

    tx_bin = str(test_df['tx_codewords'].iloc[index])
    tx_int = int(tx_bin,2)
    tx.append(tx_int)

    s21.append(test_df['S21 [dB]'].iloc[index])

fig = plt.figure(1)
ax = fig.add_subplot(1,1,1,projection='3d')
ax.scatter3D(rx,tx,s21)
plt.xlabel('TX Codeword')
plt.ylabel('RX Codeword')

plt.show()