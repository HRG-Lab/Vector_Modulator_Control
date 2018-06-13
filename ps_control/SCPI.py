import socket
import warnings
# import numpy as np
from time import sleep
from time import time


# These commands have only been checked with Rohde Schwarz Equipment
class SCPI:
    def __init__(self, address):
        print("Connecting to ", address[0])
        self.ADDRESS = address
        # Initialize socket object
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect(address)
        self.sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)

        self.reset()

    # The Reset function ensures the SignalGenerator Always starts in a defined state
    def reset(self):
        # Set all instrument settingsto default
        self.send('*RST')


        # This command for specific instruments (R&S vsg)

        # # Clear status registers
        # # Also clears error queue and output buffer
        # self.send('CLS')

    # Queries instrument name and manufacturer
    def identify(self):
        self.send('*IDN?')
        ID = self.receive(100)
        return ID[0] + ' ' + ID[1]

    # Send and receive functions are implemented to avoid having to deal with endcoding
    # decoding, and parsing byte strings each time a command is sent
    def send(self, command):
        command = command + '\n'
        self.sock.send(command.encode())

    def receive(self, max_bits):
        received_string = self.sock.recv(max_bits).decode('utf-8')
        received_string = received_string.rstrip('\n')
        values = received_string.split(',')

        return values

    # OPC() confirms that a command is completed
    # Used to ensure that commands are executed in the order
    # They're sent
    def OPC(self):
        self.send('*OPC?')
        status = self.receive(100)
        return int(status[0])

    # Close function properly closes socket connection. Subclasses may implement more calls
    def close(self):
        self.sock.shutdown(socket.SHUT_RDWR)
        self.sock.close()