import numpy as np
from zeisscmm import CMM

cmm = CMM()
fsv_offset = np.genfromtxt('fsv_offset.txt')
cube_rt = np.genfromtxt(r'D:\hall_probe-master\CMM PROGRAMS\MagnetCube-90dgX+_Upstream\CubeAlignment.txt')
cube_r = cube_rt[:9].reshape((3,3))
cube_t = cube_rt[9:]

def cube2mcs(coordinate):
    return (coordinate - cube_t)@cube_r

def mcs2cube(coordinate):
    return coordinate@np.linalg.inv(cube_r) + cube_t

retract = np.array([0, 0, 85])

print(f'current pos: {cmm.get_position()}')
print(f' retract coord: {cube2mcs(retract)+fsv_offset}')

cmm.close()