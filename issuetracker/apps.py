"""Used by Django's project setup procedure."""

from django.apps import AppConfig


class IssuetrackerConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'issuetracker'
