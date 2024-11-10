from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm, UserChangeForm
from django.contrib import messages
from .forms import userRegistrationForm, userUpdateForm

########## User Registration Function ##########
def userRegistration(request):
    if request.method == 'POST':
        form = userRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'User Registration Successfully!')
            return redirect('login')
    else:
        form = userRegistrationForm()
    return render(request, 'registration.html', {'form': form})


########## User Login Function ##########
def userLogin(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        # Error Messages for 'User is not exists'
        if not User.objects.filter(username=username).exists():
            messages.warning(request, 'User is not exists.')
            return redirect('login')

        user = authenticate(username=username, password=password)

        # Error Messages for Incorrect Password
        if user is None:
            messages.warning(request, 'Incorrect Password')
            return redirect('login')
        else:
            login(request, user)
            messages.success(request, 'User Login Successfully!!!')
            return redirect('login')
    return render(request, 'login.html', {'form': AuthenticationForm})


########## User Logout Function ##########
def userLogout(request):
    logout(request)
    messages.success(request, 'User Logout Successfully!')
    return redirect('login')


########## User Update Function ##########
def userUpdate(request):
    if request.user.is_authenticated:
        if request.method == 'POST':
            form = userUpdateForm(request.POST, instance = request.user)
            if form.is_valid():
                messages.success(request, 'User Update Successfully!')
                form.save()
                return redirect('profile')
        else:
            form = userUpdateForm(instance = request.user)
            return render(request, 'update.html', {'form': form})