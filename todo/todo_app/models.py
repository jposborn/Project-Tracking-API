from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator


class Project(models.Model):
    project_owner = models.ForeignKey(User, on_delete=models.CASCADE)
    project_name = models.CharField(max_length=50)
    project_description = models.CharField(max_length=200)
    project_created_date = models.DateField(auto_now_add=True)
    project_pct_complete = models.DecimalField(default=0, max_digits=5, decimal_places=2)
    project_due_date = models.DateField()
    project_no_tasks = models.IntegerField(default=0)
    project_completed = models.BooleanField(default=False)

    def __str__(self):
        return self.project_name


class Task(models.Model):
    task_owner = models.ForeignKey(User, on_delete=models.CASCADE)
    task_name = models.CharField(max_length=50)
    task_notes = models.CharField(max_length=200)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='tasks')
    task_created_date = models.DateField(auto_now_add=True)
    task_last_update = models.DateField(auto_now=True)
    task_pct_complete = models.PositiveIntegerField(validators=[MinValueValidator(0), MaxValueValidator(100)])
    task_due_date = models.DateField()
    task_completed = models.BooleanField(default=False)

    def __str__(self):
        return self.task_name


class AssignedUser(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='assigned_users')
    user = models.CharField(max_length=50)

    def __str__(self):
        return self.user

