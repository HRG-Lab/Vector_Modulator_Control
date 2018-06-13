import socket
import serial
import numpy as np
from numpy import pi
import matplotlib.pyplot as plt
from time import sleep
from time import time

startTime = time()

deviceNumber = 8

# Server_address contains teh IP address of the VNA and the port for recieving scpi commands (Standard SCPI port is 5025)
server_address = ('165.91.209.114',5025)

# The serial port locates the arduino connected to this machine
serial_port = '/dev/ttyACM0' #'COM44'

# Initialize sends commands to the VNA to prepare
def initialize():

    # CALCulate:PARameter:DELete:ALL
    # Deletes all calculations/traces from main window
    pna.send('CALC:PAR:DEL:ALL\n')
    sleep(1)

    #Add trace for S12
    pna.send('CALC:PAR \'CH1_S12_1\',S12\n')
    pna.send('DISP:WIND1:TRAC1:FEED \'CH1_S12_1\'\n')
    pna.send('DISP:WIND1:TRAC1:Y:RPOS MAX\n')
    pna.send('DISP:WIND1:TRAC1:Y:RLEV 0\n')
    pna.send('DISP:WIND1:TRAC1:Y:PDIV 10\n')
    pna.send('CALC:PAR:SEL \'CH1_S12_1\'\n')

    pna.send('CALC:FORM MLOG\n')
    pna.send('CALC:MARK ON\n')
    pna.send('CALC:MARK:X 2460 MHz\n')
    pna.send('CALC:PAR \'CH1_S12_2\',S12\n')
    pna.send('DISP:WIND2:TRAC1:FEED \'CH1_S12_2\'\n')
    pna.send('CALC:PAR:SEL \'CH1_S12_2\'\n')
    pna.send('CALC:FORM PHAS\n')
    pna.send('CALC:MARK2 ON\n')
    pna.send('CALC:MARK2:X 2460 MHz\n')

    # Turn on averaging
    pna.send('SENS:AVER ON\n')
    pna.send('SENS:AVER:MODE SWEEP\n')
    pna.send('SENS:AVER:COUN 2\n')
    sleep(1)

def setI(Vi):
    command = str(deviceNumber)+'I'+str(Vi)
    ser.write(command)

def setQ(Vq):
    command = str(deviceNumber)+'Q'+str(Vq)
    ser.write(command)

def readMarker(num):
    pna.send('SENS:AVER:CLE\n')
    sleep(3)
    command = 'CALC:PAR:SEL \'CH1_S12_'+str(num)+'\'\n'
    pna.send(command)
    command = 'CALC:MARK'+str(num)+':Y?\n'
    pna.send(command)
    result = pna.recv(100)
    result = result.split(',')
    result = float(result[0])
    return result

def minIndex(array):
    minVal = min(array)
    for i in range(len(array)):
        if array[i] == minVal:
            index = i
    return index
        

pna = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
pna.connect(server_address)
pna.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)

ser = serial.Serial(serial_port, 115200)
#####################
Vmin = 0.5
Vmax = 2.5

Vi = []
Vq = []

for i in range(41):
    v = 1.2+(i*0.01)
    Vi.append(v)
    Vq.append(v)

print('Initializing...')
initialize()

#coarse search for Vmi
mag_results = []

tempVal = 0
incCounter = 0
print('Locating Null Gain Point...')
print('Coarse Search for Vmi...')
for i in Vi:
    print('I = '+str(i)+', Q = '+str(1.3))
    setI(i)
    setQ(1.3)

    sleep(2)

    y = readMarker(1)

    mag_results.append(y)

    if y > tempVal:
        incCounter += 1
    else:
        incCounter = 0
            

    #if incCounter >= 5:
        #break

    tempVal = y


Vmi = Vi[minIndex(mag_results)]

#fine search for Vmi
Vi = []

for i in range(21):
    v = (Vmi-0.01)+(i*0.001)
    Vi.append(v)

mag_results = []

print('Fine Search for Vmi...')
for i in Vi:
    print('I = '+str(i)+', Q = '+str(1.3))
    setI(i)
    setQ(1.3)

    sleep(2)

    y = readMarker(1)

    mag_results.append(y)

Vmi = Vi[minIndex(mag_results)]

plt.figure(1)
ax1 = plt.subplot(111)
ax1.plot(Vi,mag_results)

#coarse search for Vmq
mag_results = []

print('Coarse Search for Vmq...')
tempVal = 0
incCounter = 0
for q in Vq:
    print('I = '+str(Vmi)+', Q = '+str(q))
    setQ(q)
    setI(Vmi)

    sleep(2)

    y = readMarker(1)

    mag_results.append(y)

    if y > tempVal:
        incCounter += 1
    else:
        incCounter = 0

    #if incCounter >= 5:
        #break

    tempVal = y


Vmq = Vq[minIndex(mag_results)]

#fine search for Vmq
Vq = []

for i in range(21):
    v = (Vmq-0.01)+(i*0.001)
    Vq.append(v)

mag_results = []

print('Fine Search for Vmq...')
for q in Vq:
    print('I = '+str(Vmi)+', Q = '+str(q))
    setQ(q)
    setI(Vmi)

    sleep(2)

    y = readMarker(1)

    mag_results.append(y)

Vmq = Vq[minIndex(mag_results)]

