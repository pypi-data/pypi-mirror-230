import queue
import random
import threading


class Runner:
    def __init__(self, jobs):
        self.jobcount = jobs
        self.threads = []
        self.jobqueue = queue.Queue()
        self.jobresults = queue.Queue()

    def start(self):
        if self.jobcount > 1:
            for _ in range(self.jobcount):
                self.threads.append(threading.Thread(target=self.run))
            for t in self.threads:
                t.start()

    def stop(self):
        while not self.jobqueue.empty():
            self.jobqueue.get_nowait()
        for _ in self.threads:
            self.jobqueue.put(None)
        for t in self.threads:
            t.join()
        self.threads = []

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, type, value, traceback):
        self.stop()

    def _call(self, fn, args, kwargs):
        try:
            return (args, kwargs, fn(*args, **kwargs), None)
        except Exception as e:
            return (args, kwargs, None, e)

    def run(self):
        while True:
            job = self.jobqueue.get()
            if job is None:
                return

            index, fn, args, kwargs = job

            self.jobresults.put((index, self._call(fn, args, kwargs)))

    def call(self, fn, calls):
        if self.threads:
            jobs = [
                (index, fn, args, kwargs) for index, (args, kwargs) in enumerate(calls)
            ]
            random.shuffle(jobs)
            for job in jobs:
                self.jobqueue.put(job)
            results = [self.jobresults.get() for _ in jobs]
            results.sort(key=lambda r: r[0])
            return [res for _, res in results]
        else:
            return [self._call(fn, args, kwargs) for args, kwargs in calls]
