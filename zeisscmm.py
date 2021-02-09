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

    def set_speed(self, speed: float):
        '''
        Double check to make sure speed command is G01 or G53!!!
        '''
        self.send(f'G01X{speed}Y{speed}Z{speed}\r\n'.encode('ascii'))
    
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


if __name__ == '__main__':
    a = CMM()
    print(a)
    a.get_status()
    print(a.status)
    a.close()