from multiprocessing import Process, Queue, cpu_count
import time
import random


currentProcesses = []
returnQueues = []

threadAmount = 100


def MyTask(secs, q):
    print(f"Waiting {secs} secs")
    time.sleep(secs)
    q.put(secs)


if __name__ == '__main__':

    for i in range(threadAmount):
        returnQueue = Queue()
        returnQueues.append(returnQueue)

        process = Process(target=MyTask, args=(random.randint(1, 10), returnQueues[i], ))
        currentProcesses.append(process)
        currentProcesses[i].start()


    while True:
        for i in range(threadAmount):
            if not currentProcesses[i].is_alive():
                data = returnQueues[i].get()
                print(f"Got {data} from thread {i}, restarting it and passing in new data")

                returnQueues[i] = Queue()
                currentProcesses[i] = Process(target=MyTask, args=(data, returnQueues[i], ))
                currentProcesses[i].start()
