from rest_framework import serializers
from django.contrib.auth.models import User
from datetime import date

from todo_app.models import Project, Task, AssignedUser


class TaskSerializer(serializers.ModelSerializer):
    task_owner = serializers.StringRelatedField(read_only=True)  # Must be __str__ method of Django User class!

    class Meta:
        model = Task
        # fields = "__all__"
        exclude = ('project',)
        extra_kwargs = {
            'task_completed': {"read_only": True},
        }


class AssignUserSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    class Meta:
        model = AssignedUser
        # fields = "__all__"
        exclude = ('project',)


class ProjectSerializer(serializers.ModelSerializer):
    project_owner = serializers.StringRelatedField(read_only=True)
    tasks = TaskSerializer(many=True, read_only=True)
    assigned_users = AssignUserSerializer(many=True, read_only=True)
    # tasks = serializers.HyperlinkedRelatedField(
    #     many=True,
    #     read_only=True,
    #     view_name='task-details'
    # )

    class Meta:
        model = Project
        fields = "__all__"
        extra_kwargs = {
            'project_pct_complete': {"read_only": True},
            'project_no_tasks': {"read_only": True},
            'project_completed': {"read_only": True},
        }

    def validate_project_due_date(self, value):
        if value < date.today():
            raise serializers.ValidationError({"error": "Project Due Date is in the past!"})
        else:
            return value



