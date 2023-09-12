#!python
import sys
import multiprocessing as mp
import time
import random


def worker(i):
    print(i)
    time.sleep(random.random())
    return i

def main():
    fw = open("a.txt", "w+")
    threads = 2
    max_submitted_task = threads * 2
    pool = mp.Pool(threads, maxtasksperchild=1)
    submitted_task_list = []
    for i in range(30):
        while True:
            if len(submitted_task_list) > 0:
                r = submitted_task_list[0]
                if r.ready():
                    assert r.successful()
                    fw.write("%s\n" % r.get())
                    submitted_task_list.pop(0)
                
            if len(submitted_task_list) < max_submitted_task:
                r = pool.apply_async(worker, (i, ))
                submitted_task_list.append(r)
                break
            else:
                time.sleep(1)

    while len(submitted_task_list) > 0:
        r = submitted_task_list[0]
        if r.ready():
            assert r.successful()
            fw.write("%s\n" % r.get())
            submitted_task_list.pop(0)
        else:
            time.sleep(1)

    pool.close()
    pool.join()

    fw.close()

main()

