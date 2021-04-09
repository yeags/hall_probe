import nidaqmx as ni
import numpy as np
from time import sleep

class HallDAQ:
    POWER_ON = 1.3
    POWER_OFF = 0.0
    FSV_OFF = 0.0
    FSV_PLUS = 5.0
    FSV_MINUS = -5.0
    SENSOR_RANGE = {'2T': 5,
                    '100MT': 0,
                    'OFF': 0}
    
    def __init__(self, rate, samps_per_chan, start_trigger=False, acquisition='finite'):
        if acquisition.lower() == 'continuous':
            self.acquisition_type = ni.constants.AcquisitionType.CONTINUOUS
        elif acquisition.lower() == 'finite':
            self.acquisition_type = ni.constants.AcquisitionType.FINITE
        self.trigger_status = start_trigger
        self.power_status = False
        self.fsv_status = False
        self.sensitivity_status = False
        self.hs_task_status = False
        self.mag_temp_task_status = False
        self.RATE = rate
        self.SAMPLES_CHAN = samps_per_chan

        self.__create_tasks__()
        self.__configure_tasks__()
    
    def __create_tasks__(self):
        self.hallsensor = ni.Task('HallSensor')
        self.magnet_temp = ni.Task('MagnetTemp')
        self.power_relay = ni.Task('PowerRelay')
        self.fsv = ni.Task('FSV')
        self.hall_sensitivity = ni.Task('HallSensitivity')
        self.trigger = ni.Task('StartTrigger')
    
    def __configure_tasks__(self):
        self.hallsensor.ai_channels.add_ai_voltage_chan('FieldSensor/ai0:3')
        self.hallsensor.timing.cfg_samp_clk_timing(self.RATE, sample_mode=self.acquisition_type,
                                                   samps_per_chan=self.SAMPLES_CHAN)
        self.power_relay.ao_channels.add_ao_voltage_chan('AnalogOut/ao0')
        # self.fsv.ao_channels.add_ao_voltage_chan('AnalogOut/ao3')
        if self.trigger_status:
            self.trigger.ao_channels.add_ao_voltage_chan('AnalogOut/ao2')
            self.hallsensor.triggers.start_trigger.cfg_dig_edge_start_trig('/MagnetcDAQ/PFI0')
        self.fsv.ao_channels.add_ao_voltage_chan('AnalogOut/ao3')
        self.hall_sensitivity.ao_channels.add_ao_voltage_chan('AnalogOut/ao1')
        self.magnet_temp.ai_channels.add_ai_thrmcpl_chan('MagnetTemp/ai0:7',
                                                         units=ni.constants.TemperatureUnits.DEG_C,
                                                         thermocouple_type=ni.constants.ThermocoupleType.K)
        self.magnet_temp.timing.cfg_samp_clk_timing(self.RATE, sample_mode=ni.constants.AcquisitionType.CONTINUOUS,
                                                    samps_per_chan=self.SAMPLES_CHAN)
    
    def change_sensitivity(self, sensitivity=None):
        if sensitivity is not None:
            self.hall_sensitivity.write(self.SENSOR_RANGE[sensitivity.upper().replace(' ', '')])
        else:
            pass
    
    def close_tasks(self):
        self.hallsensor.close()
        self.fsv.close()
        self.magnet_temp.close()
        self.power_relay.close()
        self.hall_sensitivity.close()
        self.trigger.close()

    def fsv_on(self, v='positive'):
        if v == 'positive'.lower():
            self.fsv.write(5)
        elif v == 'negative'.lower():
            self.fsv.write(-5)
    
    def fsv_off(self):
        self.fsv.write(0)

    def power_on(self, sensitivity='2T'):
        '''
        2T range will always be used
        '''
        if self.power_status:
            pass
        else:
            self.power_relay.write(self.POWER_ON)
            self.hall_sensitivity.write(self.SENSOR_RANGE['2T'])
            self.power_status = True

    def power_off(self):
        if self.power_status:
            self.hall_sensitivity.write(self.SENSOR_RANGE['OFF'])
            self.power_relay.write(self.POWER_OFF)
            self.power_status = False
        else:
            pass
    
    def pulse(self):
        self.trigger.write(5)
        sleep(0.005)
        self.trigger.write(0)

    def read_hallsensor(self):
        while not self.hallsensor.is_task_done():
            pass
        sample = np.array(self.hallsensor.read(self.hallsensor._in_stream.avail_samp_per_chan)).T
        return sample
        
    def read_magnet_temp(self):
        while self.magnet_temp._in_stream.avail_samp_per_chan < self.SAMPLES_CHAN:
            pass
        sample = np.array(self.magnet_temp.read(self.magnet_temp._in_stream.avail_samp_per_chan)).T
        return sample

    def start_hallsensor_task(self):
        if self.hs_task_status:
            pass
        else:
            self.hallsensor.start()
            self.hs_task_status = True

    def stop_hallsensor_task(self):
        if self.hs_task_status:
            self.hallsensor.stop()
            self.hs_task_status = False
        else:
            pass

    def start_magnet_temp_task(self):
        if self.mag_temp_task_status:
            pass
        else:
            self.magnet_temp.start()
            self.mag_temp_task_status = True

    def stop_magnet_temp_task(self):
        if self.mag_temp_task_status:
            self.magnet_temp.stop()
            self.mag_temp_task_status = False
        else:
            pass
        
if __name__ == '__main__':
    from time import perf_counter
    daq = HallDAQ(1,5000, acquisition='finite')
    print('Powering on daq...')
    daq.power_on()
    print('Powered on.  Set to 2 T range.')
    print('Starting task...')
    daq.start_hallsensor_task()
    # sleep(3)
    # print('Sending trigger pulse.')
    # daq.pulse()
    print('Turning on FSV')
    daq.fsv_on()
    print('Reading from hall sensor...')
    start = perf_counter()
    data = daq.read_hallsensor()
    end = perf_counter()
    print('Turning off FSV')
    daq.fsv_off()
    print(f'Read {data.shape[0]} samples in {end - start} seconds')
    print('Saving data as "sample_data.txt"')
    # np.savetxt('sample_data.txt', data, fmt='%.6f')
    # print(data)
    print(f' Array shape: {data.shape}')
    print('Stopping task')
    daq.stop_hallsensor_task()
    print('Power off')
    daq.power_off()
    print('Closing task')
    daq.close_tasks()