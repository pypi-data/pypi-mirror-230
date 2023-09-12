import threading
import time
from queue import Queue, PriorityQueue
from functools import wraps
from werkzeug.local import LocalProxy

class Celery:
    def __init__(self, app=None):
        self.app = app
        self.tasks = Queue()
        self.priority_tasks = PriorityQueue()
        self.result_store = {}
        self.worker_thread = threading.Thread(target=self._worker)
        self.worker_thread.daemon = True
        self.worker_thread.start()
        self.rate_limits = {}

    def _worker(self):
        while True:
            try:
                priority, task, task_id, args, kwargs, retries = self.priority_tasks.get_nowait()
            except Queue.Empty:
                try:
                    task, task_id, args, kwargs, retries = self.tasks.get(timeout=1)
                except Queue.Empty:
                    continue

            try:
                result = task(*args, **kwargs)
                self.result_store[task_id] = result
                print("Task result:", result)
            except Exception as e:
                if retries > 0:
                    print(f"Error executing task: {e}. Retrying...")
                    self.priority_tasks.put((priority, task, task_id, args, kwargs, retries - 1))
                else:
                    self.result_store[task_id] = None
                    print("Error executing task:", e)
                    # Add logic here for error handling
            finally:
                if self.priority_tasks.empty():
                    self.tasks.task_done()
                else:
                    self.priority_tasks.task_done()

    def retry_with_delay(self, max_retries, delay=0, backoff=2):
        def decorator(f):
            @wraps(f)
            def wrapper(*args, **kwargs):
                task_id = len(self.result_store) + 1
                self.tasks.put((f, task_id, args, kwargs, max_retries, delay, backoff))
                return TaskResult(self, task_id)
            return wrapper
        return decorator

    def retry_backoff(self, max_retries, delay=0, backoff=2):
        def decorator(f):
            @wraps(f)
            def wrapper(*args, **kwargs):
                task_id = len(self.result_store) + 1
                self.tasks.put((f, task_id, args, kwargs, max_retries, delay, backoff))
                return TaskResult(self, task_id)
            return wrapper
        return decorator

    def shared_task(self, f):
        @wraps(f)
        def delay(*args, **kwargs):
            task_id = len(self.result_store) + 1
            self.tasks.put((f, task_id, args, kwargs, 3))  # 3 retries by default
            return TaskResult(self, task_id)
        return delay

    def task(self, f):
        @wraps(f)
        def delay(*args, **kwargs):
            task_id = len(self.result_store) + 1
            self.tasks.put((f, task_id, args, kwargs, 3))  # 3 retries by default
            return TaskResult(self, task_id)
        return delay
    
    def rate_limit(self, limit, key_func=None, shared=False):
        def decorator(f):
            @wraps(f)
            def wrapper(*args, **kwargs):
                if key_func:
                    key = key_func(*args, **kwargs)
                else:
                    key = f.__name__

                if not shared:
                    # Individual rate limiting
                    allowed = self._check_rate_limit_individual(key, limit)
                else:
                    # Shared rate limiting
                    allowed = self._check_rate_limit_shared(key, limit)

                if allowed:
                    return f(*args, **kwargs)
                else:
                    # Handle rate limit exceeded
                    return "Rate limit exceeded", 429
            return wrapper
        return decorator

    def _check_rate_limit_individual(self, key, limit):
        now = time.time()
        if key in self.rate_limits:
            count, timestamp = self.rate_limits[key]
            if now - timestamp < 1:  # 1 second interval
                if count >= limit:
                    return False
                else:
                    self.rate_limits[key] = (count + 1, timestamp)
                    return True
            else:
                self.rate_limits[key] = (1, now)
                return True
        else:
            self.rate_limits[key] = (1, now)
            return True

    def _check_rate_limit_shared(self, key, limit):
        now = time.time()
        if 'shared' in self.rate_limits:
            count, timestamp = self.rate_limits['shared']
            if now - timestamp < 1:  # 1 second interval
                if count >= limit:
                    return False
                else:
                    self.rate_limits['shared'] = (count + 1, timestamp)
                    return True
            else:
                self.rate_limits['shared'] = (1, now)
                return True
        else:
            self.rate_limits['shared'] = (1, now)
            return True
        
    def priority_task(self, priority):
        def decorator(f):
            @wraps(f)
            def wrapper(*args, **kwargs):
                task_id = len(self.result_store) + 1
                self.priority_tasks.put((priority, f, task_id, args, kwargs, 3))  # 3 retries by default
                return TaskResult(self, task_id)
            return wrapper
        return decorator

    def retry(self, max_retries, delay=0, backoff=2):
        def decorator(f):
            @wraps(f)
            def wrapper(*args, **kwargs):
                task_id = len(self.result_store) + 1
                self.tasks.put((f, task_id, args, kwargs, max_retries, delay, backoff))
                return TaskResult(self, task_id)
            return wrapper
        return decorator

    def schedule_periodic(self, interval, task, *args, **kwargs):
        def periodic_task():
            while True:
                task(*args, **kwargs)
                time.sleep(interval)
        thread = threading.Thread(target=periodic_task)
        thread.daemon = True
        thread.start()

    def create_task(self, func, *args, **kwargs):
        task_id = len(self.result_store) + 1
        return Task(self, func, task_id, args, kwargs)

    def task_decorator(self, func):
        def decorator(*args, **kwargs):
            return self.create_task(func, *args, **kwargs)
        return decorator

    def get_celery_task(self):
        return LocalProxy(lambda: self)

    def get_result(self, task_id):
        return self.result_store.get(task_id)

    def group(self, *tasks):
        return TaskGroup(self, tasks)

    def chord(self, tasks, body):
        return ChordTask(self, tasks, body)

    def chain(self, *tasks):
        return ChainTask(self, tasks)

    def signature(self, task, *args, **kwargs):
        return Signature(self, task, args, kwargs)

    def schedule_task(self, task, delay=0, priority=0, retries=0, *args, **kwargs):
        task_id = len(self.result_store) + 1
        task_args = (task, task_id, args, kwargs, retries)

        if delay > 0:
            time.sleep(delay)

        if priority > 0:
            self.priority_tasks.put((priority, *task_args))
        else:
            self.tasks.put(task_args)

        return TaskResult(self, task_id)
    
