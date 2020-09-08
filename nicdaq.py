import nidaqmx as ni
from time import sleep

class DAQ(ni.task.Task):
    '''
    Creates an NI Task with pre-configured parameters.
    '''
    def __init__(self):
        super().__init__(new_task_name='NI cDAQ')
        self.ai_channels.add_ai_thrmcpl_chan('MagnetTemp/ai0:1', thermocouple_type=ni.constants.ThermocoupleType.K)
        self.ai_channels.add_ai_voltage_chan('FieldSensor/ai0:2')
        self.timing.cfg_samp_clk_timing(1000, sample_mode=ni.constants.AcquisitionType.CONTINUOUS, samps_per_chan=2)
    
    def __repr__(self):
        return 'NI cDAQ Task'
    
if __name__ == '__main__':
    print('Creating DAQmx Object...')
    cdaq = DAQ()
    print('Sleeping...')
    sleep(5)
    print('Closing DAQmx Object...')
    cdaq.close()