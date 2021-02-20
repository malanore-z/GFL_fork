import os
import time

from daemoniker import Daemonizer


def child_proc():
    time.sleep(10)
    outfile = open("child_out", "w")
    work_dir = os.path.dirname(os.path.dirname(__file__))
    outfile.write(work_dir)
    outfile.write("\n")
    if os.path.exists("pid_file"):
        outfile.write("true")
    else:
        outfile.write("false")
    outfile.write("\n")
    outfile.write("Child - %d\n" % os.getpid())
    outfile.flush()
    outfile.close()
    time.sleep(10)


def parent_proc():
    print("Parent - %d" % os.getpid())
    with Daemonizer() as (is_setup, daemonizer):
        is_parent = daemonizer("pid_file")
    child_proc()


if __name__ == "__main__":
    parent_proc()


