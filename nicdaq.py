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

class Constants:
    @staticmethod
    def therm_types():
        return {'B': ni.constants.ThermocoupleType.B, 'E': ni.constants.ThermocoupleType.E,
                'J': ni.constants.ThermocoupleType.J, 'K': ni.constants.ThermocoupleType.K,
                'N': ni.constants.ThermocoupleType.N, 'R': ni.constants.ThermocoupleType.R,
                'S': ni.constants.ThermocoupleType.S, 'T': ni.constants.ThermocoupleType.T}
    @staticmethod
    def temp_units():
        return {'C': ni.constants.TemperatureUnits.DEG_C,
                'F': ni.constants.TemperatureUnits.DEG_F,
                'K': ni.constants.TemperatureUnits.K}
    @staticmethod
    def voltage_units():
        return {'V': ni.constants.VoltageUnits.VOLTS,
                'mT': ni.constants.VoltageUnits.FROM_CUSTOM_SCALE}

if __name__ == '__main__':
    print('Creating DAQmx Object...')
    cdaq = DAQ()
    print('Sleeping...')
    sleep(5)
    print('Closing DAQmx Object...')
    cdaq.close()