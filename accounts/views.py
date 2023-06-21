from django.shortcuts import render, redirect
from .forms import UserForm
from .models import User, UserProfile
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.contrib import messages, auth
from vendor.forms import VendorForm
from .utils import detectUser
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.exceptions import PermissionDenied


# Restrict the vendor access to customer dash board
def check_role_vendor(user):
    if user.role == 1:
        return True
    else:
        raise PermissionDenied


# Restrict the customer access to vendor dash board
def check_role_customer(user):
    if user.role == 2:
        return True
    else:
        raise PermissionDenied


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



def login(request):
    if request.POST:
        email = request.POST['email']
        password = request.POST['password']
        user = auth.authenticate(email=email, password=password)
        if user is not None:
            auth.login(request, user)
            return redirect('myAccount')
        else:
            messages.error(request, 'Invalid login credentials')
            return redirect('login')
    return render(request, 'accounts/login.html')


def logout(request):
    auth.logout(request)
    messages.info(request, 'You have logged out.')
    return redirect('login')


@login_required(login_url='login')
@user_passes_test(check_role_customer)
def customerDashboard(request):
    return render(request, 'accounts/customerDashboard.html')


@login_required(login_url='login')
@user_passes_test(check_role_vendor)
def vendorDashboard(request):
    return render(request, 'accounts/vendorDashboard.html')


@login_required(login_url='login')
def myAccount(request):
    user = request.user
    redirectUrl = detectUser(user)
    return redirect(redirectUrl)

