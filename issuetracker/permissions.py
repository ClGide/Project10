from rest_framework.exceptions import PermissionDenied
from issuetracker.models import Contributors


def only_obj_author_permission(request, obj):
    if obj.author_user_id != request.user:
        raise PermissionDenied


def only_project_contributor_permission(request, project_id):
    contributors = Contributors.objects.filter(
        project_id=project_id
    )
    contributors_user = [contributor.user_id for contributor in
                         contributors]
    if request.user not in contributors_user:
        raise PermissionDenied
