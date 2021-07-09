from time import perf_counter, sleep
import socket
import numpy as np
# import matplotlib.pyplot as plt
from scipy.stats import gmean


def time_packet(num_iter, no_delay=False, blocking=True):
    cmm = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    cmm.connect(('192.4.1.200', 4712))
    cmm.setblocking(blocking)
    if no_delay:
        cmm.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
    times = []
    for i in range(num_iter):
        start = perf_counter()
        cmm.send('D84\r\n\x01'.encode('ascii'))
        data = b''
        while True:
            try:
                data += cmm.recv(47)
                if data:
                    break
            except:
                pass
        end = perf_counter()
        times.append((end-start)*1000)
        sleep(0.05)
    cmm.close()
    return np.array(times)

# def plot_times(data, bins):
#     for i in data:
#         fig, ax = plt.subplots()
#         ax.hist(i, bins=bins)
#     plt.show()

def print_stats(data):
    print(f'mean: {data.mean()}')
    print(f'gmean: {gmean(data)}')
    print(f'std: {data.std(ddof=1)}\n')

num_packets = 300

t_delay = time_packet(num_packets)
t_nodelay = time_packet(num_packets, no_delay=True, blocking=True)
np.savetxt('packet_times.txt', np.array([t_delay, t_nodelay]).reshape((num_packets,2)), fmt='%.3f', delimiter=' ')
print('Default Socket\n--------------')
print_stats(t_delay)
print('No Delay Socket\n---------------')
print_stats(t_nodelay)