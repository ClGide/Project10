from django.contrib.auth.backends import BaseBackend, ModelBackend
from django.contrib.auth.models import User
from django.forms import ValidationError
from rest_framework_simplejwt.authentication import JWTAuthentication


class MyBackEnd(BaseBackend):
    JWT_authenticator = JWTAuthentication()
    django_model_backend = ModelBackend()

    def get_user(self, user_id):
        user = User.objects.filter(id=user_id)
        return user

    def authenticate(self, request, **kwargs):
        # we combine in a less than ideal way the two auth methods.
        # the risk might be that some user logs in with the token of
        # another user. We should add a check => the token should
        # match the user.
        # returning None is equivalent to raising an error.
        # I might check that the user returned by django backend's and
        # the one returned by simple_hwt are the same, but it seems
        # overkill.
        user_returned_by_django_built_in = self.django_model_backend.authenticate(request, **kwargs)
        if user_returned_by_django_built_in is None:
            raise ValidationError("username/password pair do not match.")
        """response = self.JWT_authenticator.authenticate(request)
        if response is None:
            return
        user_returned_by_simple_jwt, token = response
        return user_returned_by_simple_jwt
        """
        return user_returned_by_django_built_in