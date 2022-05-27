from rest_framework.viewsets import GenericViewSet
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.serializers import ValidationError
from django.contrib.auth import authenticate, logout
from django.core.exceptions import ImproperlyConfigured
from django.db.models.signals import post_save


from .models import Projects, Contributors
from .serializers import EmptySerializer, UserLoginSerializer, AuthUserSerializer, UserRegisterSerializer
from .utils import create_user_account, get_and_authenticate_user


class AuthViewSet(GenericViewSet):
    permission_classes = [AllowAny]
    serializer_class = EmptySerializer
    serializer_classes = {
        "login": UserLoginSerializer,
        "register": UserRegisterSerializer
    }

    @action(methods=['POST'], detail=False)
    def login(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = get_and_authenticate_user(**serializer.validated_data)
        data = AuthUserSerializer(user).data
        return Response(data=data, status=status.HTTP_200_OK)

    @action(methods=['POST'], detail=False)
    def register(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = create_user_account(**serializer.validated_data)
        data = serializer.AuthUserSerializer(user).data
        return Response(data=data, status=status.HTTP_201_CREATED)

    def logout(self, request):
        logout(request)
        data = {"success": "successfully logged out"}
        return Response(data=data, status=status.HTTP_200_OK)

    def get_serializer_class(self):
        # called behind the scenes by self.get_serializer().
        if not isinstance(self.serializer_classes, dict):
            raise ImproperlyConfigured("serializer_classes should be "
                                       "a dict mapping")

        if self.action in self.serializer_classes.keys():
            return self.serializer_classes[self.action]
        return super().get_serializer_class()


"""
class CreateProject(generics.CreateAPIView):
    serializer_class = ProjectSerializer
    http_method_names = ["post"]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(author_user_id=request.user)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data,
                        status=status.HTTP_201_CREATED,
                        headers=headers)


class ListProjectLoggedInUser(generics.ListCreateAPIView):
    queryset = Projects.objects.all()
    serializer_class = ProjectSerializer
    http_method_names = ['get']


class GetSpecificProject(generics.RetrieveAPIView):
    serializer_class = ProjectSerializer
    http_method_names = ['get']

    def retrieve(self, request, pk, **kwargs):
        instance = Projects.objects.filter(id=pk)
        serializer = self.get_serializer(instance[0])
        return Response(serializer.data)


class UpdateProject(generics.UpdateAPIView):
    serializer_class = ProjectSerializer
    http_method_names = ['put']


def model_created(sender, **kwargs):
    # whenever an user creates a project, he becomes the owner of that
    # project. We thus need a contributor instance with owner privileges.
    instance = kwargs["instance"]
    if kwargs["created"]:
        owner = Contributors(
            'owner',
            instance.author_user_id,
            instance)
        owner.save()


post_save.connect(model_created, sender=Projects)
"""

