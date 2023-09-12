import threading
import concurrent.futures
import time
from queue import Queue

class APScheduler:
    def __init__(self, app=None, num_threads=4):
        self.jobs = []
        self.jobs_lock = threading.Lock()
        self.running = False
        self.num_threads = num_threads
        self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=num_threads)
        self.job_queue = Queue()
        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        app.apscheduler = self

    def add_job(self, func, interval=10, repeat=True, args=(), kwargs=None):
        job = {
            "func": func,
            "interval": interval,
            "repeat": repeat,
            "args": args,
            "kwargs": kwargs or {},
            "last_run_time": None,
            "next_run_time": None,
        }
        with self.jobs_lock:
            self.jobs.append(job)

        if self.running:
            self.job_queue.put(job)

    def remove_job(self, func):
        with self.jobs_lock:
            for job in self.jobs:
                if job["func"] == func:
                    job["repeat"] = False

    def _job_runner(self, job):
        while job["repeat"]:
            job["last_run_time"] = time.time()
            job["next_run_time"] = job["last_run_time"] + job["interval"]
            job["func"](*job["args"], **job["kwargs"])
            time_until_next_run = job["next_run_time"] - time.time()
            if time_until_next_run > 0:
                time.sleep(time_until_next_run)

    def _submit_job(self, job):
        if job["repeat"]:
            self.executor.submit(self._job_runner, job)

    def _worker(self):
        while self.running:
            job = self.job_queue.get()
            if job:
                self._submit_job(job)
                self.job_queue.task_done()

    def start(self):
        if not self.running:
            self.running = True
            for _ in range(self.num_threads):
                threading.Thread(target=self._worker, daemon=True).start()

    def stop(self):
        self.running = False
        self.job_queue.join()
        self.job_queue = Queue()  # Clear the queue

    def modify_job(self, func, interval=None, args=(), kwargs=None):
        with self.jobs_lock:
            for job in self.jobs:
                if job["func"] == func:
                    if interval is not None:
                        job["interval"] = interval
                    if args:
                        job["args"] = args
                    if kwargs:
                        job["kwargs"] = kwargs

    def get_jobs(self):
        with self.jobs_lock:
            return self.jobs

    def get_job(self, func):
        with self.jobs_lock:
            for job in self.jobs:
                if job["func"] == func:
                    return job

    def pause_job(self, func):
        job = self.get_job(func)
        if job:
            job["repeat"] = False

    def resume_job(self, func):
        job = self.get_job(func)
        if job:
            job["repeat"] = True
            job["next_run_time"] = time.time() + job["interval"]
            self.job_queue.put(job)

    def stop_job(self, func):
        job = self.get_job(func)
        if job:
            job["repeat"] = False
            job["next_run_time"] = None

    def reschedule_job(self, func, interval=None):
        job = self.get_job(func)
        if job:
            if interval is not None:
                job["interval"] = interval
            job["next_run_time"] = time.time() + job["interval"]