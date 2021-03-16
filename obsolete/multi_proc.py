
# Example of distributing function operation over multiple cpu's

from multiprocessing import Pool
import time

a = [i for i in range(16)]

def f(x: list):
    print(x)
    time.sleep(1)

if __name__ == '__main__':
    start = time.perf_counter()
    with Pool() as p:
        p.map(f, a)

    end = time.perf_counter()
    print(f'completed in {end-start:.2f}s')


'''


from multiprocessing import Process
import os

def info(title):
    print(title)
    print('module name:', __name__)
    print('parent process:', os.getppid())
    print('process id:', os.getpid())

def f(name):
    info('function f')
    print('hello', name)

if __name__ == '__main__':
    info('main line')
    p = Process(target=f, args=('bob',))
    p.start()
    p.join()
'''