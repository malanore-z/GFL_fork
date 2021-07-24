import os
import time

import multiprocessing
import threading


lock = multiprocessing.Lock()


class LockContext(object):

    def __init__(self, lock_):
        super(LockContext, self).__init__()
        self.lock = lock_

    def __enter__(self):
        if self.lock is not None:
            self.lock.acquire()

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.lock is not None:
            self.lock.release()


def print_log(id_, l_):
    filename = "log-%d" % id_
    file = open(filename, "w")
    start_time = time.time()
    if l_ is None:
        for i in range(1000000):
            file.write("line %d\n" % i)
    else:
        for i in range(1000000):
            l_.acquire()
            file.write("line %d\n" % i)
            l_.release()
    end_time = time.time()
    print("used time: %s" % (end_time - start_time))


if __name__ == "__main__":
    t1 = threading.Thread(target=print_log, args=(1, lock))
    t2 = threading.Thread(target=print_log, args=(2, lock))
    """
    t1 = multiprocessing.Process(target=print_log, args=(1, lock))
    t2 = multiprocessing.Process(target=print_log, args=(2, lock))
    """
    start_time = time.time()
    t1.start()
    t2.start()
    end_time = time.time()
    print("total time: %s" % (end_time - start_time))

    pass

"""
process: 
used time: 26.214951515197754
used time: 26.21695327758789
total time: 26.23595356941223
thread: 
used time: 2.4791018962860107
used time: 2.554136037826538
total time: 2.5581369400024414
none: 
used time: 1.1632161140441895
used time: 1.324186086654663
total time: 1.3261873722076416

process: 
used time: 24.97898244857788
used time: 24.978950262069702
total time: 25.239006996154785

thread:

none:
used time: 0.7026424407958984
used time: 0.7116060256958008
total time: 0.947641134262085
"""