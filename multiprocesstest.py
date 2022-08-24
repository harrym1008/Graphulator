import multiprocessing
import time


def task(queue):
    while True:
        i = queue.get()
        i += 1
        time.sleep(0.1)
        queue.put(i)


q = multiprocessing.Queue()
q.put(10)

p = multiprocessing.Process(target=task, args=(q,))
p.start()

while True:
    print(q.queue[0])
