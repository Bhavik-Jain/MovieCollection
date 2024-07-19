from django.urls import path
from .views import UserRegistrationView, UserLoginView, RequestCountView, ResetRequestCountView

urlpatterns = [
    path('register/', UserRegistrationView.as_view(), name='register'),
    path('login/', UserLoginView.as_view(), name='login'),
    path('request-count/', RequestCountView.as_view(), name='request-count'),
    path('request-count/reset/', ResetRequestCountView.as_view(), name='reset-request-count'),
]