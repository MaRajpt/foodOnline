from django.shortcuts import render, redirect
from .forms import UserForm
from .models import User, UserProfile
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.contrib import messages, auth
from vendor.forms import VendorForm
from .utils import detectUser, send_verification_email
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.exceptions import PermissionDenied
from django.utils.http import urlsafe_base64_decode
from django.contrib.auth.tokens import default_token_generator
from vendor.models import Vendor


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
            mail_subject = 'Please activate your account'
            email_template = 'accounts/emails/account_verification_email.html'
           

              # SEND VERIFICATION EMAIL
            mail_subject = 'Please activate your account'
            email_template = 'accounts/emails/account_verification_email.html'
            send_verification_email(request, user, mail_subject, email_template)

            messages.success(request, 'An account activation email sent to your mail addresss !')

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

            # SEND VERIFICATION EMAIL

            mail_subject = 'Please activate your account'
            email_template = 'accounts/emails/account_verification_email.html'
            send_verification_email(request, user, mail_subject, email_template)
            messages.success(request, 'An account activation email sent to your mail addresss !')
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



def activate(request, uidb64, token):
    # Activate the userb by setting the is_active status to True
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User._default_manager.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, 'Congratulation Your account is activated')
        return redirect('myAccount')
    else:
        messages.error(request, 'Invalid activation link')
        return redirect('myAccount')


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

# ALTHOUGH WE ARE USING HELPER FUNCTION IN UTILS TO DIFFERENCIATE THE CUSTOMER AND VENDOR HOWEVER TO ELEMINATE THE CROSSDASHBOARD MANUALY WE USING DECORATOR user_passes_test WITH
# FUNCTION check_role_customer , check_role_vendor

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


def forgot_password(request):
    if request.method == 'POST':
        email = request.POST['email']
        print(email)

        if User.objects.filter(email=email).exists():
            user = User.objects.get(email__exact=email)
            # reset password through email
            mail_subject = 'Reset Your Password'
            email_template = 'accounts/emails/reset_password_email.html'
            send_verification_email(request, user, mail_subject, email_template)
            messages.success(request, 'Password reset link has been sent to your email address')
        else:
            messages.error(request, 'Account does not exist')
            return redirect('forgot_password')


    return render(request, 'accounts/forgot_password.html')


def reset_password_validate(request, uidb64, token):
    # validate the user by decoding the token and user pk
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User._default_manager.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        #  storing uid in session so password can be reset
         request.session['uid'] = uid
         messages.info(request, 'Please reset your password')

         return redirect('reset_password')
    else:
        messages.error(request, 'This link has been expired')
        return redirect('myAccount')
    
def reset_password(request):
    if request.POST:
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']
        if password == confirm_password:
            pk = request.session.get('uid')
            user = User.objects.get(pk=pk)
            user.set_password(password)
            user.is_active = True
            user.save()
            messages.success(request, 'Password reset successful')
            return redirect('login')
        else:
            messages.error(request, 'Passwords do not match !')
            return redirect('reset_password')
    return render(request, 'accounts/reset_password.html')
                                    