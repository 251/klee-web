import os
import redis
from klee_web.worker.worker import celery


def registered_tasks(workers=None):
    """Returns tasks registered to workers."""
    i = celery.control.inspect(workers)
    return i.registered() if i and i.registered() else {}


def active_tasks(workers=None):
    """Returns currently executing tasks."""
    i = celery.control.inspect(workers)
    return i.active() if i and i.active() else {}


def scheduled_tasks(workers=None):
    """Returns scheduled tasks."""
    i = celery.control.inspect(workers)
    return i.scheduled() if i and i.scheduled() else {}


def reserved_tasks(workers=None):
    """Returns tasks taken off the queue by a worker, waiting to be executed."""
    i = celery.control.inspect(workers)
    return i.reserved() if i and i.reserved() else {}


def active_queues(workers=None):
    """Returns active queues per worker."""
    i = celery.control.inspect(workers)
    return i.active_queues() if i and i.active_queues() else {}


def get_workers():
    """Returns a list of active Celery workers."""
    i = celery.control.inspect()
    return list(i.registered().keys()) if i and i.registered() else []


def redis_queue():
    """Returns tasks in the Redis queue that haven't been assigned to a worker."""
    r = redis.StrictRedis(
        host=os.environ.get('REDIS_HOST', 'localhost'),
        port=int(os.environ.get('REDIS_PORT', 6379)),
        decode_responses=True  # Ensures JSON handling is smoother
    )
    return r.lrange('celery', 0, -1)  # Get all pending tasks


def kill_task(task_id):
    """Forcefully kills a Celery task."""
    celery.control.revoke(task_id, terminate=True, signal='SIGKILL')
