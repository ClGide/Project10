"""
Serializers have two main goals. The first is to serialize requested data
from the DB in order to send it through the internet. The second is to
deserialize JSON data received from the user.
"""


from django.contrib.auth import password_validation
from django.contrib.auth.models import User
from django.db.models import Model
from rest_framework import serializers

from .models import Project, Issue, Comment, Contributor


class UserLoginSerializer(serializers.Serializer):
    # Used to validate data
    username = serializers.CharField(max_length=32, required=True)
    password = serializers.CharField(max_length=32,
                                     required=True,
                                     write_only=True)


class UserRegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["username", "first_name", "last_name", "email", "password"]

    @staticmethod
    def validate_password(value):
        # if you define a method named validate_<field_name>,
        # django will use the return value as the value of that
        # field.
        print(f"value in serializer: {value}")
        password_validation.validate_password(value)
        return value


class EmptySerializer(serializers.Serializer):
    pass


class ProjectSerializer(serializers.ModelSerializer):
    """
    The project table contains an author_user_id column that won't
    be filled with user data. Thus, it doesn't need JSON serialization.
    """
    class Meta:
        model: Model = Project
        fields = ["title", "description", "type"]


class ContributorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contributor
        fields = "__all__"


class IssueSerializer(serializers.ModelSerializer):
    """
    The only field that doesn't need JSON serialization is created_time
    because it is automatically filled by Django.
    """
    class Meta:
        model = Issue
        fields = [
            "title", "description",
            "tag", "priority", "status",
            "project_id",
            "author_user_id", "assignee_user_id"
        ]


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        # author_user_id should be auto filled.
        # the user should enter the issue title and the app should
        # find issue_id.
        model = Comment
        fields = ["description", "author_user_id", "issue_id"]
