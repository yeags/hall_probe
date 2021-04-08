import numpy as np
import zeisscmm
from nicdaq import HallDAQ

def import_fsv_alignment(filename: str):
    diff = np.genfromtxt(filename, delimiter=' ')
    rotation = diff[:-3].reshape((3,3))
    translation = diff[-3:]
    return (rotation, translation)

def fsv2mcs(coordinate: np.ndarray, rotation: np.ndarray, translation: np.ndarray):
    return (coordinate - translation)@rotation

def mcs2fsv(coordinate: np.ndarray, rotation: np.ndarray, translation: np.ndarray):
    return coordinate@np.linalg.inv(rotation) + translation

def x_routine(cmm_obj: zeisscmm.CMM, hall_obj: HallDAQ):
    current_pos = cmm_obj.get_position()

def y_routine(cmm_obj: zeisscmm.CMM, hall_obj: HallDAQ):
    current_pos = cmm_obj.get_position()

def z_routine(cmm_obj: zeisscmm.CMM, hall_obj: HallDAQ):
    current_pos = cmm_obj.get_position()

def save_probe_offset():
    pass