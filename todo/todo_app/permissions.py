from rest_framework import permissions
from todo_app.models import Project, AssignedUser, Task


# If user is Admin can edit otherwise read only
class IsAdminOrReadOnly(permissions.IsAdminUser):

    def has_permission(self, request, view):  # has_permission  for general access to api
        if request.method in permissions.SAFE_METHODS:  # SAFE_METHODS are Read Only Requests (e.g. GET)
            return True  # Check permissions for read-only request
        else:
            return bool(request.user and request.user.is_staff)   # Check permissions for write request (True/False)


class IsOwnerOrReadOnly(permissions.BasePermission):
    message = 'Permission denied. You must be the task owner, project owner or an admin.'

    def has_permission(self, request, view):  # has_object_permission as refers to specific object access
        if request.method in permissions.SAFE_METHODS or request.user.is_staff:  # SAFE_METHODS are Read Only Requests (e.g. GET)
            print(request.user)
            return True
        else:
            task_pk = view.kwargs['pk']
            task = Task.objects.get(pk=task_pk)
            print(request.user)
            print(task.task_owner)
            print(task.project.project_owner)
            if request.user == task.task_owner or request.user == task.project.project_owner:
                return True
            else:
                return False


class IsProjectOwner(permissions.BasePermission):
    message = 'Permission denied. You must be the project owner or Admin.'

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS or request.user.is_staff:
            return True
        else:
            project_pk = view.kwargs['pk']  # get pk of project passed from url
            project = Project.objects.get(pk=project_pk)
        return request.user == project.project_owner


class IsAssignedToProject(permissions.BasePermission):
    message = 'Permission denied. User not assigned to this project.'

    def has_permission(self, request, view):
        project_pk = view.kwargs['pk']  # get pk of project passed from url
        project = Project.objects.get(pk=project_pk)

        if project.project_owner == request.user:
            return True
        else:
            return AssignedUser.objects.filter(project=project_pk, user=request.user).exists()






