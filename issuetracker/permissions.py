"""
The project defines four levels of permissions. The first one is AllowAny
(e.g. register must be available to all users, including unauthenticated ones).
The second one is IsAuthenticated. It's the default we set in
softdesk.settings.py. (e.g. all authenticated users have read and create access
to the Project table).
The two other levels are defined in this module.
"""


from rest_framework.exceptions import PermissionDenied
from issuetracker.models import Contributor


def only_obj_author_permission(request, obj):
    """
    Returns None when the user making the request is the author of the
    given instance model. Otherwise raises PermissionDenied.
    """
    if obj.author_user_id != request.user:
        raise PermissionDenied


def only_project_contributor_permission(request, project_id):
    """
    Returns None when the user making the request is in the given project's
    list of contributors. Otherwise raises PermissionDenied.
    """
    contributors = Contributor.objects.filter(
        project_id=project_id
    )
    contributors_user = [contributor.user_id for contributor in
                         contributors]
    if request.user not in contributors_user:
        raise PermissionDenied
