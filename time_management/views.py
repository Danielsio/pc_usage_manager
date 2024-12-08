from rest_framework import generics, views, status
from rest_framework.response import Response
from django.contrib.auth.models import User
from datetime import timedelta
from .models import UserTime
from .serializers import UserSerializer, UserTimeSerializer

# User Registration Endpoint
class RegisterUserView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer

# Retrieve or Update Remaining Time for a User
class UserTimeView(views.APIView):
    def get(self, request, username):
        try:
            user = User.objects.get(username=username)
            user_time = UserTime.objects.get(user=user)
            serializer = UserTimeSerializer(user_time)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except (User.DoesNotExist, UserTime.DoesNotExist):
            return Response({'error': 'User or time not found'}, status=status.HTTP_404_NOT_FOUND)

    def patch(self, request, username):
        try:
            user = User.objects.get(username=username)
            user_time = UserTime.objects.get(user=user)
            data = request.data
            if 'add_minutes' in data:
                user_time.add_time(int(data['add_minutes']))
                user_time.save()
                serializer = UserTimeSerializer(user_time)
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response({'error': 'add_minutes field is required'}, status=status.HTTP_400_BAD_REQUEST)
        except (User.DoesNotExist, UserTime.DoesNotExist):
            return Response({'error': 'User or time not found'}, status=status.HTTP_404_NOT_FOUND)


class UpdateUserTimeView(views.APIView):
    """Handles updating remaining time."""

    def patch(self, request, username):
        """Update the remaining time for a user."""
        try:
            user = User.objects.get(username=username)
            user_time = UserTime.objects.get(user=user)
            data = request.data

            if 'remaining_time' in data:
                # Convert the incoming seconds to a timedelta
                user_time.remaining_time = timedelta(seconds=int(data['remaining_time']))
                user_time.save()
                serializer = UserTimeSerializer(user_time)
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response({'error': 'remaining_time field is required'}, status=status.HTTP_400_BAD_REQUEST)
        except (User.DoesNotExist, UserTime.DoesNotExist):
            return Response({'error': 'User or time not found'}, status=status.HTTP_404_NOT_FOUND)

