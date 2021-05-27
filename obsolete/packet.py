import numpy as np
import matplotlib.pyplot as plt


data = np.genfromtxt('packet_time.csv', delimiter=',', skip_header=1)

data_response = data[:, 1] - data[:, 0]

timing = []

for i in range(data.shape[0]-1):
    timing.append(data[i+1, 0] - data[i, 0])
timing = np.array(timing)

def stdev(y):
    return y/y.std(ddof=1)

def stdy(y):
    return y

plt.figure(figsize=(11, 8.5))
plt.subplots_adjust(hspace=0.3)
plt.suptitle('Packet Latency')
plt.subplot(211)
plt.scatter([i for i in range(data_response.shape[0])],
            data_response, marker='.')
plt.xlabel('packet')
plt.ylabel('latency [s]')
plt.grid()
plt.ylim(data_response.min()-data_response.std(ddof=1),
         data_response.max()+data_response.std(ddof=1))

plt.subplot(212)
plt.hist(data_response, bins=40)
plt.xlabel('latency [s]')
plt.ylabel('frequency')
plt.grid()
plt.savefig('packet latency.pdf')

plt.figure(figsize=(11, 8.5))
plt.subplots_adjust(hspace=0.3)
plt.suptitle('Packet Transmit Variance')
plt.subplot(211)
plt.scatter([i for i in range(timing.shape[0])],
            timing, marker='.')
plt.ylim(timing.min()-timing.std(ddof=1),
         timing.max()+timing.std(ddof=1))
plt.xlabel('packet')
plt.ylabel('variance [s]')
plt.grid()

plt.subplot(212)
plt.hist(timing, bins=40)
plt.xlabel('variance [s]')
plt.ylabel('frequency')
plt.grid()
plt.savefig('packet transmit variance.pdf')

plt.show()
