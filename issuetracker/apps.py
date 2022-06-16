"""Used by Django's project setup procedure."""

from django.apps import AppConfig


class IssuetrackerConfig(AppConfig):
    """
    Even before loading the urls, the application server of the project
    needs to know which apps are contained in the project. To do so,
    it needs an AppConfig instance from each of the apps. Those will then
    be stored behind the scenes in an instance of the Apps class called the
    master registry.
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'issuetracker'
