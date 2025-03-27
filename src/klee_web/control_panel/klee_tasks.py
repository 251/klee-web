import datetime
import itertools
import json
import os
import redis

from copy import deepcopy
from worker.worker import celery
from frontend.models import Task


def get_workers():
    """Get a list of active Celery workers."""
    i = celery.control.inspect()
    return list(i.registered().keys()) if i and i.registered() else []


def registered_tasks(workers=None):
    """Fetch registered tasks per worker."""
    i = celery.control.inspect(workers)
    return remove_killed_tasks(i.registered() if i and i.registered() else {}, workers)


def active_tasks(workers=None):
    """Get currently active tasks per worker."""
    i = celery.control.inspect(workers)
    tasks = i.active() if i and i.active() else {}
    return populate_task_data(remove_killed_tasks(tasks, workers))


def scheduled_tasks(workers=None):
    """Get scheduled tasks."""
    i = celery.control.inspect(workers)
    return remove_killed_tasks(i.scheduled() if i and i.scheduled() else {}, workers)


def active_queues(workers=None):
    """Get active queues per worker."""
    i = celery.control.inspect(workers)
    return i.active_queues() if i and i.active_queues() else {}


def reserved_tasks(workers=None):
    """Fetch reserved tasks."""
    i = celery.control.inspect(workers)
    return remove_killed_tasks(i.reserved() if i and i.reserved() else {}, workers)


def redis_queue():
    """Retrieve tasks from Redis queue."""
    r = redis.StrictRedis(
        host=os.environ.get('REDIS_HOST', 'localhost'),
        port=int(os.environ.get('REDIS_PORT', 6379)),
        decode_responses=True
    )
    return r.lrange('celery', 0, -1)  # Get all pending tasks


def waiting_tasks():
    """Fetch all waiting tasks (Redis + reserved)."""
    redis_tasks = list(map(get_task_from_redis, redis_queue()))
    reserved = list(populate_task_data(reserved_tasks()))
    return redis_tasks + reserved


def revoked_tasks(workers=None):
    """Fetch revoked tasks."""
    i = celery.control.inspect(workers)
    return i.revoked() if i and i.revoked() else {}


def done_tasks():
    """Retrieve completed tasks from the DB."""
    tasks = Task.objects.filter(completed_at__isnull=False).order_by('-created_at')
    return list(map(populate_completed_task, tasks.values()))


def populate_task_data(tasks):
    """Enhance task data with database attributes."""
    task_ids = [t['id'] for t in tasks]
    task_map = {t.task_id: t for t in Task.objects.filter(task_id__in=task_ids)}

    all_tasks = []
    for t in tasks:
        task = {'id': t['id'], 'mach': t.get('mach', 'Unknown')}
        all_tasks.append(get_db_attrs(task, task_map))

    return all_tasks


def get_db_attrs(task, task_map=None):
    """Attach DB attributes to a task if it exists in the DB."""
    db_task = task_map.get(task['id']) if task_map else Task.objects.filter(task_id=task['id']).first()
    populated_task = deepcopy(task)

    if db_task:
        populated_task.update({
            'ip_address': db_task.ip_address,
            'created_at': db_task.created_at.isoformat(),
            'running_time': divmod((datetime.datetime.now() - db_task.created_at).total_seconds(), 60)
        })

    return populated_task


def get_task_from_redis(task_data):
    """Convert Redis task JSON to a dictionary."""
    try:
        task_json = json.loads(task_data)
        return get_db_attrs({
            'id': task_json.get('properties', {}).get('correlation_id', 'unknown'),
            'mach': 'Pending',
        })
    except (json.JSONDecodeError, KeyError, TypeError):
        return {'id': 'unknown', 'mach': 'Pending'}


def populate_completed_task(db_task):
    """Convert a completed DB task into a JSON-ready dict."""
    time_delta = db_task['completed_at'] - db_task['created_at']
    running_time = divmod(time_delta.total_seconds(), 60)

    return {
        'id': db_task['task_id'],
        'mach': db_task['worker_name'],
        'ip_address': db_task['ip_address'],
        'created_at': db_task['created_at'].isoformat(),
        'location': db_task['location'],
        'user': db_task['user'],
        'running_time': running_time,
    }


def kill_task(task_id):
    """Kill a Celery task and remove it from the DB."""
    Task.objects.filter(task_id=task_id).delete()
    celery.control.revoke(task_id, terminate=True, signal='SIGKILL')


def remove_killed_tasks(tasks, workers=None):
    """Remove revoked tasks from the task list."""
    revoked = revoked_tasks(workers) or {}

    set_revoked = set(itertools.chain.from_iterable(revoked.values())) if revoked else set()

    for mach, ts in tasks.items():
        for t in ts:
            t['mach'] = mach

    all_tasks = (filter(lambda t: t['id'] not in set_revoked, v) for v in tasks.values())
    return list(itertools.chain.from_iterable(all_tasks))
