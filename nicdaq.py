import nidaqmx as ni
import numpy as np

class HallDAQ:
    POWER_ON = 1.3
    POWER_OFF = 0.0
    FSV_OFF = 0.0
    FSV_PLUS = 5.0
    FSV_MINUS = -5.0
    SENSOR_RANGE = {'2T': [5.0, 0.0],
                    '100MT': [0.0, 0.0],
                    'OFF': [0.0, 0.0]}
    RATE = 1000
    SAMPLES_CHAN = 100
    def __init__(self):
        self.power_status = False
        self.fsv_status = False
        self.sensitivity_status = False
        self.hs_task_status = False
        self.mag_temp_task_status = False

        self.__create_tasks__()
        self.__configure_tasks__()
    
    def __create_tasks__(self):
        self.hallsensor = ni.Task('HallSensor')
        self.magnet_temp = ni.Task('MagnetTemp')
        self.power_relay = ni.Task('PowerRelay')
        self.fsv = ni.Task('FSV')
        self.hall_sensitivity = ni.Task('HallSensitivity')
    
    def __configure_tasks__(self):
        self.hallsensor.ai_channels.add_ai_voltage_chan('FieldSensor/ai0:3')
        self.hallsensor.timing.cfg_samp_clk_timing(self.RATE, sample_mode=ni.constants.AcquisitionType.CONTINUOUS,
                                                   samps_per_chan=self.SAMPLES_CHAN)
        self.power_relay.ao_channels.add_ao_voltage_chan('AnalogOut/ao0')
        self.fsv.ao_channels.add_ao_voltage_chan('AnalogOut/ao3')
        self.hall_sensitivity.ao_channels.add_ao_voltage_chan('AnalogOut/ao1:2')
        self.magnet_temp.ai_channels.add_ai_thrmcpl_chan('MagnetTemp/ai0:7',
                                                         units=ni.constants.TemperatureUnits.DEG_C,
                                                         thermocouple_type=ni.constants.ThermocoupleType.K)
        self.magnet_temp.timing.cfg_samp_clk_timing(self.RATE, sample_mode=ni.constants.AcquisitionType.CONTINUOUS,
                                                    samps_per_chan=self.SAMPLES_CHAN)
    
    def power_on(self, sensitivity='2T'):
        if self.power_status:
            pass
        else:
            self.power_relay.write(self.POWER_ON)
            self.hall_sensitivity.write(self.SENSOR_RANGE[sensitivity.upper().replace(' ', '')])
            self.power_status = True

    def power_off(self):
        if self.power_status:
            self.hall_sensitivity.write(self.SENSOR_RANGE['OFF'])
            self.power_relay.write(self.POWER_OFF)
            self.power_status = False
        else:
            pass
    
    def change_sensitivity(self, sensitivity=None):
        if sensitivity is not None:
            self.hall_sensitivity.write(self.SENSOR_RANGE[sensitivity.upper().replace(' ', '')])
        else:
            pass

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

    def fsv_on(self):
        # uncomment write command when fsv tool is fixed
        # self.fsv.write(5)
        pass
    def fsv_off(self):
        # uncomment write command when fsv tool is fixed
        # self.fsv.write(0)
        pass

    def read_hallsensor(self):
        while self.hallsensor._in_stream.avail_samp_per_chan < self.SAMPLES_CHAN:
            pass
        sample = np.array(self.hallsensor.read(self.hallsensor._in_stream.avail_samp_per_chan)).T
        return sample
        
    def read_magnet_temp(self):
        while self.magnet_temp._in_stream.avail_samp_per_chan < self.SAMPLES_CHAN:
            pass
        sample = np.array(self.magnet_temp.read(self.magnet_temp._in_stream.avail_samp_per_chan)).T
        return sample

    def close_tasks(self):
        self.hallsensor.close()
        self.fsv.close()
        self.magnet_temp.close()
        self.power_relay.close()
        self.hall_sensitivity.close()

if __name__ == '__main__':
    from time import sleep
    daq = HallDAQ()
    print('Powering on daq...')
    daq.power_on()
    print('Powered on.  Set to 2 T range.')
    print('Starting task...')
    daq.start_hallsensor_task()
    sleep(0.05)
    print('Reading from hall sensor...')
    data = daq.read_hallsensor()
    print(data)
    print(f' Array shape: {data.shape}')
    print('Stopping task')
    daq.stop_hallsensor_task()
    print('Power off')
    daq.power_off()
    print('Closing task')
    daq.close_tasks()
