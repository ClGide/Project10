"""
Two utility functions used in the register and login process.
"""

from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import RefreshToken


def create_user_account(username, email, password, first_name="",
                        last_name="") -> User:
    """Takes values for the User's fields and creates the instance."""
    user = User.objects.create_user(
        username,
        first_name=first_name,
        last_name=last_name,
        email=email,
        password=password,
    )
    return user


def get_tokens_for_user(user) -> dict[str, str]:
    """Takes a user instance and returns a refresh and access JWT token."""
    refresh = RefreshToken.for_user(user)

    return {
        "refresh": str(refresh),
        "acess": str(refresh.access_token)
    }