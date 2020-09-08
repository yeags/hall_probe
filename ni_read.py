import nidaqmx as ni
import time
import numpy as np

samples=200

def sleep(duration, get_now=time.perf_counter):
    now = get_now()
    end = now + duration
    while now < end:
        now = get_now()

# Create DAQ Task Object
daq = ni.Task(new_task_name='hallsensor')

# Add temperature sensors
daq.ai_channels.add_ai_thrmcpl_chan('MagnetTemp/ai0:1',
                                    thermocouple_type=ni.constants.ThermocoupleType.K)

# Add field sensors
daq.ai_channels.add_ai_voltage_chan('FieldSensor/ai0:2')

# Configure timing
daq.timing.cfg_samp_clk_timing(10, sample_mode=ni.constants.AcquisitionType.CONTINUOUS)

# print(f'buffer size per chan: {daq.in_stream.input_buf_size}')
# read_interval = []

d = open('data.txt', 'w')
# daq.in_stream.input_buf_size = 1000
print(f'input buffer size: {daq.in_stream.input_buf_size}')
daq.in_stream.over_write = ni.constants.OverwriteMode.OVERWRITE_UNREAD_SAMPLES
ni.constants.DataTransferActiveTransferMode(10264)

i=0
daq.start()
start = time.perf_counter()
while i < samples:
    d.write(f'{i};{daq.read(ni.constants.READ_ALL_AVAILABLE)}\n')
    sleep(0.1)
    # d.write(f'{i};{daq.read(10)}\n')
    i += 1
end = time.perf_counter()
daq.stop()
d.close()
daq.close()
print(f'elapsed time: {(end-start):.3f}s')