from django.contrib import admin
from todo_app.models import Project, Task, AssignedUser

# Register your models here.
admin.site.register(Project)
admin.site.register(Task)
admin.site.register(AssignedUser)
