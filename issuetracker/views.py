from django.contrib.auth.models import User
from rest_framework import generics
from rest_framework import permissions
from .serializers import UserSerializer, ProjectSerializer, ContributorSerializer
from .models import Projects, Contributors
from rest_framework.response import Response


class CreateProject(generics.CreateAPIView):
    serializer_class = ProjectSerializer


class ListProjectLoggedInUser(generics.ListCreateAPIView):
    queryset = Projects.objects.all()
    serializer_class = ProjectSerializer


class GetSpecificProject(generics.RetrieveAPIView):
    serializer_class = ProjectSerializer

    def retrieve(self, request, pk):
        instance = Projects.objects.filter(id=pk)
        serializer = self.get_serializer(instance[0])
        return Response(serializer.data)
