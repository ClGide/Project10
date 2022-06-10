"""
Each URL matches one or multiple endpoints from the specification.
"""

from django.urls import path
from rest_framework import routers
from rest_framework_simplejwt.views import TokenRefreshView

from issuetracker import views

app_name = "issuetracker"

router = routers.DefaultRouter(trailing_slash=False)
# endpoint 1 and 2
router.register("", views.AuthViewSet, basename="auth")

urlpatterns: list[path] = [
    # endpoint 3. Lists all projects in the DB
    path("projects/list_projects",
         views.ListProjectLoggedInUser.as_view()),

    # endpoint 4. Creates new project.
    path("projects/create",
         views.CreateProject.as_view()),

    # endpoint 5, 6, 7. Respectively, retrieves, updates or deletes one
    # project.
    # This URL can be used with three different request methods. Each
    # of those request methods are mapped to a view's method.
    path("projects/<int:pk>",
         views.ProjectViewSet.as_view(
             {"get": "retrieve",
              "put": "update",
              "delete": "destroy"}
         )),

    # endpoint 8. Adds new contributor to a project.
    path("projects/add_user",
         views.AddContributorProject.as_view()),

    # endpoint 9. Lists all project's contributor.
    path("projects/<int:pk>/users",
         views.ListProjectContributors.as_view()),

    # endpoint 10. Deletes one contributor from the project.
    path("projects/<int:project_pk>/users/<int:user_pk>",
         views.DeleteContributorProject.as_view()),


    # endpoint 11, 12. Respectively retrieves all project's issues or
    # adds a new issue.
    path("projects/<int:pk>/issues",
         views.IssueViewSet.as_view(
             {"get": "get",
              "post": "create"}
         )),

    # endpoint 13, 14. Respectively updates or deletes one issue.
    path("projects/issues/<int:pk>",
         views.IssueViewSet.as_view(
             {"put": "update",
              "delete": "destroy"}
         )),

    # endpoint 15, 16. Respectively retrieves all issue's comments or
    # adds a new comment.
    path("projects/issues/<int:pk>/comments",
         views.CommentViewSet.as_view(
             {"get": "get",
              "post": "create"}
         )),

    # endpoint 17, 18. Respectively updates or deletes one comment.
    path("projects/issues/comments/<int:pk>",
         views.CommentViewSet.as_view(
             {"put": "update",
              "delete": "destroy"}
         ),
         name="update/delete issue in a project"),

    # used for testing purposes.
    path('api/token/refresh', TokenRefreshView.as_view(),
         name='token_refresh'),
]

urlpatterns += router.urls
