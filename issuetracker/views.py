from rest_framework.viewsets import GenericViewSet
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import generics
from django.contrib.auth import authenticate, logout
from django.contrib.auth.models import User
from django.core.exceptions import ImproperlyConfigured

from .models import Projects, Contributors, Issues, Comments
from .serializers import EmptySerializer, UserLoginSerializer, CommentSerializer, AuthUserSerializer, UserRegisterSerializer
from .serializers import IssueSerializer, ContributorSerializer, ProjectSerializer
from .utils import create_user_account, get_tokens_for_user


class AuthViewSet(GenericViewSet):
    permission_classes = [AllowAny]
    serializer_class = EmptySerializer
    serializer_classes = {
        "login": UserLoginSerializer,
        "register": UserRegisterSerializer
    }

    @action(methods=['POST'], detail=False)
    def login(self, request):
        # actions may be intended either for a single obj or the entire
        # collection. If it's intended for a single obj, set detail to
        # true, define the pk arg and use it to make the query.
        # Note that without action our method wouldn't be routable.
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        print(f"this serializer:{serializer.validated_data}")
        user = authenticate(request, **serializer.validated_data)
        auth_serializer = AuthUserSerializer(user)
        token = get_tokens_for_user(user)
        data = {"user_data": auth_serializer.data,
                "token": token}
        return Response(data=data, status=status.HTTP_200_OK)

    @action(methods=['POST'], detail=False)
    def register(self, request):
        print(f"user")
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = create_user_account(**serializer.validated_data)
        auth_serializer = AuthUserSerializer(user)
        return Response(data=auth_serializer.data,
                        status=status.HTTP_201_CREATED)

    @action(methods=['POST'], detail=False)
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


class ListProjectLoggedInUser(generics.ListCreateAPIView):
    queryset = Projects.objects.all()
    serializer_class = ProjectSerializer
    http_method_names = ['get']


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


class GetProject(GenericViewSet):
    serializer_class = ProjectSerializer
    http_method_names = ['get', 'put', 'delete']

    def retrieve(self, request, *args, **kwargs):
    # Although some args aren't used in the method body, I need to
    # declare them. The methods of this class are generic methods.
    # Thus, I do not completely control how they're called by Django
        pk = kwargs["pk"]
        project = Projects.objects.get(id=pk)
        serializer = self.get_serializer(project)
        return Response(serializer.data)

    def update(self, request, *args, **kwargs):
        pk = kwargs["pk"]
        project = Projects.objects.get(id=pk)
        serializer = self.serializer_class(project, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        if getattr(project, "_prefetched_objects_cache", None):
        # If 'prefetch_related' has been applied to a queryset, we need to
        # forcibly invalidate the prefetch cache on the instance.
            project._prefetched_object_cache = {}
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        pk = kwargs["pk"]
        project = Projects.objects.get(id=pk)
        project.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class AddContributorProject(generics.CreateAPIView):
    serializer_class = ContributorSerializer
    http_method_names = ["post"]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        username = request.data["username"]
        project_title = request.data["project_title"]
        # I need to make sure username is unique. But I think that's
        # the default. Same for the project title.
        user = User.objects.get(username=username)
        project = Projects.objects.get(title=project_title)
        serializer.initial_data["user_id"] = user.id
        serializer.initial_data["project_id"] = project.id
        serializer.is_valid(raise_exception=True)
        serializer.save()
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data,
                        status=status.HTTP_201_CREATED,
                        headers=headers)


class ListProjectCollaborators(APIView):
    http_method_names = ["get"]

    def get(self, request, *args, **kwargs):
        pk = kwargs["pk"]
        queryset = Contributors.objects.filter(project_id=pk)
        serializer = ContributorSerializer(queryset, many=True)
        return Response(serializer.data)


class DeleteContributorProject(generics.DestroyAPIView):
    http_method_names = ["delete"]

    def destroy(self, request, *args, **kwargs):
        project_id = kwargs["project_pk"]
        user_id = kwargs["user_pk"]
        project = Contributors.objects.get(user_id=user_id,
                                           project_id=project_id)
        project.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class GetIssue(GenericViewSet):
    serializer_class = CommentSerializer
    http_method_names = ['get', 'post', 'put', 'delete']

    def get(self, request, *args, **kwargs):
        pk = kwargs["pk"]
        queryset = Issues.objects.filter(project_id=pk)
        serializer = self.serializer_class(queryset, many=True)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        pk = kwargs["pk"]
        assignee_username = request.data["assignee_username"]
        assignee_user = User.objects.get(username=assignee_username)
        serializer.initial_data["project_id"] = pk
        serializer.initial_data["author_user_id"] = request.user.id
        serializer.initial_data["assignee_user_id"] = assignee_user.id
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data,
                        status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        pk = kwargs["pk"]
        issue = Issues.objects.get(id=pk)
        serializer = self.serializer_class(issue, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        if getattr(issue, "_prefetched_objects_cache", None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            issue._prefetched_object_cache = {}
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        pk = kwargs["pk"]
        issue = Issues.objects.get(id=pk)
        issue.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class GetComment(GenericViewSet):
    serializer_class = CommentSerializer
    http_method_names = ['get', 'post', 'put', 'delete']

    def get(self, request, *args, **kwargs):
        pk = kwargs["pk"]
        queryset = Comments.objects.filter(issue_id=pk)
        serializer = self.serializer_class(queryset, many=True)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        pk = kwargs["pk"]
        serializer.initial_data["issue_id"] = pk
        serializer.initial_data["author_user_id"] = request.user.id
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data,
                        status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        pk = kwargs["pk"]
        comment = Comments.objects.get(id=pk)
        serializer = self.serializer_class(comment, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        if getattr(comment, "_prefetched_objects_cache", None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            comment._prefetched_object_cache = {}
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        pk = kwargs["pk"]
        comment = Comments.objects.get(id=pk)
        comment.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
