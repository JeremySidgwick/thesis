# authentication/views.py

from django.contrib.auth import authenticate, login, logout
from django.shortcuts import redirect, render
from django.conf import settings

from crowdsourcing.models import Project, UserProject
from . import forms

def logout_user(request):
    logout(request)
    return redirect('login')

def login_page(request):
    form = forms.LoginForm()
    message = ''
    if request.method == 'POST':
        form = forms.LoginForm(request.POST)
        if form.is_valid():
            user = authenticate(
                username=form.cleaned_data['username'],
                password=form.cleaned_data['password'],
            )
            if user is not None:
                login(request, user)
                return redirect('main_page')
                message = f'Bonjour, {user.username}! Vous êtes connecté.'
            else:
                message = 'Identifiants invalides.'
    return render(
        request, 'login.html', context={'form': form, 'message': message})


def signup_page(request):
    form = forms.SignupForm()
    if request.method == 'POST':
        form = forms.SignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            # auto-login user
            projects = Project.objects.all()
            for i in projects:
                UserProject.objects.create(user=user, project=i,role='manager',last_participation="2000-10-10 10:10")


            login(request, user)
            return redirect(settings.LOGIN_REDIRECT_URL)
    return render(request, 'signup.html', context={'form': form})