import nidaqmx as ni
from time import sleep

class DAQ(ni.task.Task):
    '''
    Creates an NI Task
    Takes input parameters from Hall Probe GUI
    '''
    def __init__(self, task_name: str):
        self.task_name = task_name
        super().__init__(new_task_name=task_name)
    
    def add_voltage_channels(self, v_channels: list, v_min: float, v_max: float, units):
        for channel in range(len(v_channels)):
            if v_channels[channel]:
                self.ai_channels.add_ai_voltage_chan(f'FieldSensor/ai{channel}',
                                                     min_val=v_min,
                                                     max_val=v_max,
                                                     units=units)

    def add_temperature_channels(self, temp_channels: list, type, units):
        for channel in range(len(temp_channels)):
            if temp_channels[channel]:
                self.ai_channels.add_ai_thrmcpl_chan(f'MagnetTemp/ai{channel}',
                                                     thermocouple_type=Constants.therm_types()[type], 
                                                     units=Constants.temp_units()[units])
        self.ai_channels.all.ai_adc_timing_mode = ni.constants.ADCTimingMode.HIGH_SPEED
        self.timing.samp_timing_type = ni.constants.SampleTimingType.ON_DEMAND

    def set_sampling(self, sample_rate: int, num_samples: int):
        self.timing.cfg_samp_clk_timing(sample_rate,
                                        sample_mode=ni.constants.AcquisitionType.CONTINUOUS,
                                        samps_per_chan=num_samples)
    def __repr__(self):
        return f'NI cDAQ Task: {self.task_name}'

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
    @staticmethod
    def continuous():
        return ni.constants.AcquisitionType.CONTINUOUS

if __name__ == '__main__':
    print('Creating DAQmx Object...')
    cdaq = DAQ('new task')
    print(cdaq, 'Sleeping...')
    sleep(5)
    print('Closing DAQmx Object...')
    cdaq.close()