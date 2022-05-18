"""softdesk URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import include, path
from issuetracker import views

app_name = "issuetracker"

urlpatterns: list[path] = [
    path("api-auth/",
         include("rest_framework.urls", namespace="rest_framework")),
    path("projects/",
         views.ListProjectLoggedInUser.as_view(),
         name="list all projects"),
    path("projects/",
         views.CreateProject.as_view(),
         name="create project"),
    path("projects/<int:pk>",
         views.GetSpecificProject.as_view(),
         name="retrieve specific project"),
]
