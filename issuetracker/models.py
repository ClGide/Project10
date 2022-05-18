from django.db import models
from django.contrib.auth.models import User


class Projects(models.Model):
    title = models.CharField(blank=False, max_length=128)
    description = models.CharField(blank=False, max_length=512)
    type = models.CharField(blank=False, max_length=128)
    author_user_id = models.ForeignKey(User, on_delete=models.CASCADE)


class Contributors(models.Model):
    """
    It seems that, for safety reasons, the best is for permissions
    to be automatically set behind the curtains based on the role of
    the contributor.
    """
    PROJECT_OWNER = 0   # he can delete and modify the users list
    PROJECT_COLLABORATOR = 0    # read_only access to the users list
    PERMISSION_CHOICES = [
        (PROJECT_OWNER, "owner"),
        (PROJECT_COLLABORATOR, "collaborator")
    ]
    permission = models.CharField(
        choices=PERMISSION_CHOICES,
        default=PROJECT_COLLABORATOR,
        blank=True,
        max_length=128
    )
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    project_id = models.ForeignKey(Projects, on_delete=models.CASCADE)
    role = models.CharField(blank=True, null=False, max_length=128)

    def clean(self):
        """For now I won't let the user enter the role, it will be
        automatically set behind the curtains based on the permissions.
        However, later I might go the other way around. More complex
        permissions would be automatically set based on self.role"""
        if self.permission == (self.PROJECT_OWNER, "owner"):
            self.role = "owner"
        else:
            self.role = "collaborator"


class Issues(models.Model):
    title = models.CharField(blank=False, max_length=128)
    description = models.CharField(blank=False, max_length=512)
    tag = models.CharField(blank=False, max_length=512)
    priority = models.CharField(blank=False, max_length=128)
    project_id = models.IntegerField(unique=True)
    status = models.CharField(blank=False, max_length=128)
    author_user_id = models.ForeignKey(User, on_delete=models.CASCADE, blank=True)
    created_time = models.DateTimeField(blank=True)


class Comments(models.Model):
    description = models.CharField(blank=False, max_length=512)
    # a comment is still useful even if the author's account was deleted
    author_user_id = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    issue_id = models.ForeignKey(Issues, on_delete=models.CASCADE)
    created_time = models.DateTimeField(blank=True)
