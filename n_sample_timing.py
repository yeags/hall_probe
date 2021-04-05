import nidaqmx as ni
import numpy as np
from time import sleep, perf_counter
import numpy as np

RATE = 50000
SAMPS = 100

hallsensor = ni.Task()
relay = ni.Task()
trigger = ni.Task()
select = ni.Task()

relay.ao_channels.add_ao_voltage_chan('AnalogOut/ao0')
trigger.ao_channels.add_ao_voltage_chan('AnalogOut/ao3')
select.ao_channels.add_ao_voltage_chan('AnalogOut/ao1:2')

hallsensor.ai_channels.add_ai_voltage_chan('FieldSensor/ai0:3')
hallsensor.timing.cfg_samp_clk_timing(RATE, sample_mode=ni.constants.AcquisitionType.CONTINUOUS,
                                      samps_per_chan=SAMPS)
hallsensor.in_stream.input_buf_size = SAMPS
hallsensor.in_stream.over_write = ni.constants.OverwriteMode.OVERWRITE_UNREAD_SAMPLES

data = np.zeros((4,SAMPS))

hs_stream = ni.stream_readers.AnalogMultiChannelReader(hallsensor.in_stream)


def pulse():
    trigger.write(5)
    sleep(0.005)
    trigger.write(0)

relay.write(1.3)
select.write([5,0])

start = perf_counter()
hallsensor.start()
input('Press ENTER to read')
ni.stream_readers.AnalogMultiChannelReader.read_many_sample(data, SAMPS)
# hallsensor.stop()
print(data.shape)
np.savetxt('samp.txt', data, fmt='%.6f')
relay.write(0)
select.write([0,0])
