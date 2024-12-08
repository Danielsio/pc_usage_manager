from rest_framework import serializers
from django.contrib.auth.models import User
from .models import UserTime

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user

class UserTimeSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField()  # Display username instead of user ID

    class Meta:
        model = UserTime
        fields = ['user', 'remaining_time']
