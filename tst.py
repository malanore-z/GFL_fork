import time
import multiprocessing

from gfl.shell import Shell


def demo():
    for _ in range(10):
        time.sleep(1)
        print("child process tick")
    print("child process end")


if __name__ == "__main__":
    p = multiprocessing.Process(target=Shell.startup)
    p.start()
    print("main process end")
    # Shell.startup()
