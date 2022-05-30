from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save


class Projects(models.Model):
    title = models.CharField(blank=False, max_length=128)
    description = models.CharField(blank=False, max_length=512)
    TYPE_CHOICES = [
        ("back end", "back end"),
        ("front end", "front end"),
        ("iOS", "iOS"),
        ("Android", "Android")
    ]
    type = models.CharField(
        choices=TYPE_CHOICES,
        default="back end",
        null=False,
        blank=True,
        max_length=32
    )
    # the author should be set by the app, never by the user.
    author_user_id = models.ForeignKey(User,
                                       editable=False,
                                       null=False,
                                       blank=True,
                                       on_delete=models.CASCADE)


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
    TAG_CHOICES = [
        ("tag", "tag"),
        ("enhancement", "enhancement"),
        ("task", "task")
    ]
    tag = models.CharField(
        choices=TAG_CHOICES,
        default="tag",
        blank=True,
        null=False,
        max_length=64)
    PRIORITY_CHOICES = [
        ("low", "low"),
        ("medium", "medium"),
        ("high", "high")
    ]
    priority = models.CharField(
        choices=PRIORITY_CHOICES,
        default="medium",
        blank=True,
        null=False,
        max_length=64
    )
    project_id = models.ForeignKey(Projects,
                                   on_delete=models.CASCADE,
                                   blank=True)
    STATUS_CHOICES = [
        ("to-do", "to-do"),
        ("in progress", "in progress"),
        ("completed", "completed")
    ]
    status = models.CharField(
        choices=STATUS_CHOICES,
        default="to-do",
        blank=False,
        null=False,
        max_length=64
    )
    # whenever two fields are related to the same model, there's going to
    # be a conflict in the reversing. In other words, the related_name
    # is set by default twice to the same value and User wouldn't know
    # what to do if we didn't manually set related_name.
    # Moreover, this field should never be set by the user. Thus, we set
    # editable to false.
    author_user_id = models.ForeignKey(User,
                                       on_delete=models.CASCADE,
                                       editable=False,
                                       null=False,
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
    # Moreover, below two fields should never be set by the user. Thus, we
    # set editable to false.
    author_user_id = models.ForeignKey(User,
                                       editable=False,
                                       blank=True,
                                       on_delete=models.SET_NULL,
                                       null=True)
    issue_id = models.ForeignKey(Issues,
                                 on_delete=models.CASCADE,
                                 blank=True,
                                 editable=False,
                                 null=False)
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
