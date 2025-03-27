import datetime

from django.contrib import messages
from django.urls import reverse
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import render

from .decorators import group_required
from .forms import AdminConfigForm
from worker.worker import celery
from worker.worker_config import WorkerConfig
from . import usage_stats
from . import klee_tasks

HUMAN_READABLE_FIELD_NAMES = {
    "timeout": "Timeout",
    "cpu_share": "CPU Share",
    "memory_limit": "Memory Limit"
}

worker_configuration = WorkerConfig()


@group_required("admin")
def index(request):
    attrs = {
        'total_done': len(klee_tasks.done_tasks()),
        'avg_time': usage_stats.avg_job_duration(),
        'jobs_per_day': usage_stats.avg_jobs_per_day(),
        'today': datetime.datetime.now().strftime("%a %d/%m/%Y %H:%M")
    }
    return render(request, "control_panel/index.html", attrs)


@group_required("admin")
def get_job_history(request):
    days, job_count = usage_stats.last_seven_days()
    return JsonResponse({"days": days, "count": job_count})


@group_required("admin")
def worker_config(request):
    if request.method == 'POST':
        form = AdminConfigForm(request.POST)
        if form.is_valid():
            updated = []

            for conf in form.cleaned_data:
                data = form.cleaned_data[conf]
                if data is not None:
                    worker_configuration.set_config(conf, data)
                    updated.append(HUMAN_READABLE_FIELD_NAMES[conf])

            if updated:
                messages.success(request, ", ".join(updated) + " updated")

            return HttpResponseRedirect(reverse('control_panel:worker_config'))
    else:
        form = AdminConfigForm(
            initial={
                'cpu_share': worker_configuration.cpu_share,
                'memory_limit': worker_configuration.memory_limit,
                'timeout': worker_configuration.timeout
            }
        )
    return render(request, "control_panel/worker_config.html", {'form': form})


@group_required("admin")
def worker_list(request):
    """Retrieve worker uptime stats using Celery 5.4"""
    inspector = celery.control.inspect()
    uptime_stats = inspector.get_uptime_stats() or {}  # Handle case where no workers reply

    return render(
        request,
        "control_panel/worker_list.html",
        {
            "uptime_stats": uptime_stats
        }
    )


@group_required("admin")
def kill_task(request):
    klee_tasks.kill_task(request.POST['task_id'])
    return HttpResponseRedirect(
        reverse('control_panel:task_list', args=[request.POST['type']])
    )


@group_required("admin")
def task_list(request, type):
    """Get tasks based on their type"""
    task_map = {
        'active': klee_tasks.active_tasks,
        'waiting': klee_tasks.waiting_tasks,
        'done': klee_tasks.done_tasks,
    }

    attrs = {
        'tasks': task_map.get(type, lambda: klee_tasks.active_tasks())(),
        'page': type
    }
    return render(request, "control_panel/task_list.html", attrs)
