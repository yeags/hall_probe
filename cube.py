from nicdaq import HallDAQ
from calibration import get_xyz_calib_values, calib_data
import zeisscmm
import numpy as np

class Cube:
    def __init__(self, cube_filename: str, probe_calibration_path: str, probe_offset_filename: str):
        self.daq = HallDAQ(1, 1000, start_trigger=True, acquisition='finite')
        self.daq.power_on()
        self.cmm = zeisscmm.CMM()
        self.calib_coeffs = get_xyz_calib_values(probe_calibration_path)
        self.rotation, self.translation = self.import_cube_alignment(cube_filename)
        self.probe_offset = self.import_probe_offset(probe_offset_filename)
    
    def import_cube_alignment(self, filename: str):
        diff = np.genfromtxt(filename, delimiter=' ')
        rotation = diff[:-3].reshape((3,3))
        translation = diff[-3:]
        return (rotation, translation)
    
    def import_probe_offset(self, filename: str):
        offset = np.genfromtxt(filename, delimiter=' ')
        return offset

    def measure_cube_center(self):
        pass

    def cube2mcs(self, coordinate):
        return (coordinate - self.translation)@self.rotation

    def mcs2cube(self, coordinate):
        return coordinate@np.linalg.inv(self.rotation) + self.translation

if __name__ == '__main__':
    test = Cube()