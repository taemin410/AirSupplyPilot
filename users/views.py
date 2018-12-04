from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from .forms import TokenForm
from .forms import CustomUserSignUpForm
from rest_framework.authtoken.models import Token
from .models import CustomUser
from django.contrib.auth.forms import AdminPasswordChangeForm
    
def sign_up(request, user):
    user = CustomUser.objects.get(email=user)
    if user.name == "":
        if request.method == 'POST':
            form1 = CustomUserSignUpForm(request.POST, instance=user)
            form2 = AdminPasswordChangeForm(user, request.POST)
            if form1.is_valid() and form2.is_valid():
                form1.save()
                form2.save()
                return redirect('login')
        form1 = CustomUserSignUpForm(instance=user)
        form2 = AdminPasswordChangeForm(user)
        args = {'form1': form1, 'form2': form2}
        return render(request, 'signup.html', args)
    else:
        return redirect('validate_token')

def validate_token(request):
    if request.method == 'POST':
        form = TokenForm(request.POST)
        if form.is_valid():
            token = request.POST.get('token')
            if token in Token.objects.values_list('key', flat=True):
                user = Token.objects.get(key=token).user
                return redirect('signup', user)
    else:
        form = TokenForm()
        return render(request, 'validate_token.html', {'form': form})