from datetime import datetime

from rest_framework import generics
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from todo_app.models import Project, Task, AssignedUser
from todo_app.serializer import TaskSerializer, ProjectSerializer, AssignUserSerializer
from todo_app.utils import update_project_fields, update_task_fields
from todo_app.permissions import IsAdminOrReadOnly, IsTaskOwnerOrReadOnly, IsProjectOwner, IsAssignedToProject

from django.contrib.auth.models import User


class TaskCreate(generics.CreateAPIView):
    serializer_class = TaskSerializer
    permission_classes = [IsAssignedToProject]

    def get_queryset(self):
        return Task.objects.all()

    def perform_create(self, serializer):
        project_pk = self.kwargs.get('pk')  # get pk of project passed from url
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


class AssignUser(generics.ListCreateAPIView):
    serializer_class = AssignUserSerializer
    permission_classes = [IsProjectOwner]

    def get_queryset(self):
        pk = self.kwargs['pk']
        return AssignedUser.objects.filter(project=pk)   # Needed to complete create request

    def perform_create(self, serializer):
        project_pk = self.kwargs.get('pk')
        project = Project.objects.get(pk=project_pk)
        new_user = self.request.data['user']

        # User Validation must be in view due custom user field in AssignedUserSerializer
        if not(User.objects.filter(username=new_user).exists()):
            raise ValidationError({"error": f"The username {new_user} does not exist"})
        elif AssignedUser.objects.filter(project=project_pk, user=new_user).exists():
            raise ValidationError({"error": f"{new_user} is already assigned to the {project.project_name} project"})
        serializer.save(project=project, user=new_user)


class RemoveAssigned(APIView):
    serializer_class = ProjectSerializer
    permission_classes = [IsProjectOwner]

    def delete(self, request, pk):

        project_pk = self.kwargs['pk']
        print(project_pk)
        print(self.request.data['user'])
        user_remove = AssignedUser.objects.filter(project=project_pk, user=self.request.data['user'])
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


class TaskDetail(generics.RetrieveUpdateDestroyAPIView):
    # queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = [IsTaskOwnerOrReadOnly]
    # permission_classes = [AdminOrReadOnly]

    def get_queryset(self):
        return Task.objects.all()   # Needed to complete create request??

    def perform_destroy(self, instance):
        task_pk = self.kwargs['pk']
        task = Task.objects.get(pk=task_pk)
        project_pk = task.project.pk
        print(task.project.pk)
        project = Project.objects.get(pk=project_pk)
        project.project_no_tasks = project.project_no_tasks - 1
        project.save()
        instance.delete()
        update_project_fields(project_pk)

    def perform_update(self, serializer):
        task = serializer.save()
        serializer.save()
        update_project_fields(task.project.pk)
        update_task_fields(task)



