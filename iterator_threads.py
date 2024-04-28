import queue
import threading

def chain(*iterables):
    """Yields elements from any of the given iterables.
    Each of the iterables runs in their own thread."""
    q = queue.Queue()

    def run(iterable, end_token):
        try:
            for x in iterable:
                q.put(x)
        finally:
            q.put(end_token)

    threads = dict()
    for iter in iterables:
        token = object()
        thread = threading.Thread(target=run, args=(iter, token))
        threads[token] = thread
        thread.start()

    while threads:
        e = q.get()
        if e in threads:
            threads.pop(e)
            continue
        yield e

if __name__ == "__main__":
    print("Testing!")
    import random
    import time

    def r(number):
        for x in range(10):
            time.sleep(random.random() * 10.0)
            yield (number, x)

    for x in chain(*[r(n) for n in range(4)]):
        print(x)
