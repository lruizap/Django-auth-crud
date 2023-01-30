from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.utils import timezone
from .forms import TaskForm
from .models import Task

# Create your views here.


def home(request):
    return render(request, 'home.html')


def signup(request):

    if request.method == 'POST':
        try:
            if request.POST['password1'] == request.POST['password2']:
                # register user
                user = User.objects.create_user(
                    username=request.POST['username'], password=request.POST['password1'])
                user.save()
                login(request, user)
                return redirect('tasks')
        except IntegrityError:
            return render(request, 'form/signup.html', {
                'form': UserCreationForm,
                'error': 'El usuario ya existe'
            })
        else:
            return render(request, 'form/signup.html', {
                'form': UserCreationForm,
                'error': 'Las contraseñas no coinciden'
            })
    else:
        return render(request, 'form/signup.html', {
            'form': UserCreationForm
        })


@login_required
def signout(request):
    logout(request)
    return redirect('home')


def signin(request):
    if request.method == 'GET':
        return render(request, 'form/signin.html', {
            'form': AuthenticationForm
        })
    else:
        user = authenticate(
            request, username=request.POST['username'], password=request.POST['password'])

        if user is None:
            return render(request, 'form/signin.html', {
                'form': AuthenticationForm,
                'error': 'El usuario o la contraseña son incorrectos'
            })
        else:
            login(request, user)
            return redirect('tasks')


@login_required
def tasks(request):
    tasks = Task.objects.filter(user=request.user, dateCompleted__isnull=True)
    return render(request, 'tasks/tasks.html', {
        'tasks': tasks
    })


@login_required
def tasks_completed(request):
    tasks = Task.objects.filter(
        user=request.user, dateCompleted__isnull=False).order_by('-dateCompleted')
    return render(request, 'tasks/tasks.html', {
        'tasks': tasks
    })


@login_required
def task_detail(request, task_id):
    if request.method == 'GET':
        task = get_object_or_404(Task, pk=task_id, user=request.user)
        form = TaskForm(instance=task)
        return render(request, 'tasks/task_detail.html', {
            'task': task,
            'form': form
        })
    else:
        try:
            task = get_object_or_404(Task, pk=task_id, user=request.user)
            form = TaskForm(request.POST, instance=task)
            form.save()
            return redirect('tasks')
        except ValueError:
            return render(request, 'tasks/task_detail.html', {
                'task': task,
                'form': form,
                'error': 'Error actualizando los datos'
            })


@login_required
def complete_task(request, task_id):
    task = get_object_or_404(Task, pk=task_id, user=request.user)
    if request.method == 'POST':
        task.dateCompleted = timezone.now()
        task.save()
        return redirect('tasks')


@login_required
def create_task(request):
    if request.method == 'GET':
        return render(request, 'tasks/create_task.html', {
            'form': TaskForm
        })
    else:
        try:
            form = TaskForm(request.POST)
            new_task = form.save(commit=False)
            new_task.user = request.user
            new_task.save()
            return redirect('tasks')
        except ValueError:
            return render(request, 'tasks/create_task.html', {
                'form': TaskForm,
                'error': 'Porfavor, introduzca un valor válido'
            })


@login_required
def delete_task(request, task_id):
    task = get_object_or_404(Task, pk=task_id, user=request.user)
    if request.method == 'POST':
        task.delete()
        return redirect('tasks')
