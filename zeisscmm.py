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
        # self.position = None
        self.get_status()
    
    def __repr__(self):
        return 'Zeiss CMM Object'

    def get_status(self):
        self.send('D16\r\n\x01'.encode('ascii'))
        self.status = self.recv(1024).decode('ascii')
        return self.status
    
    def cnc_on(self):
        self.send('D01\r\n'.encode('ascii'))
        self.cnc_status = True
    def cnc_off(self):
        self.send('D02\r\n'.encode('ascii'))
        self.cnc_status = False

    def set_speed(self, speed):
        '''
        speed in mm/s (3,) array
        '''
        self.speed = speed
        self.send(f'G53X{round(speed[0], 3)}Y{round(speed[1], 3)}Z{round(speed[2], 3)}\r\n'.encode('ascii'))
    
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
        return np.array([float(i) for i in re.findall(r'[+-]\d+\.\d+', position_str)])
    
    def get_positions(self):
        self.send('D17\r\n\x01'.encode('ascii'))
        position_str = self.recv(1024).decode('ascii')
        position_np = np.array([float(i) for i in re.findall(r'[+-]\d*\.\d+', position_str)])
        return (position_np[:3], position_np[4:])
    
    def get_lag_distance(self):
        self.send('D19\r\n\x01'.encode('ascii'))
        lag = self.recv(1024).decode('ascii')
        lag_np = np.array([float(i) for i in re.findall(r'[-\+]\d*\.\d+', lag)][:3])
        return lag_np
    
    def get_workpiece_temp(self):
        self.send('D07\r\n\x01'.encode('ascii'))
        response = self.recv(1024).decode('ascii')
        temp = [float(i) for i in re.findall(r'\d+\.\d+', response)]
        avg_temp = (temp[2] + temp[3]) / 2
        return avg_temp


def generate_scan_area(start_point, x_length, y_length, grid=0.5):
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

def generate_scan_volume(start_point, x_length, y_length, z_length, grid=0.5):
    '''
    function returns a (z index, waypoints, xyz columns) array which is a stack of planes along z
    '''
    end_point = start_point + [x_length, y_length, z_length]
    num_waypoints = int(2*(1/grid)*y_length + 2)
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
    new_z = xyz_wp.copy()

    for h in range(volume.shape[0]):
        new_z[:, 2] = z[h]
        volume[h] = new_z
    
    return volume

def transform_points(xyz_array, translation, rotation, inverse=False):
    '''
    xyz_array is a 2d or 3d numpy array of coordinate values
    translation is a (3,) array
    rotation is a (3,3) array
    use inverse=True to go from mcs to pcs coordinates
    '''
    xyz_array_copy = xyz_array.copy()
    if not inverse:
        if xyz_array.ndim == 1:
            xyz_array_copy = rotation@xyz_array + translation
        
        elif xyz_array.ndim == 2:
            for i, point in enumerate(xyz_array):
                xyz_array_copy[i] = rotation@point + translation

        elif xyz_array.ndim == 3:
            for i, height in enumerate(xyz_array):
                for j, point in enumerate(height):
                    xyz_array_copy[i, j] = rotation@point + translation

    else:
        if xyz_array.ndim == 1:
            xyz_array_copy = np.linalg.inv(rotation)@(xyz_array - translation)
        
        elif xyz_array.ndim == 2:
            for i, point in enumerate(xyz_array):
                xyz_array_copy[i] = np.linalg.inv(rotation)@(point - translation)

        elif xyz_array.ndim == 3:
            for i, height in enumerate(xyz_array):
                for j, point in enumerate(height):
                    xyz_array_copy[i, j] = np.linalg.inv(rotation)@(point - translation)
    return xyz_array_copy

if __name__ == '__main__':
    with CMM() as test:
        print(test)
        test.get_status()
        print(test.status)
        test.get_position()
        print(test.position)