plt.figure(2)
ax2 = plt.subplot(111)
ax2.plot(Vq,mag_results)

#coarse search for Vmi
Vi = []
for i in range(41):
    v = 1.2+(i*0.01)
    Vi.append(v)
    
mag_results = []

tempVal = 0
incCounter = 0
print('Locating Null Gain Point...')
print('Coarse Search for Vmi...')
for i in Vi:
    print('I = '+str(i)+', Q = '+str(Vmq))
    setI(i)
    setQ(Vmq)

    sleep(2)

    y = readMarker(1)

    mag_results.append(y)

    if y > tempVal:
        incCounter += 1
    else:
        incCounter = 0
            

    #if incCounter >= 5:
        #break

    tempVal = y


Vmi = Vi[minIndex(mag_results)]

#fine search for Vmi
Vi = []

for i in range(21):
    v = (Vmi-0.01)+(i*0.001)
    Vi.append(v)

mag_results = []

print('Fine Search for Vmi...')
for i in Vi:
    print('I = '+str(i)+', Q = '+str(Vmq))
    setI(i)
    setQ(Vmq)

    sleep(2)

    y = readMarker(1)

    mag_results.append(y)

Vmi = Vi[minIndex(mag_results)]

plt.figure(3)
ax3 = plt.subplot(111)
ax3.plot(Vi,mag_results)

Gnull = min(mag_results)

Vrange = 2*min(Vmi-Vmin,Vmq-Vmin,Vmax-Vmi,Vmax-Vmq)

setI(Vmi)
setQ(Vmq)

print('\nVmi = '+str(Vmi)+'V')
print('Vmq = '+str(Vmq)+'V')
print('Vrange = '+str(Vrange)+'V')
print('Gnull = '+str(Gnull)+'dB\n')

Imin = Vmi-(Vrange/2)
Imax = Vmi+(Vrange/2)
Qmin = Vmq-(Vrange/2)
Qmax = Vmq+(Vrange/2)
Vi = [Imin,Vmi-(Vrange/2)*np.cos(45*(pi/180)),Vmi,Vmi+(Vrange/2)*np.cos(45*(pi/180)),Imax]
Vq = [Qmin,Vmq-(Vrange/2)*np.cos(45*(pi/180)),Vmq,Vmq+(Vrange/2)*np.cos(45*(pi/180)),Qmax]

Vi = np.round(Vi, 3)
Vq = np.round(Vq, 3)

print('Vi = ')
print(Vi)
print('Vq = ')
print(Vq)

print('\nFinding Max Gain Average...')

Gain = np.zeros((5,5))
Phase = np.zeros((5,5))
calcPhase = np.zeros((5,5))

for i in range(len(Vi)):
    for q in range(len(Vq)):
        print('I = '+str(Vi[i])+', Q = '+str(Vq[q]))
        setI(Vi[i])
        sleep(2)
        setQ(Vq[q])
        sleep(2)
        Gain[q,i] = readMarker(1)
        Phase[q,i] = readMarker(2)
        calcPhase[q,i] = np.arctan2((Vq[q]-Vmq),(Vi[i]-Vmi))*180/pi

phaseOffsets = Phase - calcPhase
phaseOffsetsSum = np.sum(phaseOffsets) - phaseOffsets[2,2]
phaseOffset = phaseOffsetsSum/(phaseOffsets.size - 1)

print(Gain)
print(Phase)

maxGain = np.average([Gain[0,2],Gain[1,3],Gain[2,4],Gain[3,3],Gain[4,2],Gain[3,1],Gain[2,0],Gain[1,1]])

print('\nVmi = '+str(Vmi)+'V')
print('Vmq = '+str(Vmq)+'V')
print('Vrange = '+str(Vrange)+'V')
print('Gnull = '+str(Gnull)+'dB\n')

print('\nGmax = '+str(maxGain)+'dB, '+str(pow(10,maxGain/20)))
print('Phase Offset = '+str(phaseOffset))
#####################
ser.close()
pna.close()

endTime = time()

totalTime = endTime-startTime

minutes = int(totalTime/60)

seconds = int(np.round(totalTime - (minutes*60)))

print('\nCalibration Completed in '+str(minutes)+' min '+str(seconds)+' sec')

f = open('../../CalibrationResults/Cube/Calibration_'+str(deviceNumber)+'.txt','w')

f.write('Vmi = '+str(Vmi)+'V\n')
f.write('Vmq = '+str(Vmq)+'V\n')
f.write('Gmax = '+str(maxGain)+'dB, '+str(pow(10,maxGain/20))+'\n')
f.write('Phase Offset = '+str(phaseOffset)+'\n\n')

f.write('Vrange = '+str(Vrange)+'V\n')
f.write('Gnull = '+str(Gnull)+'dB, '+str(pow(10,Gnull/20))+'\n\n')

f.write('copy for arduino code:\n')
f.write('const double Gmax = '+str(np.round(pow(10,maxGain/20),5))+';\n')
f.write('const double Gnull = '+str(np.round(pow(10,Gnull/20),5))+';\n')
f.write('const float phase_offset = '+str(phaseOffset)+';\n')
f.write('const float Vmi = '+str(Vmi)+';\n')
f.write('const float Vmq = '+str(Vmq)+';\n')
f.write('const float Vr = '+str(Vrange)+';')

f.close()

plt.show()
