import nidaqmx as ni
import numpy as np

class HallDAQ:
    POWER_ON = 1.3
    POWER_OFF = 0.0
    FSV_OFF = 0.0
    FSV_PLUS = 5.0
    FSV_MINUS = -5.0
    RANGE_2T = [5.0, 0.0]
    RANGE_100MT = [0.0, 0.0]
    RANGE_OFF = [0.0, 0.0] # Same as RANGE_100MT.  Simply used for turning off analog output voltage
    RATE = 1000
    SAMPLES_CHAN = 100
    def __init__(self):
        self.power_status = False
        self.fsv_status = False
        self.sensitivity_status = False

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
        self.hallsensor.timing.cfg_samp_clk_timing(self.RATE, sample_mode=ni.constants.AcquisitionType.CONTINUOUS, samps_per_chan=self.SAMPLES_CHAN)
        self.power_relay.ao_channels.add_ao_voltage_chan('AnalogOut/ao0')
        self.fsv.ao_channels.add_ao_voltage_chan('AnalogOut/ao3')
        self.hall_sensitivity.ao_channels.add_ao_voltage_chan('AnalogOut/ao1:2')
        # add magnet temp configuration when known and not using gui for input selection
    
    def power_on(self, sensitivity=RANGE_2T):
        if self.power_status:
            pass
        else:
            self.power_relay.write(self.POWER_ON)
            self.hall_sensitivity.write(sensitivity)
            self.power_status = True

    def power_off(self):
        if self.power_status:
            self.hall_sensitivity.write(self.RANGE_OFF)
            self.power_relay.write(self.POWER_OFF)
            self.power_status = False
        else:
            pass
    
    def change_sensitivity(self, sensitivity=None):
        if sensitivity is not None:
            self.hall_sensitivity.write(sensitivity)
        else:
            pass

    def start_hallsensor_task(self):
        self.hallsensor.start()
    
    def stop_hallsensor_task(self):
        self.hallsensor.stop()

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
        pass

    def close_tasks(self):
        self.hallsensor.close()
        self.fsv.close()
        self.magnet_temp.close()
        self.power_relay.close()
        self.hall_sensitivity.close()

if __name__ == '__main__':
    pass