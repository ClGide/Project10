"""
Models are Django's Object Relational Mapper. They act as an interface
between the sql tables and the application. Each class is mapped to a table.
Each field is mapped to a table's column and each instance is mapped to a
table's row. Besides the models defined here, django's User built-in model
is used throughout the application.
"""

import datetime

from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save


class Project(models.Model):
    title: str = models.CharField(blank=False, max_length=128)
    description: str = models.CharField(blank=False, max_length=512)
    TYPE_CHOICES = [
        ("back end", "back end"),
        ("front end", "front end"),
        ("iOS", "iOS"),
        ("Android", "Android")
    ]
    type: str = models.CharField(
        choices=TYPE_CHOICES,
        default="back end",
        null=False,
        blank=True,
        max_length=32
    )
    author_user_id: models.Model = models.ForeignKey(User,
                                                     null=False,
                                                     blank=True,
                                                     on_delete=models.CASCADE)


class Contributor(models.Model):
    """
    The permission field isn't useful in the current version of the project.
    The idea behind the specification seems to be that permissions should
    be set based on that field. However, because the permissions hierarchy
    isn't that complex, two simple functions in permissions.py are enough.
    """
    PROJECT_OWNER = ""
    PROJECT_COLLABORATOR = ""
    PERMISSION_CHOICES = [
        ("owner", PROJECT_OWNER),
        ("collaborator", PROJECT_COLLABORATOR)
    ]
    permission: str = models.CharField(
        choices=PERMISSION_CHOICES,
        default=PROJECT_COLLABORATOR,
        blank=True,
        null=False,
        max_length=32
    )
    user_id: models.Model = models.ForeignKey(User, on_delete=models.CASCADE)
    project_id: models.Model = models.ForeignKey(Project, on_delete=models.CASCADE)

    class Meta:
        """An user shouldn't be part of a project twice."""
        unique_together = ["user_id", "project_id"]


class Issue(models.Model):
    title: str = models.CharField(blank=False, max_length=32)
    description: str = models.CharField(blank=False, max_length=512)
    TAG_CHOICES = [
        ("tag", "tag"),
        ("enhancement", "enhancement"),
        ("task", "task")
    ]
    tag: str = models.CharField(
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
    priority: str = models.CharField(
        choices=PRIORITY_CHOICES,
        default="medium",
        blank=True,
        null=False,
        max_length=64
    )
    project_id: models.Model = models.ForeignKey(Project,
                                                 on_delete=models.CASCADE,
                                                 blank=True)
    STATUS_CHOICES = [
        ("to-do", "to-do"),
        ("in progress", "in progress"),
        ("completed", "completed")
    ]
    status: str = models.CharField(
        choices=STATUS_CHOICES,
        default="to-do",
        blank=False,
        null=False,
        max_length=64
    )
    # Whenever two fields are related to the same model, there's going to
    # be a conflict in the reversing. In other words, the related_name
    # is by default set twice to the same value. Thus, User wouldn't know
    # what to do if we didn't manually set related_name.
    author_user_id: models.Model = models.ForeignKey(User,
                                                     on_delete=models.CASCADE,
                                                     null=False,
                                                     blank=True)
    # When the original author becomes the assignee.
    assignee_user_id: models.Model = models.ForeignKey(User,
                                                       on_delete=models.CASCADE,
                                                       default=author_user_id,
                                                       related_name="assignee")
    # An issue is bound to be updated. The useful timestamp is thus a
    # time-created one.
    created_time: datetime.datetime = models.DateTimeField(blank=True,
                                                           auto_now_add=True)


class Comment(models.Model):
    description = models.CharField(blank=False, max_length=512)
    # A comment is still useful even if the author's account was deleted
    author_user_id = models.ForeignKey(User,
                                       blank=False,
                                       on_delete=models.SET_NULL,
                                       null=True)
    issue_id = models.ForeignKey(Issue,
                                 on_delete=models.CASCADE,
                                 blank=False,
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
        owner = Contributor(
            permission='owner',
            user_id=instance.author_user_id,
            project_id=instance)
        owner.save()


post_save.connect(model_created, sender=Project)
