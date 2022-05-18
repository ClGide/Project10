from django.contrib.auth.models import User
from .models import Projects, Contributors
from rest_framework import serializers


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["first_name", "last_name", "email"]


class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Projects
        fields = ["title", "description", "type", "author_user_id"]


class ContributorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contributors
        fields = ["user_id", "project_id", "permission"]