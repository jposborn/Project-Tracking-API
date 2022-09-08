from datetime import datetime

from rest_framework import generics
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from todo_app.models import Project, Task, AssignedUser
from todo_app.serializer import TaskSerializer, ProjectSerializer, AssignUserSerializer, TaskDetailSerializer
from todo_app.utils import update_project_fields, update_task_fields
from todo_app.permissions import IsAdminOrReadOnly, IsOwnerOrReadOnly, IsProjectOwner, IsAssignedToProject

from django.contrib.auth.models import User


class TaskCreate(generics.CreateAPIView):
    serializer_class = TaskSerializer
    permission_classes = [IsAssignedToProject]

    def get_queryset(self):
        return Task.objects.all()

    def perform_create(self, serializer):
        project_pk = self.kwargs.get('pk')  # get pk of project passed from url.
        project = Project.objects.get(pk=project_pk)  # set project variable as called project object

        task_due_date = datetime.strptime((self.request.data['task_due_date']), '%Y-%m-%d').date()

        if task_due_date > project.project_due_date or task_due_date < datetime.now().date():
            raise ValidationError(
                {'error': 'The Task due date cannot be before today or later than the project due date'}
                                    )
        elif serializer.validated_data['task_pct_complete'] != 0:
            raise ValidationError({'error': 'Initial Task Complete percentage must be zero'})

        # When overriding create method modified model fields (objects) not in request have to be sent in
        # serializer.save()
        task = serializer.save(project=project, task_owner=self.request.user)
        project.project_no_tasks = project.project_no_tasks + 1
        project.save()
        update_project_fields(task.project.pk)


class ProjectList(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        project = Project.objects.all()
        serializer = ProjectSerializer(project, many=True, context={'request': request})
        return Response(serializer.data)

    def post(self, request):
        serializer = ProjectSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(project_owner=self.request.user)
            return Response(serializer.data)
        else:
            return Response(serializer.errors)


class ProjectDetail(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsProjectOwner]
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer


# class AssignUser(generics.ListCreateAPIView):
#     serializer_class = AssignUserSerializer
#     permission_classes = [IsProjectOwner]
#
#     def get_queryset(self):
#         pk = self.kwargs['pk']
#         return AssignedUser.objects.filter(project=pk)   # Needed to complete create request
#
#     def perform_create(self, serializer):
#         project_pk = self.kwargs.get('pk')
#         project = Project.objects.get(pk=project_pk)
#         new_user = self.request.data['user']
#
#         # User Validation must be in view due custom user field in AssignedUserSerializer
#         if not(User.objects.filter(username=new_user).exists()):
#             raise ValidationError({"error": f"The username {new_user} does not exist"})
#         elif AssignedUser.objects.filter(project=project_pk, user=new_user).exists():
#             raise ValidationError({"error": f"{new_user} is already assigned to the {project.project_name} project"})
#         serializer.save(project=project, user=new_user)


class Assign(APIView):
    permission_classes = [IsProjectOwner]

    def post(self, request, pk):
        serializer = AssignUserSerializer(data=request.data)

        project_pk = self.kwargs.get('pk')
        project = Project.objects.get(pk=project_pk)
        new_user = self.request.data['user']

        if serializer.is_valid():
            # User Validation below  must be in view due custom user field in AssignUserSerializer
            if not (User.objects.filter(username=new_user).exists()):
                return Response({"error": f"The username {new_user} does not exist"}, status=status.HTTP_404_NOT_FOUND)
            elif AssignedUser.objects.filter(project=project_pk, user=new_user).exists():
                return Response({"error": f"{new_user} is already assigned to the {project.project_name} project"},
                                status=status.HTTP_400_BAD_REQUEST
                                )
            serializer.save(project=project, user=new_user)
            return Response(serializer.data)

    def get(self, request, pk):
        print(pk)
        project = AssignedUser.objects.filter(project=pk)
        print(project)
        serializer = AssignUserSerializer(project, many=True)
        return Response(serializer.data)

    def delete(self, request,pk):
        # project_pk = self.kwargs['pk']
        print(pk)
        print(self.request.data['user'])
        user_remove = AssignedUser.objects.filter(project=pk, user=self.request.data['user'])
        print(user_remove)
        if user_remove.exists():
            user_remove.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return Response({"error": "User is not assigned to this project"})


class TaskList(generics.ListAPIView):
    # queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        pk = self.kwargs['pk']  # project pk passed from url
        return Task.objects.filter(project=pk)  # use the selected project as filter for list of tasks


# class TaskDetail(generics.RetrieveUpdateDestroyAPIView):
#     # queryset = Task.objects.all()
#     serializer_class = TaskSerializer
#     permission_classes = [IsOwnerOrReadOnly]
#
#     def get_queryset(self):
#         return Task.objects.all()   # Needed to complete create request??
#
#     def perform_destroy(self, instance):
#         project_pk = instance.project.pk
#         print(instance.project.pk)
#         project = Project.objects.get(pk=project_pk)
#         project.project_no_tasks = project.project_no_tasks - 1
#         project.save()
#         instance.delete()
#         update_project_fields(project_pk)
#
#     def perform_update(self, serializer):
#         task = serializer.save()
#         update_project_fields(task.project.pk)
#         update_task_fields(task)


class TaskDetail(APIView):
    permission_classes = [IsOwnerOrReadOnly]

    def get(self, request, pk):
        task = Task.objects.filter(pk=pk)
        serializer = TaskDetailSerializer(task, many=True)
        return Response(serializer.data)

    def delete(self, request, pk):
        task = Task.objects.get(pk=pk)
        print(task.project)
        task.project.project_no_tasks = task.project.project_no_tasks - 1
        task.project.save()
        task.delete()
        update_project_fields(task.project.pk)
        return Response(status=status.HTTP_204_NO_CONTENT)

    def put(self, request, pk):
        task = Task.objects.get(pk=pk)
        self.check_object_permissions(self.request, task)
        serializer = TaskSerializer(task, data=request.data)
        if serializer.is_valid():
            serializer.save(project=task.project, task_owner=task.task_owner)
        update_project_fields(task.project.pk)
        update_task_fields(task)
        return Response(serializer.data)




