from django.urls import path
from account.views import *

urlpatterns = [
    
    path("registration",SignUpView.as_view(),name='registration'),
    path('otpverify',OtpVerificationView.as_view(),name='otpverify'),
    path('login',LoginView.as_view(),name='loginpage'),
    path('logout',SignOutView.as_view(),name='logout'),
    path('profile', ProfileView.as_view(), name='profile'),
    path('edit-profile', EditProfileView.as_view(), name='edit_profile'),
    path('change-email-otp', ChangeEmailOtpView.as_view(), name='change_email_otp'),
    path('resend-otp', ResendOtpView.as_view(), name='resendotp'),
]