from django.shortcuts import render,redirect
from django.contrib import messages
from django.views import View
from account.models import *
from account.forms import *
from django.contrib.auth import authenticate,login,logout
from mail_manage.utils import send_account_otp
from product.models import Product

# Create your views here.

from django.db.models import Q
from chat.models import Message, Conversation
from django.utils import timezone

class HomeView(View):
    def get(self, request, *args, **kwargs):
        products = Product.objects.filter(is_sold=False).order_by('-created_at')
        featured_products = Product.objects.filter(is_sold=False, is_boosted=True, boost_expiry__gt=timezone.now()).order_by('-created_at')[:4]
        recent_products = Product.objects.filter(is_sold=False, is_boosted=False).order_by('-created_at')[:12]
        
        category_list = [
            ('mobiles', 'Mobiles', 'smartphone'),
            ('laptops', 'Laptops', 'laptop'),
            ('fashion', 'Fashion', 'shirt'),
            ('cars', 'Cars', 'car'),
            ('bikes', 'Bikes', 'bike'),
            ('electronics', 'Electronics', 'monitor'),
            ('gaming', 'Gaming', 'gamepad'),
            ('camera', 'Camera', 'camera'),
            ('audio', 'Audio', 'headphones'),
            ('watch', 'Watch', 'watch'),
            ('home', 'Home', 'home'),
            ('books', 'Books', 'book-open'),
            ('health', 'Health', 'heart'),
        ]

        unread_count = 0
        if request.user.is_authenticated:
            unread_count = Message.objects.filter(
                Q(conversation__buyer=request.user) | Q(conversation__seller=request.user),
                is_read=False
            ).exclude(sender=request.user).count()
            
        context = {
            'products': products,
            'featured_products': featured_products,
            'recent_products': recent_products,
            'category_list': category_list,
            'unread_count': unread_count,
        }
        return render(request, "home.html", context)

class SignUpView(View):
    def get(self,request):
        data=RegForm()
        return render(request,'signup.html',{'form':data})
    def post(self,request):
        form_data=RegForm(data=request.POST)
        if form_data.is_valid():
            user=form_data.save(commit=False)
            user.is_active=False
            user.is_verified=False
            user.save()
            request.session['pending_otp_user_id'] = user.id  # Store for resend
            if send_account_otp(user):
                messages.success(request, "OTP sent to your email. Please verify your account.")
                return redirect('otpverify')
            else:
                messages.error(request, "Account created, but email failed. Please contact support.")
                return redirect('otpverify')
        return render(request,'signup.html',{'form':form_data})

class LoginView(View):
    def get(self,request):
        forms=LoginForm()
        return render(request,'login.html',{'form':forms})
    def post(self,request):
        data_form=LoginForm(data=request.POST)
        if data_form.is_valid():
            email=data_form.cleaned_data.get('email')
            password=data_form.cleaned_data.get('password')
            # Use username=email to ensure compatibility with most backends
            user=authenticate(request,username=email,password=password)
            
            if user:
                if not user.is_verified:
                    request.session['pending_otp_user_id'] = user.id
                    send_account_otp(user) # Auto-resend
                    messages.warning(request, 'Account not verified. A fresh OTP has been sent to your email.')
                    return redirect('otpverify')
                
                login(request,user)
                messages.success(request,'Login Successful. Welcome back!')
                if user.is_superuser:
                    return redirect('custom_admin:dashboard')
                return redirect('home')
            else:
                messages.warning(request,'Invalid email or password.')
                return redirect('loginpage')
        
        # If form is invalid, show specific errors
        for field, errors in data_form.errors.items():
            for error in errors:
                messages.error(request, f"{field.title()}: {error}")
        return redirect('loginpage')
            
    
class OtpVerificationView(View):
    def get(self,request):
        return render(request,'otp_verify.html')
    def post(self,request):
        otpvl=request.POST.get('otpnum')
        try:
            user_instance=User.objects.get(otp=otpvl)
            user_instance.is_verified=True
            user_instance.is_active=True
            user_instance.otp=None
            user_instance.save()
            
           
            if 'pending_otp_user_id' in request.session:
                del request.session['pending_otp_user_id']
                
            messages.success(request,'Verification Successful! Your account is now active.')
            return redirect('loginpage')
        except User.DoesNotExist:
            messages.error(request, 'Invalid OTP. Please try again.')
            return redirect('otpverify')
        except Exception as e:
            messages.error(request, 'Verification error. Please try again.')
            return redirect('otpverify')

class ResendOtpView(View):
    def get(self, request):
        user_id = request.session.get('pending_otp_user_id')
        if not user_id:
            messages.error(request, "Session expired or invalid access. Please try logging in again.")
            return redirect('loginpage')
            
        try:
            user = User.objects.get(id=user_id)
            if user.is_verified:
                messages.info(request, "Your account is already verified. Please log in.")
                return redirect('loginpage')
                
            if send_account_otp(user):
                messages.success(request, "A fresh verification code has been dispatched to your email.")
            else:
                messages.error(request, "Failed to send OTP. Please check your connection or try again later.")
            return redirect('otpverify')
        except User.DoesNotExist:
            messages.error(request, "User context lost. Please try logging in again.")
            return redirect('loginpage')

class SignOutView(View):
    def get(self, request):
        logout(request)
        return redirect('home')

class ProfileView(View):
    def get(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('loginpage')
        UserProfile.objects.get_or_create(user=request.user)
        return render(request, "user_profile.html")

class EditProfileView(View):
    def get(self, request):
        UserProfile.objects.get_or_create(user=request.user)
        user_form = UserUpdateForm(instance=request.user)
        profile_form = UserProfileForm(instance=request.user.userprofile)
        return render(request, 'edit_profile.html', {
            'user_form': user_form,
            'profile_form': profile_form
        })
    def post(self, request):
        user_form = UserUpdateForm(request.POST, instance=request.user)
        profile_form = UserProfileForm(request.POST, request.FILES, instance=request.user.userprofile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('profile')
        return render(request, 'edit_profile.html', {
            'user_form': user_form,
            'profile_form': profile_form
        })
    
# create superuser

from django.http import HttpResponse
from django.contrib.auth import get_user_model

def create_superuser(request):
    User = get_user_model()

    if not User.objects.filter(email="admin@gmail.com").exists():
        User.objects.create_superuser(
            email="admin@gmail.com",
            password="admin123"
        )
        return HttpResponse("Superuser created")

    return HttpResponse("Superuser already exists")