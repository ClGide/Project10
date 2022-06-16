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
    """
    Ensures user's input is valid. Doesn't ensure the user exists or the
    password's right but only that the input respects some basic constraints.
    """
    username: str = serializers.CharField(max_length=32, required=True)
    password: str = serializers.CharField(max_length=32,
                                          required=True,
                                          write_only=True)


class UserRegisterSerializer(serializers.ModelSerializer):
    """
    Checks that values inputted for user's fields respects minimum constraints.
    """
    class Meta:
        model = User
        fields = ["username", "first_name", "last_name", "email", "password"]

    @staticmethod
    def validate_password(value) -> str:
        # If you define a method named validate_<field_name>,
        # django will use the return value as the value of that
        # field.
        password_validation.validate_password(value)
        return value


class EmptySerializer(serializers.Serializer):
    """
    Used in views.AuthViewSet. The view inherits GenericViewSet, a class that
    requires a serializer_class field. But the logic we used there only uses
    the serializer_classes field. Thus, we needed a serializer that accepts
    nothing to be sure the required field is never used.
    """


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
    """
    The only field that doesn't need JSON serialization is created_time
    because it is automatically filled by Django.
    """
    class Meta:
        model = Comment
        fields = ["description", "author_user_id", "issue_id"]
