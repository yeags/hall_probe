import multiprocessing as mp
from time import perf_counter
# from itertools import cycle
from random import randint

def sleep(duration, get_now=perf_counter):
    now = get_now()
    end = now + duration
    while now < end:
        now = get_now()

def f(x, status):
    # for i in cycle([j for j in range(10)]):
    while True:
        # x.put(i)
        x.put(randint(1, 20))
        sleep(0.0125)
        if x.qsize() != 0:
            x.get()
        else:
            break

def g(x, status):
    for i in range(20):
        print(f'q size: {x.qsize()} contents: {x.get()}')
        sleep(0.0754)
    status.put(1)



if __name__ == '__main__':
    q = mp.Queue()
    q_status = mp.Queue()
    p = mp.Process(target=f, args=(q, q_status))
    p2 = mp.Process(target=g, args=(q, q_status))
    p.start()
    p2.start()
    # p.join()
    # p2.join()