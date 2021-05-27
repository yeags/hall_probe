import threading
import numpy as np
from time import perf_counter
from calibration import remove_outliers

hs = np.random.random((1000,4))
mt = np.random.random((1000,8))

hs_thread = threading.Thread(target=remove_outliers, args=(hs,))
mt_thread = threading.Thread(target=remove_outliers, args=(mt,))

sequential_start = perf_counter()
remove_outliers(hs)
remove_outliers(mt)
sequential_end = perf_counter()

threaded_start = perf_counter()
hs_thread.start()
mt_thread.start()
hs_thread.join()
mt_thread.join()
threaded_end = perf_counter()

print(f'Sequential operation took {1000*(sequential_end - sequential_start)} ms')
print(f'Threaded operation took {1000*(threaded_end - threaded_start)} ms')