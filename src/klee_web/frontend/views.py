import datetime
from django.contrib.auth.decorators import login_required
from django.forms.utils import ErrorList

from django.shortcuts import get_object_or_404, render, redirect
from django.http import HttpResponse, HttpResponseNotFound, FileResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.urls import reverse
from django.contrib import messages, auth
from django.contrib.auth import update_session_auth_hash

from .forms import SubmitJobForm, UserCreationForm, UserChangePasswordForm
from .models import Task
import json
import os


def index(request):
    form = SubmitJobForm()
    return render(request, 'frontend/index.html', {'form': form})


def store_data(task, type, data):
    d = {'type': type, 'data': data}
    task.current_output = json.dumps(d)
    task.save()


def jobs_dl(request, job_id):
    if request.method == 'GET':
        file_path = os.path.join('/tmp/', f"{job_id}.tar.gz")
        if os.path.exists(file_path):
            return FileResponse(open(file_path, 'rb'), as_attachment=True)
        return HttpResponseNotFound("File not found")
    return HttpResponseNotFound("This page only supports GET")


@csrf_exempt
def jobs_notify(request):
    if request.method == 'POST':
        type = request.POST.get('type')
        channel = request.POST.get('channel')
        task = get_object_or_404(Task, task_id=channel)
        task.worker_name = request.POST.get('worker_name')
        store_data(
            task,
            type,
            request.POST.get('data')
        )
        if type == 'job_complete' or type == 'job_failed':
            task.location = 'Non public IP'
            task.completed_at = datetime.datetime.now()

            task.save()
            return HttpResponse('Ok!')
    else:
        return HttpResponseNotFound("This page only supports POST")


def jobs_status(request, job_id):
    if request.method == 'GET':
        task = Task.objects.get(task_id=job_id)
        return JsonResponse(task.current_output, safe=False)
    else:
        return HttpResponseNotFound("This page only supports GET")


def register(request):
    if request.method == 'POST':
        user_form = UserCreationForm(request.POST)
        if user_form.is_valid():
            user_form.save()
            user_data = user_form.cleaned_data
            user = auth.authenticate(username=user_data['username'],
                                     password=user_data['password2'])
            auth.login(request, user)
            return redirect(reverse('index'))
    else:
        user_form = UserCreationForm()

    return render(request, 'registration/register.html', {
        'form': user_form,
    })


@login_required
def settings(request):
    if request.method == 'POST':
        user_form = UserChangePasswordForm(request.POST)
        if user_form.is_valid():
            if request.user.check_password(
                    user_form.cleaned_data['old_password']):
                new_password = user_form.cleaned_data['password1']
                request.user.set_password(new_password)
                request.user.save()
                update_session_auth_hash(request, request.user)
                messages.success(request, 'Password successfully changed')
            else:
                errors = \
                    user_form._errors.setdefault('old_password', ErrorList())
                errors.append('Incorrect Password')
    else:
        user_form = UserChangePasswordForm()

    return render(request, 'frontend/settings.html', {
        'form': user_form,
    })
