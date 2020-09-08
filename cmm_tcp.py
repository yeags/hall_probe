import socket

cmm = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
cmm.connect(('192.4.1.200', 4712))

def send_cmd(command, recv_response=True):
    if recv_response:
        cmm.send((command+'\r\n\x01').encode('ascii'))
        data = cmm.recv(1024).decode('ascii')
        return data
    else:
        cmm.send((command+'\r\n').encode('ascii'))

