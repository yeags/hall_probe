from time import sleep
import numpy as np
import socket
import re

class CMM(socket.socket):
    '''
    Creates a TCP connection to the Zeiss CMM.
    '''
    def __init__(self, ip='192.4.1.200', port=4712):
        super().__init__(socket.AF_INET, socket.SOCK_STREAM)
        self.connect((ip, port))
        self.cnc_status = False
        self.speed = None
        self.position = None
        self.mcs = np.array([[1,0,0],
                             [0,1,0],
                             [0,0,1]])
        self.pcs_rotation = None
        self.pcs_offset = None
    
    def __repr__(self):
        return 'Zeiss CMM Object'

    def get_status(self):
        self.send('D16\r\n\x01'.encode('ascii'))
        self.status = self.recv(1024).decode('ascii')
    
    def cnc_on(self):
        self.send('D01\r\n'.encode('ascii'))
        self.cnc_status = True
    def cnc_off(self):
        self.send('D02\r\n'.encode('ascii'))
        self.cnc_status = False

    def set_speed(self, speed):
        '''
        speed in mm/s (int or float)
        '''
        self.send(f'G53X{speed}Y{speed}Z{speed}\r\n'.encode('ascii'))
    
    def wait(self, delay):
        while '@_' in self.get_status():
            pass
        while '@_' not in self.get_status():
            pass
        sleep(delay)
    
    def goto_position(self, xyz):
        self.send(f'G02X{xyz[0]}Y{xyz[1]}Z{xyz[2]}\r\n'.encode('ascii'))
    
    def step_cmm(self, xyz):
        self.send(f'G03X{xyz[0]}Y{xyz[1]}Z{xyz[2]}\r\n'.encode('ascii'))

    def get_position(self):
        self.send('D84\r\n\x01'.encode('ascii'))
        position_str = self.recv(1024).decode('ascii')
        self.position = np.array([float(i) for i in re.findall(r'[+-]\d+\.\d+', position_str)])


def scan_area(start_point, x_length, y_length, grid=0.5):
    '''
    start_point is a (3,) numpy array consisting of xyz coordinate
    function returns an (n, 3) array of waypoints for hall probe scanning a single plane
    '''
    end_point = start_point + [x_length, y_length, 0]
    num_waypoints = 4*y_length + 2
    num_y_patterns = int((num_waypoints-2)/4)
    x_pattern = np.tile(np.array([end_point[0], end_point[0], start_point[0], start_point[0]]), num_y_patterns)
    x = x_pattern.copy()
    x = np.insert(x, 0, start_point[0])
    
    x = np.append(x, end_point[0])
    y = np.array([[i, i] for i in np.arange(start_point[1], end_point[1]+grid, grid)]).flatten()
    z = np.array([start_point[2]]*num_waypoints)
    xyz = np.array([x, y, z]).T
    
    return xyz

def scan_volume(start_point, x_length, y_length, z_length, grid=0.5):
    '''
    function returns a (z_grid, waypoints, xyz columns) array which is a stack of planes along z
    '''
    end_point = start_point + [x_length, y_length, z_length]
    num_waypoints = 4*y_length + 2
    num_y_patterns = int((num_waypoints-2)/4)
    x_pattern = np.tile(np.array([end_point[0], end_point[0], start_point[0], start_point[0]]), num_y_patterns)
    x = x_pattern.copy()
    x = np.insert(x, 0, start_point[0])
    
    x = np.append(x, end_point[0])
    y = np.array([[i, i] for i in np.arange(start_point[1], end_point[1]+grid, grid)]).flatten()
    z_wp = np.array([start_point[2]]*num_waypoints)
    xyz_wp = np.array([x, y, z_wp]).T
    z = np.arange(start_point[2], end_point[2]+grid, grid)
    volume = np.zeros((z.shape[0], x.shape[0], 3))

    for h in range(volume.shape[0]):
        new_z = xyz_wp.copy()
        new_z[:, 2] = z[h]
        volume[h] = new_z
    
    return volume

def mcs(xyz_array, translation, rotation):
    pass

def pcs(xyz_array, translation, rotation):
    pass

if __name__ == '__main__':
    a = CMM()
    print(a)
    a.get_status()
    print(a.status)
    a.close()