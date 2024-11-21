from django.urls import path
from users.views import *


urlpatterns = [
    path('login/', UserLoginAPIView.as_view(), name='login'),
    path("logout/", CustomLogoutView.as_view(), name="knox_logout"),
    path("user-change-password/",UserPasswordChangeApiView.as_view(),name="password-change",),

]