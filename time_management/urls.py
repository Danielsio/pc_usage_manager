from django.urls import path
from .views import RegisterUserView, UserTimeView, UpdateUserTimeView, LoginUserView, LogoutUserView
from rest_framework_simplejwt.views import ( TokenObtainPairView, TokenRefreshView, )

urlpatterns = [
    path('register/', RegisterUserView.as_view(), name='register'),
    path('login/', LoginUserView.as_view(), name='login'),
    path('logout/', LogoutUserView.as_view(), name='logout'),
    path('users/<str:username>/time/', UserTimeView.as_view(), name='user-time'),
    path('users/<str:username>/time/update/', UpdateUserTimeView.as_view(), name='update-user-time'),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
