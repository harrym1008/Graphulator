import concurrent.futures
import time

def Waiting(wait):
    print(f"sleeping {wait} seconds ")
    time.sleep(wait)
    return wait


with concurrent.futures.ThreadPoolExecutor() as executor:
    f1 = executor.submit(Waiting, 1.5)
    f2 = executor.submit(Waiting, 1.5)
    print(f1.result())
    print(f2.result())


'''ts = []
for i in range(40):
    t = threading.Thread(target=Waiting, args=[i/10])
    t.start()
    ts.append(t)

for i in ts:
    i.join()'''

print("Done ")
