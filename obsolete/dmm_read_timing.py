import time
import nidmm
from numpy import array
import matplotlib.pyplot as plt

hall = nidmm.Session('Dev1')
hall.configure_measurement_digits(nidmm.Function.DC_VOLTS, 1, 5.5)
hall.configure_trigger(nidmm.TriggerSource.IMMEDIATE)

x = []
y = []
start = time.time()
for i in range(20):
    x.append(time.time())
    y.append(hall.read())
    time.sleep(0.1)
delta = time.time() - start
avg_lag = (delta-1)/10
print(delta, avg_lag)

x = array(x)
y = array(y)
x = x - start

plt.scatter(x, y, marker='.')
plt.grid()
plt.show()
