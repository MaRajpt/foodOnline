from django.shortcuts import render, redirect
from .forms import UserForm
from .models import User
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.contrib import messages

# Create your views here.

def registerUser(request):
    if request.POST:
        form = UserForm(request.POST)
        if form.is_valid():
            # password need hashing / foodonline 70

            password = form.cleaned_data['password']
            user = form.save(commit=False)
            user.set_password(password)
            user.role = User.CUSTOMER
            form.save()
            messages.success(request, 'Your account has been registered successfully !')
            return redirect('registerUser')
        else:
            form = UserForm(request.POST)
            return render(request, 'accounts/registerUser.html', context)
       
    else:
        form = UserForm()
        context = {
            'form': form
        }
        return render(request, 'accounts/registerUser.html', context)