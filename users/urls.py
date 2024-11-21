from django.urls import path
from users.views import *


urlpatterns = [
    path('login/', UserLoginAPIView.as_view(), name='login'),
    path("logout/", CustomLogoutView.as_view(), name="knox_logout"),
    path("user-change-password/",UserPasswordChangeApiView.as_view(),name="password-change",),
    path('register/', RegisterView.as_view(), name='register'),
    path('userlogin/', LoginView.as_view(), name='login'),
    path('addaddress/', AddressCreateView.as_view(), name='login'),
    
    path('request-password-reset/', RequestPasswordResetView.as_view(), name='request-password-reset'),
    path('verify-otp-and-reset-password/', VerifyOTPAndResetPasswordView.as_view(), name='verify-otp-and-reset-password'),

]