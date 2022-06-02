""" softdesk URL Configuration."""


from django.urls import path
from issuetracker import views
from rest_framework import routers
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView
)
from rest_framework.authtoken.views import obtain_auth_token


app_name = "issuetracker"

router = routers.DefaultRouter(trailing_slash=False)
# endpoint 1 and 2
router.register("", views.AuthViewSet, basename="auth")


urlpatterns: list[path] = [
    # I named the two below endpoints in a different manner for ease.
    # However, later I'll have to create a single view that handles the
    # post and get methods AND a single path that routes both types of
    # requests. The problem with two urls having the same name is that
    # the rest framework always only checks the first. Thus, if the
    # first one handles the GET method and the second one the POST
    # method, the POST method will never be handled.

    # endpoint 3
    path("projects/list_projects",
         views.ListProjectLoggedInUser.as_view(),
         name="projects"),

    # endpoint 4
    path("projects/create",
         views.CreateProject.as_view(),
         name="create project"),

    # endpoint 5, 6, 7
    path("projects/<int:pk>",
         views.GetProject.as_view(
             {"get": "retrieve",
              "put": "update",
              "delete": "destroy"}
         ),
         name="get/update/delete project"),

    # endpoint 8
    path("projects/add_user",
         views.AddContributorProject.as_view(),
         name="Add collaborator to a project"),

    # endpoint 9
    path("projects/<int:pk>/users",
         views.ListProjectCollaborators.as_view(),
         name="list all collaborators in Project"),

    # endpoint 10
    path("projects/<int:project_pk>/users/<int:user_pk>",
         views.DeleteContributorProject.as_view(),
         name="delete a collaborator from a project"),

    # endpoint 11, 12, 13, 14
    path("projects/<int:pk>/issues",
         views.GetIssue.as_view(
            {"get": "get",
             "post": "create"}
         ),
         name="get issues from a project/create issue"),
    path("projects/issues/<int:pk>",
         views.GetIssue.as_view(
            {"put": "update",
             "delete": "destroy"}
         ),
         name="update/delete issue in a project"),

    # endpoint 15, 16, 17, 18
    path("projects/issues/<int:pk>/comments",
         views.GetComment.as_view(
             {"get": "get",
              "post": "create"}
         ),
         name="get issues from a project/create issue"),
    path("projects/issues/comments/<int:pk>",
         views.GetComment.as_view(
            {"put": "update",
             "delete": "destroy"}
         ),
         name="update/delete issue in a project"),

    # jwt tokens
    path('api/token', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/token/verify', TokenVerifyView.as_view(), name='token_verify')

]

urlpatterns += router.urls
