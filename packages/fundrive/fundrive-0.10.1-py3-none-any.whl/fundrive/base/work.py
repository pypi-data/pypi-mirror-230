import time
from queue import Queue
from threading import Thread
from typing import List

import requests


def _get_size(url):
    with requests.Session() as sess:
        resp = sess.get(url, stream=True)
        return int(resp.headers.get("content-length", 0))


class Worker:
    def __init__(self, url: str, filepath, range_start=0, range_end=None, callback=None, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.url = url
        self.filepath = filepath

        self.range_start = range_start
        self.range_curser = range_start
        self.range_end = range_end or _get_size(url)
        self.size = self.range_end - self.range_start
        self.callback = callback

    def run(self):
        chunk_size = 1 * 1024
        header = {"Range": f"bytes={self.range_curser}-{self.range_end}"}
        with requests.get(self.url, stream=True, headers=header) as req:
            if 200 <= req.status_code <= 299:
                with open(self.filepath, "wb") as cache:
                    for chunk in req.iter_content(chunk_size=chunk_size):
                        cache.write(chunk)
                        self.range_curser += len(chunk)
        if self.callback:
            self.callback(self)

    def __lt__(self, another):
        return self.range_start < another.range_start

    def get_progress(self):
        """progress for each worker"""
        return {"curser": self.range_curser, "start": self.range_start, "end": self.range_end, "total": self.size}


class _WorkerFactory(object):
    def __init__(self, worker_num, capacity, timeout=30):
        self.worker_num = worker_num
        self._task_queue = Queue(maxsize=capacity)
        self.timeout = timeout
        self._threads: List[Thread] = []
        self._close = False

    def submit(self, worker):
        self._task_queue.put(worker)

    def join(self):
        for thread in self._threads:
            thread.join()

    def start(self):
        for i in range(self.worker_num):
            thread = Thread(target=self._worker)
            thread.start()
            self._threads.append(thread)

    def _worker(self):
        while True:
            try:
                worker = self._task_queue.get(timeout=self.timeout)
                worker.run()
                self._task_queue.task_done()
            except Exception as e:
                pass
            if self._close:
                break

    def close(self):
        self._close = True

    def empty(self):
        return self._task_queue.empty()


class WorkerFactory(object):
    def __init__(self, worker_num=5, capacity=50, timeout=30):
        self.worker_num = worker_num
        self.capacity = capacity
        self.timeout = timeout
        self._handle: _WorkerFactory = ...

    def __enter__(self):
        self._handle = _WorkerFactory(worker_num=self.worker_num, capacity=self.capacity, timeout=self.timeout)
        self._handle.start()
        return self._handle

    def __exit__(self, exc_type, exc_val, exc_tb):
        while not self._handle.empty():
            time.sleep(1)
        self._handle.close()
        return True
