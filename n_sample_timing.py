import nidaqmx as ni
import numpy as np
from time import sleep

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
hallsensor.timing.cfg_samp_clk_timing(RATE, sample_mode=ni.constants.AcquisitionType.FINITE, samps_per_chan=SAMPS)

def pulse(state='high'):
    if state == 'high':
        trigger.write(5)
        # sleep(0.05)
        # trigger.write(0)
    else:
        trigger.write(0)
        # sleep(0.05)
        # trigger.write(5)

