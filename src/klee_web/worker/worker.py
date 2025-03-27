import os
import re
import subprocess
from celery import Celery
from celery.exceptions import SoftTimeLimitExceeded
from worker.worker_config import WorkerConfig
from worker.runner import WorkerRunner

# Initialize Celery app
celery = Celery(broker=os.environ['CELERY_BROKER_URL'], backend='rpc')

worker_config = WorkerConfig()


# Define a custom Celery task for uptime stats
@celery.task(name='get_uptime_stats')
def get_uptime_stats():
    uptime_pattern = re.compile(
        r'up\s+(.*?),\s+([0-9]+) '
        r'users?,\s+load averages?: '
        r'([0-9]+\.[0-9][0-9]),?\s+([0-9]+\.[0-9][0-9])'
        r',?\s+([0-9]+\.[0-9][0-9])')

    uptime_output = subprocess.check_output('uptime')
    uptime_matches = uptime_pattern.search(uptime_output)

    return {
        'uptime': uptime_matches.group(1),
        'users': uptime_matches.group(2),
        'loadavg_1min': uptime_matches.group(3),
        'loadavg_5min': uptime_matches.group(4),
        'loadavg_15min': uptime_matches.group(5),
    }


# Your submit_code task remains unchanged
@celery.task(name='submit_code', bind=True)
def submit_code(self, code, email, klee_args, endpoint):
    name = self.request.hostname
    with WorkerRunner(self.request.id, endpoint, worker_name=name) as runner:
        try:
            runner.run(code, email, klee_args)
        except SoftTimeLimitExceeded:
            result = {
                'klee_run': {
                    'output': f'Job exceeded time limit of {worker_config.timeout} seconds'
                }
            }
            runner.send_notification('job_failed', result)
