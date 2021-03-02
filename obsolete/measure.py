import socket
from time import sleep
import nidaqmx as ni

# Create socket connection to CMM
cmm = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
cmm.connect(('192.4.1.200', 4712))

# Create CMM command function

def send_cmd(command, recv_response=True):
    if recv_response:
        cmm.send((command+'\r\n\x01').encode('ascii'))
        data = cmm.recv(1024).decode('ascii')
        return data
    else:
        cmm.send((command+'\r\n').encode('ascii'))

# Create DAQ Task Object
daq = ni.Task()

# Add temperature sensors
daq.ai_channels.add_ai_thrmcpl_chan('MagnetTemp/ai0:1', thermocouple_type=ni.constants.ThermocoupleType.K)

# Add field sensors
daq.ai_channels.add_ai_voltage_chan('FieldSensor/ai0:2')

# Configure timing
daq.timing.cfg_samp_clk_timing(1000, sample_mode=ni.constants.AcquisitionType.CONTINUOUS, samps_per_chan=2)

position = []
sensors = []
data = []
i = 0

while i < 1000:
    position.append(send_cmd('D84'))
    sensors.append(daq.read())
    i += 1
    sleep(0.1)

with open('measurement_data.txt', 'w') as sf:
    sf.write('{},{}'.format(position, sensors))

cmm.close()
daq.close()