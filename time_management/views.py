import logging
from datetime import timedelta
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from rest_framework import generics, views, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from .models import UserTime
from .serializers import UserSerializer, UserTimeSerializer

# Initialize logger
logger = logging.getLogger(__name__)

# User Registration Endpoint
class RegisterUserView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        logger.info("Attempting to register a new user.")
        response = super().create(request, *args, **kwargs)
        logger.info(f"User '{response.data['username']}' registered successfully.")
        return response

# User Login Endpoint
class LoginUserView(views.APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        logger.info("Login attempt received.")
        username = request.data.get('username')
        password = request.data.get('password')

        if not username or not password:
            logger.warning("Login failed: missing username or password.")
            return Response(
                {"error": "Both username and password are required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        user = authenticate(username=username, password=password)

        if user:
            logger.info(f"User '{username}' authenticated successfully.")
            refresh = RefreshToken.for_user(user)
            user_time = UserTime.objects.get(user=user)
            remaining_time = user_time.remaining_time

            return Response(
                {
                    "success": True,
                    "username": user.username,
                    "remaining_time": str(remaining_time),
                    "access": str(refresh.access_token),
                    "refresh": str(refresh),
                },
                status=status.HTTP_200_OK
            )
        else:
            logger.warning(f"Login failed for username '{username}'. Invalid credentials.")
            return Response(
                {"error": "Invalid username or password."},
                status=status.HTTP_401_UNAUTHORIZED
            )

# User Logout Endpoint
class LogoutUserView(views.APIView):
    def post(self, request):
        logger.info("Logout attempt received.")
        try:
            refresh_token = request.data.get('refresh')
            token = RefreshToken(refresh_token)
            token.blacklist()

            logger.info("User logged out successfully and token revoked.")
            return Response({"success": True, "message": "Logged out successfully and token revoked."}, status=status.HTTP_200_OK)
        except Exception as e:
            logger.warning(f"Logout failed: {e}")
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


# Add minutes bought to user's remaining time
class UserTimeView(views.APIView):
    def patch(self, request, username):
        user = User.objects.get(username=username)
        user_time = user.time
        data = request.data

        if 'add_minutes' in data:
            user_time.add_time(int(data['add_minutes']))
            serializer = UserTimeSerializer(user_time)
            logger.info(f"Added {data['add_minutes']} minutes for user '{username}'.")
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            logger.warning(f"Failed to update time for user '{username}': 'add_minutes' field missing.")
            return Response({'error': 'add_minutes field is required'}, status=status.HTTP_400_BAD_REQUEST)

# Sync User Time
class UpdateUserTimeView(views.APIView):
    def patch(self, request, username):
        logger.info(f"Updating remaining time for user '{username}'.")
        user = User.objects.get(username=username)
        user_time = user.time
        data = request.data

        if 'remaining_time' in data:
            # Convert the incoming seconds to a timedelta
            user_time.remaining_time = timedelta(seconds=int(data['remaining_time']))
            user_time.save()
            serializer = UserTimeSerializer(user_time)
            logger.info(f"Updated remaining time for user '{username}' to {data['remaining_time']} seconds.")
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            logger.warning(f"Failed to update time for user '{username}': 'remaining_time' field missing.")
            return Response({'error': 'remaining_time field is required'}, status=status.HTTP_400_BAD_REQUEST)