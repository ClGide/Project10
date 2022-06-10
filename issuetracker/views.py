"""
The default permission is IsAuthenticated. In other words, all below
serializers will refuse access to unauthenticated users if not explictly
stated otherwise.
"""

from typing import Union

from django.db.models import QuerySet, Model
from django.contrib.auth import authenticate, logout
from django.contrib.auth.models import User
from django.core.exceptions import ImproperlyConfigured
from django.forms import ValidationError
from rest_framework import generics
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.serializers import ModelSerializer
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet

from issuetracker.permissions import only_project_contributor_permission, \
    only_obj_author_permission
from .models import Project, Contributor, Issue, Comment
from .serializers import EmptySerializer, UserLoginSerializer, \
    UserRegisterSerializer, CommentSerializer
from .serializers import IssueSerializer, ContributorSerializer, \
    ProjectSerializer
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

        # validate data
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # checks user exists and has the right password
        username, password = request.data["username"], request.data["password"]
        user = authenticate(username=username, password=password)
        if user is None:
            raise ValidationError("username/password is false")

        # returns JWT token
        tokens = get_tokens_for_user(user)

        return Response(data=tokens, status=status.HTTP_200_OK)

    @action(methods=['POST'], detail=False)
    def register(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = create_user_account(**serializer.validated_data)
        tokens = get_tokens_for_user(user)
        return Response(data=tokens,
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
    """Retrieves and returns all projects from the DB in JSON format."""
    queryset: QuerySet = Project.objects.all()
    serializer_class: ModelSerializer = ProjectSerializer
    http_method_names = ['get']


class CreateProject(generics.CreateAPIView):
    """Deserializes user data and creates row in the project table with it."""
    serializer_class: ModelSerializer = ProjectSerializer
    http_method_names = ["post"]

    def create(self, request, *args, **kwargs) -> Response:
        serializer: ModelSerializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(author_user_id=request.user)

        headers: Union[
            dict[str, str], dict] = self.get_success_headers(serializer.data)

        return Response(serializer.data,
                        status=status.HTTP_201_CREATED,
                        headers=headers)


class ProjectViewSet(GenericViewSet):
    """
    Handles get, put and delete request methods from the same URL.

    Some methods' args aren't used in the method body. However, I need to
    declare them. This class implements generic methods.
    Thus, I do not completely control how they're called by Django.
    """
    serializer_class: ModelSerializer = ProjectSerializer
    http_method_names = ['get', 'put', 'delete']

    def retrieve(self, request, *args, **kwargs) -> Response:
        """
        Retrieves requested project from the DB and returns it in JSON format.
        """
        pk: int = kwargs["pk"]
        project: QuerySet = Project.objects.get(id=pk)
        serializer: ModelSerializer = self.get_serializer(project)
        return Response(serializer.data)

    def update(self, request, *args, **kwargs) -> Response:
        """
        Retrieves the requested project from the DB, makes sure the user has
        update authorization and then use the request data to make the desired
        update.
        """
        pk: int = kwargs["pk"]
        project: QuerySet = Project.objects.get(id=pk)

        only_obj_author_permission(request, project)

        serializer: ModelSerializer = self.serializer_class(project, data=request.data,
                                                            partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        if getattr(project, "_prefetched_objects_cache", None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            project._prefetched_object_cache = {}
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs) -> Response:
        """
        Retrieves the requested project from the DB, makes sure the user has
        delete authorization and then perform deletion.
        """
        pk: int = kwargs["pk"]
        project: QuerySet = Project.objects.get(id=pk)

        only_obj_author_permission(request, project)

        project.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class AddContributorProject(generics.CreateAPIView):
    serializer_class: ModelSerializer = ContributorSerializer
    http_method_names = ["post"]

    def create(self, request, *args, **kwargs) -> Response:
        """
        Uses request data to add a new entry in the Contributor table.
        """
        serializer: ModelSerializer = self.get_serializer(data=request.data)

        username: str = request.data["username"]
        project_title: str = request.data["project_title"]

        # The contributor model has two one-to-many relationships. One with
        # the user model, the other with the project model. The serializer
        # uses ids to establish the relationships. However, because the user
        # isn't supposed to know the ids, he enters the user's username and
        # the project's title and we make a query to retrieve those ids.
        user: User = User.objects.get(username=username)
        project: Project = Project.objects.get(title=project_title)

        serializer.initial_data["user_id"] = user.id
        serializer.initial_data["project_id"] = project.id
        serializer.is_valid(raise_exception=True)
        serializer.save()
        headers: Union[
            dict[str, str], dict] = self.get_success_headers(serializer.data)
        return Response(serializer.data,
                        status=status.HTTP_201_CREATED,
                        headers=headers)


class ListProjectContributors(APIView):
    http_method_names = ["get"]

    def get(self, request, *args, **kwargs) -> Response:
        """
        Based on the given project pk, retrieves all project's contributors.
        """
        pk: int = kwargs["pk"]
        queryset: QuerySet = Contributor.objects.filter(project_id=pk)
        serializer: ModelSerializer = ContributorSerializer(queryset, many=True)
        return Response(serializer.data)


class DeleteContributorProject(generics.DestroyAPIView):
    http_method_names = ["delete"]

    def destroy(self, request, *args, **kwargs) -> Response:
        """
        Based on the given project pk and user pk, retrieves the matching
        contributor instance and deletes it.
        """
        project_id: int = kwargs["project_pk"]
        user_id: int = kwargs["user_pk"]
        project: Project = Contributor.objects.get(user_id=user_id,
                                                   project_id=project_id)
        project.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class IssueViewSet(GenericViewSet):
    serializer_class: ModelSerializer = IssueSerializer
    http_method_names = ['get', 'post', 'put', 'delete']

    def get(self, request, *args, **kwargs) -> Response:
        """
        Based on the given project pk, checks that the user has read access
        to the project's issues and if that's the case, returns the project's
        issues.
        """
        pk: int = kwargs["pk"]

        only_project_contributor_permission(request, pk)

        queryset: QuerySet = Issue.objects.filter(project_id=pk)
        serializer: ModelSerializer = self.serializer_class(queryset,
                                                            many=True)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs) -> Response:
        """
        Based on the given project pk and request data, checks that the user
        has create access to the project's issues and if that's the case,
        performs creation.
        """
        serializer: ModelSerializer = self.serializer_class(data=request.data)
        pk: int = kwargs["pk"]

        only_project_contributor_permission(request, pk)

        assignee_username: str = request.data["assignee_username"]
        assignee_user: User = User.objects.get(username=assignee_username)
        serializer.initial_data["project_id"]: int = pk
        serializer.initial_data["author_user_id"]: int = request.user.id
        serializer.initial_data["assignee_user_id"]: int = assignee_user.id
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data,
                        status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs) -> Response:
        """
        Based on the given issue pk and request data, checks that the user
        has update access to the issue and if that's the case, performs update.
        """
        pk: int = kwargs["pk"]
        issue: Issue = Issue.objects.get(id=pk)

        only_obj_author_permission(request, issue)

        serializer: ModelSerializer = self.serializer_class(
            issue,
            data=request.data,
            partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        if getattr(issue, "_prefetched_objects_cache", None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            issue._prefetched_object_cache = {}
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs) -> Response:
        """
        Based on the given issue pk and request data, checks that the user
        has delete access to the issue and if that's the case,
        performs deletion.
        """
        pk: int = kwargs["pk"]
        issue: Issue = Issue.objects.get(id=pk)

        only_obj_author_permission(request, issue)

        issue.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class CommentViewSet(GenericViewSet):
    serializer_class = CommentSerializer
    http_method_names = ['get', 'post', 'put', 'delete']

    def get(self, request, *args, **kwargs):
        pk = kwargs["pk"]
        only_project_contributor_permission(request, pk)
        queryset = Comment.objects.filter(issue_id=pk)
        serializer = self.serializer_class(queryset, many=True)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        pk = kwargs["pk"]
        only_project_contributor_permission(request, pk)
        serializer.initial_data["issue_id"] = pk
        serializer.initial_data["author_user_id"] = request.user.id
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data,
                        status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        pk = kwargs["pk"]
        comment = Comment.objects.get(id=pk)
        only_obj_author_permission(request, comment)
        serializer = self.serializer_class(comment, data=request.data,
                                           partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        if getattr(comment, "_prefetched_objects_cache", None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            comment._prefetched_object_cache = {}
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        pk = kwargs["pk"]
        comment = Comment.objects.get(id=pk)
        only_obj_author_permission(request, comment)
        comment.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