class TaskResult:
    def __init__(self, celery, task_id):
        self.celery = celery
        self.task_id = task_id

    def result(self):
        return self.celery.get_result(self.task_id)

class Task:
    def __init__(self, celery, func, task_id, args=None, kwargs=None):
        self.celery = celery
        self.func = func
        self.task_id = task_id
        self.args = args or ()
        self.kwargs = kwargs or {}

    def delay(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs
        self.celery.tasks.put((self.func, self.task_id, self.args, self.kwargs))
        return TaskResult(self.celery, self.task_id)

class TaskGroup:
    def __init__(self, celery, tasks):
        self.celery = celery
        self.tasks = tasks

    def apply_async(self):
        task_results = [task.delay() for task in self.tasks]
        return GroupResult(self.celery, task_results)

class GroupResult:
    def __init__(self, celery, task_results):
        self.celery = celery
        self.task_results = task_results

    def join(self):
        return [task_result.result() for task_result in self.task_results]

class ChordTask:
    def __init__(self, celery, tasks, body):
        self.celery = celery
        self.tasks = tasks
        self.body = body

    def apply_async(self):
        group_result = self.celery.group(*self.tasks).apply_async()
        result = group_result.join()
        return self.body(*result)

class ChainTask:
    def __init__(self, celery, tasks):
        self.celery = celery
        self.tasks = tasks

    def apply_async(self):
        return ChainResult(self.celery, self.tasks)

class ChainResult:
    def __init__(self, celery, tasks):
        self.celery = celery
        self.tasks = tasks

    def apply_async(self):
        return ChainResult(self.celery, self.tasks)

    def next(self, task):
        return ChainResult(self.celery, self.tasks + (task,))

    def join(self):
        for task in self.tasks:
            task.delay().result()

class Signature:
    def __init__(self, celery, task, args, kwargs):
        self.celery = celery
        self.task = task
        self.args = args
        self.kwargs = kwargs

    def apply_async(self):
        return self.task.delay(*self.args, **self.kwargs)