from django.shortcuts import render, redirect
from .forms import UserForm
from .models import User, UserProfile
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.contrib import messages
from vendor.forms import VendorForm

# Create your views here.

def registerUser(request):
    if request.POST:
        form = UserForm(request.POST)
        if form.is_valid():
            # password need hashing / foodonline 70

            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            username= form.cleaned_data['username']
            password = form.cleaned_data['password']
            email = form.cleaned_data['email']
            user = User.objects.create_user(first_name=first_name, last_name=last_name, username=username, password=password, email=email)
            user.role = User.CUSTOMER
            user.save()
            messages.success(request, 'Your account has been registered successfully !')
            return redirect('registerUser')
        else:
            form = UserForm(request.POST)
            context = {'form': form}
            return render(request, 'accounts/registerUser.html', context)
       
    else:
        form = UserForm()
        context = {'form': form}
        return render(request, 'accounts/registerUser.html', context)
    

def registerVendor(request):

    if request.POST:
        form_filled = UserForm(request.POST)
        vendor_form_filled = VendorForm(request.POST, request.FILES)
        if form_filled.is_valid() and vendor_form_filled.is_valid():

            first_name = form_filled.cleaned_data['first_name']
            last_name = form_filled .cleaned_data['last_name']
            username= form_filled .cleaned_data['username']
            password = form_filled .cleaned_data['password']
            email = form_filled .cleaned_data['email']
            user = User.objects.create_user(first_name=first_name, last_name=last_name, username=username, password=password, email=email)
            user.role = User.VENDOR
            user.save()
            print('user save')
            vendor = vendor_form_filled.save(commit=False)
            vendor.user = user
            profile = UserProfile.objects.get(user=user)
            vendor.user_profile = profile
            vendor.save()
            messages.success(request, 'Your wonderful restaurant has been registered successfully !')
            return redirect('registerVendor')
        else:

            form = UserForm(request.POST)
            vendor_form = VendorForm(request.POST)
            context = {'form':form, 'vendor_form':vendor_form}
            return render(request, 'accounts/registerVendor.html', context)
        
    form = UserForm()
    vendor_form = VendorForm()
    context = {'form':form, 'vendor_form':vendor_form}
                            
    return render(request, 'accounts/registerVendor.html', context)