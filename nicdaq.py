import nidaqmx as ni
from time import sleep

class DAQTask(ni.task.Task):
    '''
    Creates an NI Task
    Takes input parameters from Hall Probe GUI
    '''
    def __init__(self, task_name: str):
        self.task_name = task_name
        super().__init__(new_task_name=task_name)
    
    def add_voltage_channels(self, v_channels: list, aiv_min: float, aiv_max: float, units):
        for channel in range(len(v_channels)):
            if v_channels[channel]:
                self.ai_channels.add_ai_voltage_chan(f'FieldSensor/ai{channel}',
                                                     min_val=aiv_min,
                                                     max_val=aiv_max,
                                                     units=units)
    
    def add_analog_out_channels(self, ao_channels: list, aov_min: float, aov_max: float):
        for channel in range(len(ao_channels)):
            if ao_channels[channel]:
                self.ao_channels.add_ao_voltage_chan(f'AnalogOut/ao{channel}',
                                                     min_val=aov_min,
                                                     max_val=aov_max)

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

class HallDAQ:
    POWER_ON = 1.3
    POWER_OFF = 0.0
    FSV_OFF = 0.0
    FSV_PLUS = 5.0
    FSV_MINUS = -5.0
    RANGE_2T = [5.0, 0.0]
    RANGE_100MT = [0.0, 0.0]
    RANGE_OFF = [0.0, 0.0] # Same as RANGE_100MT.  Simply used for turning off analog output voltage
    def __init__(self):
        self.__create_tasks__()
        self.__configure_tasks__()
    
    def __create_tasks__(self):
        self.cdaq_hallprobe = DAQTask('HallProbe')
        self.cdaq_magnet_temp = DAQTask('MagnetTemp')
        self.cdaq_power_relay = DAQTask('PowerRelay')
        self.cdaq_fsv = DAQTask('FSV')
        self.cdaq_hall_sensitivity = DAQTask('HallSensitivity')
    
    def __configure_tasks__(self):
        self.cdaq_hallprobe.ai_channels.add_ai_voltage_chan('FieldSensor/ai0:3')
        self.cdaq_hallprobe.timing.cfg_samp_clk_timing(1000, sample_mode=ni.constants.AcquisitionType.CONTINUOUS, samps_per_chan=100)
        self.cdaq_power_relay.ao_channels.add_ao_voltage_chan('AnalogOut/ao0')
        self.cdaq_fsv.ao_channels.add_ao_voltage_chan('AnalogOut/ao3')
        self.cdaq_hall_sensitivity.ao_channels.add_ao_voltage_chan('AnalogOut/ao1:2')
        # add magnet temp configuration when known and not using gui for input selection
    
    def read_hall_sensor(self):
        while self.cdaq_hallprobe._in_stream.avail_samp_per_chan < 100:
            pass
        sample = self.cdaq_hallprobe.read(self.cdaq_hallprobe._in_stream.avail_samp_per_chan)
        return sample
        
    def read_magnet_temp(self):
        pass

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
    cdaq = DAQTask('new task')
    print(cdaq, 'Sleeping...')
    sleep(5)
    print('Closing DAQmx Object...')
    cdaq.close()