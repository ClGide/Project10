from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save


class Projects(models.Model):
    title = models.CharField(blank=False, max_length=128)
    description = models.CharField(blank=False, max_length=512)
    type = models.CharField(blank=False, max_length=32)
    author_user_id = models.ForeignKey(User, on_delete=models.CASCADE)


class Contributors(models.Model):
    """
    It seems that, for safety reasons, the best is for permissions
    to be automatically set behind the curtains based on the role of
    the contributor.
    I haven't used the role field because I do not understand its use.
    It seems to duplicate permissions.
    """
    # he can delete and modify the users list, create Issues
    PROJECT_OWNER = ""
    # read_only access to the users list, create Issues
    PROJECT_COLLABORATOR = ""
    PERMISSION_CHOICES = [
        ("owner", PROJECT_OWNER),
        ("collaborator", PROJECT_COLLABORATOR)
    ]
    permission = models.CharField(
        choices=PERMISSION_CHOICES,
        default=PROJECT_COLLABORATOR,
        blank=True,
        null=False,
        max_length=32
    )
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    project_id = models.ForeignKey(Projects, on_delete=models.CASCADE)

    class Meta:
        unique_together = ["user_id", "project_id"]


class Issues(models.Model):
    title = models.CharField(blank=False, max_length=32)
    description = models.CharField(blank=False, max_length=512)
    tag = models.CharField(blank=False, max_length=64)
    priority = models.CharField(blank=False, max_length=64)
    project_id = models.ForeignKey(Projects,
                                   on_delete=models.CASCADE,
                                   blank=True)
    status = models.CharField(blank=False, max_length=64)
    # whenever two fields are related to the same model, there's going to
    # be a conflict in the reversing. In other words, the related_name
    # is set by default twice to the same value and User wouldn't know
    # what to do if we didn't manually set related_name.
    author_user_id = models.ForeignKey(User, on_delete=models.CASCADE,
                                       blank=True,
                                       related_name="author")
    # when for some reason the assignee is deleted, the original author
    # becomes the assignee.
    assignee_user_id = models.ForeignKey(User,
                                         on_delete=models.CASCADE,
                                         default=author_user_id,
                                         related_name="assignee")
    # an issue is bound to be updated. The useful timestamp is thus a
    # time-created one.
    created_time = models.DateTimeField(blank=True, auto_now_add=True)


class Comments(models.Model):
    description = models.CharField(blank=False, max_length=512)
    # a comment is still useful even if the author's account was deleted
    author_user_id = models.ForeignKey(User, on_delete=models.SET_NULL,
                                       null=True)
    issue_id = models.ForeignKey(Issues, on_delete=models.CASCADE, blank=True)
    # a completely modified comment isn't the same. Thus, a last modified
    # timestamps is more adapted.
    created_time = models.DateTimeField(blank=True, auto_now=True)


def model_created(**kwargs):
    # whenever an user creates a project, he becomes the owner of that
    # project. We thus need a contributor instance with owner privileges.
    # Initially, before **kwargs there was a sender arg.
    instance = kwargs["instance"]
    if kwargs["created"]:
        owner = Contributors(
            permission='owner',
            user_id=instance.author_user_id,
            project_id=instance)
        owner.save()


post_save.connect(model_created, sender=Projects)

