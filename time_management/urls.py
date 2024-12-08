from django.urls import path
from .views import RegisterUserView, UserTimeView, UpdateUserTimeView

urlpatterns = [
    path('register/', RegisterUserView.as_view(), name='register'),
    path('users/<str:username>/time/', UserTimeView.as_view(), name='user-time'),
    path('users/<str:username>/time/update/', UpdateUserTimeView.as_view(), name='update-user-time'),
]