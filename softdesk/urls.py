""" softdesk URL Configuration.


from django.urls import path
from issuetracker import views
from rest_framework import routers

"""
app_name = "issuetracker"

urlpatterns = []

"""

router = routers.DefaultRouter(trailing_slash=False)
router.register("", views.AuthViewSet, basename="")


urlpatterns: list[path] = [
    # I named the two below endpoints in a different manner for ease.
    # However, later I'll have to create a single view that handles the
    # post and get methods AND a single path that routes both types of
    # requests. The problem with two urls having the same name is that
    # the rest framework always only checks the first. Thus, if the
    # first one handles the GET method and the second one the POST
    # method, the POST method will never be handled.

    path("projects/create/",
         views.CreateProject.as_view(),
         name="create project"),
    path("projects/list_projects/",
         views.ListProjectLoggedInUser.as_view(),
         name="list all projects"),
    path("projects/<int:pk>/",
         views.GetSpecificProject.as_view(),
         name="retrieve specific project"),
    path("projects/<int:pk>/",
         views.UpdateProject.as_view(),
         name="update specific project")
]

urlpatterns += router.urls

endpoints: 1, 2, 3, 4, 5, 
"""
