from django.http import HttpRequest, HttpResponse
from django.views.decorators.http import require_http_methods
from django.shortcuts import render, redirect
from django.contrib.auth import login as login_user
from django.contrib.auth import logout as logout_user
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.contrib.auth import authenticate

@require_http_methods(['POST', 'GET'])
def login(request: HttpRequest) -> HttpResponse:
    if request.method == 'POST':
        # the user submitted the form so try to login them in
        # Check if user exists
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login_user(request, user)
            messages.success(request, ("Login Successful"), extra_tags="alert-success")
            return redirect('index')

        messages.error(request, ("Login Failed"), extra_tags="alert-danger")

        return redirect('login')

    # user is just getting the login page
    return render(request, 'login.html')



def register(request: HttpRequest) -> HttpResponse:
    if request.method == 'POST':
        # the user sumbimitted the form so register them

        password1 = request.POST['password1']
        password2 = request.POST['password2']
        try:
            validate_password(password1)
        except ValidationError as err:
            messages.error(request, err.message, extra_tags="alert-danger")
            return render(request, 'register.html')

        if not (password1 == password2):
            messages.error(request, ("Passwords do not match. Please try again."), extra_tags="alert-danger")
            return render(request, 'register.html')
        username = request.POST['username']
        user = User.objects.create_user(username=username, password=password1)
        user = authenticate(username=username, password=password1) 
        if user is not None and user.is_authenticated:
            login_user(request=request, user=user)

        messages.success(request, (f"Registration Successful."), extra_tags="alert-success")
        return redirect('index')

    # user is just getting the page
    return render(request, 'register.html')

def logout(request: HttpRequest) -> HttpResponse:
    logout_user(request)
    return render(request, 'login.html')
