from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from rest_framework import serializers


def get_and_authenticate_user(username, password):
    user = authenticate(username=username, password=password)
    if user is None:
        raise serializers.ValidationError(
            "invalid username/password. Please try again!"
        )
    return user


def create_user_account(username, email, password, first_name="",
                        last_name=""):
    user = User.objects.create_user(
        username,
        first_name=first_name,
        last_name=last_name,
        email=email,
        password=password,
    )
    return user
