import socket
import serial
import numpy as np
import matplotlib.pyplot as plt
from time import sleep
from time import time

startTime = time()

deviceNumber = 13
server_address = ('165.91.209.114',5025)
serial_port = '/dev/ttyACM0'
pi = np.pi

def initialize():
    pna.send('CALC:PAR:DEL:ALL\n')
    sleep(1)
    pna.send('CALC:PAR \'CH1_S12_1\',S12\n')
    pna.send('DISP:WIND1:TRAC1:FEED \'CH1_S12_1\'\n')
    pna.send('DISP:WIND1:TRAC1:Y:RPOS MAX\n')
    pna.send('DISP:WIND1:TRAC1:Y:RLEV 0\n')
    pna.send('DISP:WIND1:TRAC1:Y:PDIV 10\n')
    pna.send('CALC:PAR:SEL \'CH1_S12_1\'\n')
    pna.send('CALC:FORM MLOG\n')
    pna.send('CALC:MARK ON\n')
    pna.send('CALC:MARK:X 2400 MHz\n')
    pna.send('CALC:PAR \'CH1_S12_2\',S12\n')
    pna.send('DISP:WIND2:TRAC1:FEED \'CH1_S12_2\'\n')
    pna.send('CALC:PAR:SEL \'CH1_S12_2\'\n')
    pna.send('CALC:FORM PHAS\n')
    pna.send('CALC:MARK2 ON\n')
    pna.send('CALC:MARK2:X 2400 MHz\n')
    pna.send('SENS:AVER ON\n')
    pna.send('SENS:AVER:MODE SWEEP\n')
    pna.send('SENS:AVER:COUN 2\n')
    sleep(1)
    return

def setI(Vi):
    command = str(deviceNumber)+'I'+str(Vi)
    ser.write(command)
    sleep(1)
    return

def setQ(Vq):
    command = str(deviceNumber)+'Q'+str(Vq)
    ser.write(command)
    sleep(1)
    return

def readMarker(num):
    pna.send('SENS:AVER:CLE\n')
    sleep(0.5)
    command = 'CALC:PAR:SEL \'CH1_S12_'+str(num)+'\'\n'
    pna.send(command)
    sleep(0.5)
    command = 'CALC:MARK'+str(num)+':Y?\n'
    pna.send(command)
    sleep(1)
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

for i in range(31):
    v = 1.3+(i*0.01)
    Vi.append(v)
    Vq.append(v)

print('Start Initialization Process')
print('\nDevice: #' + str(deviceNumber))
initialize()

# Search for Vmi
mag_results = []

print('Search for Vmi...')

for i in Vi:
    print('I = '+str(i)+', Q = '+str(1.45))
    setI(i)
    setQ(1.45)
    y = readMarker(1)
    mag_results.append(y)

Vmi = Vi[minIndex(mag_results)]



plt.figure(1)
ax1 = plt.subplot(211)
ax1.plot(Vi,mag_results)
plt.title('Search Vmi - Top / Vmq - Bottom')
plt.xlabel('I Voltage')
plt.ylabel('S12 Amplitude - dB')











# Search for Vmq
mag_results = []

print('Search for Vmq...')

for q in Vq:
    print('I = '+str(Vmi)+', Q = '+str(q))
    setQ(q)
    setI(Vmi)

    y = readMarker(1)

    mag_results.append(y)

Vmq = Vq[minIndex(mag_results)]

plt.figure(1)
ax1 = plt.subplot(212)
ax1.plot(Vq,mag_results)
plt.xlabel('Q Voltage')
plt.ylabel('S12 Amplitude - dB')







Gnull = min(mag_results)

Gnull =  np.round(Gnull, 3)

Vrange = 2*min(Vmi-Vmin,Vmq-Vmin,Vmax-Vmi,Vmax-Vmq)


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
        setQ(Vq[q])
        Gain[q,i] = readMarker(1)
        Phase[q,i] = readMarker(2)
        calcPhase[q,i] = np.arctan2((Vq[q]-Vmq),(Vi[i]-Vmi))*180/pi

phaseOffsets = Phase - calcPhase
phaseOffsetsSum = np.sum(phaseOffsets) - phaseOffsets[2,2]
phaseOffset = phaseOffsetsSum/(phaseOffsets.size - 1)
Gain = np.round(Gain, 3)
Phase = np.round(Phase, 3)

print('Gain = ')
print(Gain)
print('Phase = ')
print(Phase)

maxGain = np.average([Gain[0,2],Gain[1,3],Gain[2,4],Gain[3,3],Gain[4,2],Gain[3,1],Gain[2,0],Gain[1,1]])

print('\nVmi = '+str(Vmi)+'V')
print('Vmq = '+str(Vmq)+'V')
print('Vrange = '+str(Vrange)+'V')
print('Gnull = '+str(Gnull)+'dB\n')

print('Gmax = '+str(maxGain)+'dB, '+str(pow(10,maxGain/20)))
print('Phase Offset = '+str(phaseOffset))

setI(Vmi)
setQ(Vmq)

#####################
ser.close()
pna.close()

endTime = time()

totalTime = endTime-startTime

minutes = int(totalTime/60)

seconds = int(np.round(totalTime - (minutes*60)))

print('\nCalibration Completed in '+str(minutes)+' min '+str(seconds)+' sec')

f = open('../../CalibrationResults/Cube/5_11_2016/Calibration_'+str(deviceNumber)+'.txt','w')

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


