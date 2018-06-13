import ps_control.network_analyzer as network_analyzer
import serial

pna_address = ('165.91.209.114',5025)
serial_port = '/dev/ttyACM0'
baud_rate = 115200

freq = 2400
freq_units = 'MHz'
avg_count = 2

# Initialize Network Analyzer
pna = network_analyzer.network_analyzer(pna_address) # Create pna object

# The following commands replace the initialize() function from the old calibration code:
# Prepare the vna to read the phases from the markers
pna.clear_calcs()
pna.marker_on(1,freq,freq_units)
pna.marker_on(2,freq,freq_units)
pna.averaging_on('SWEEP',avg_count)

# Initialize Serial Connection to Arduino
ser_connection = serial.Serial(serial_port,baud_rate)


# After initialization, loop through different voltages to read phases

# Set I voltage

# Read marker phase value