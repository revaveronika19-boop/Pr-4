"""Практичні приклади багатопоточності."""
import threading, time, queue, os
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor

def io_task(n):
    time.sleep(0.03)
    return f'Завдання {n} виконано у {threading.current_thread().name}'
def is_prime(n):
    if n<2:return False
    for k in range(2,int(n**0.5)+1):
        if n%k==0:return False
    return True
def sum_primes(a,b): return sum(n for n in range(a,b) if is_prime(n))
class SafeCounter:
    def __init__(self): self.value=0; self.lock=threading.Lock()
    def add(self):
        with self.lock: self.value+=1

def main():
    print('1. Потоки:')
    with ThreadPoolExecutor(max_workers=5) as pool:
        for result in pool.map(io_task,range(5)): print(result)
    print('2. Процеси:')
    ranges=[(2,5000),(5000,10000)]
    with ProcessPoolExecutor(max_workers=2) as pool:
        print('Сума простих:',sum(pool.map(sum_primes,*zip(*ranges))))
    print('3. Lock:')
    counter=SafeCounter()
    threads=[threading.Thread(target=lambda: [counter.add() for _ in range(1000)]) for _ in range(5)]
    for t in threads:t.start()
    for t in threads:t.join()
    print('Лічильник:',counter.value)
    print('4. Queue + Event:')
    q=queue.Queue(); stop=threading.Event()
    def worker():
        while not stop.is_set() or not q.empty():
            try: item=q.get(timeout=.1)
            except queue.Empty:continue
            print('Оброблено:',item);q.task_done()
    t=threading.Thread(target=worker);t.start()
    for i in range(3):q.put(i)
    q.join();stop.set();t.join()
    print('5. Semaphore:')
    sem=threading.Semaphore(2)
    def limited(i):
        with sem: time.sleep(.01);return i*i
    with ThreadPoolExecutor(max_workers=5) as pool:print(list(pool.map(limited,range(5))))
if __name__=='__main__':main()
