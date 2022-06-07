from django.contrib.auth.models import User
from .models import Projects, Issues, Comments, Contributors
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import password_validation


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
    class Meta:
        model = Projects
        fields = ["title", "description", "type"]


class ContributorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contributors
        # the user should enter the username and the app should
        # find the user_id. Same for the project_id.
        fields = ["permission", "user_id", "project_id"]


class IssueSerializer(serializers.ModelSerializer):
    class Meta:
        model = Issues
        # author_user_id should be auto filled.
        # the user should enter the project title and the project_id should
        # be filled by the app.
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
        model = Comments
        fields = ["description", "author_user_id", "issue_id"]
