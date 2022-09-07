from todo_app.models import Project, Task


def update_project_fields(project_pk):
    project = Project.objects.get(pk=project_pk)

    # Check if number of tasks in a project
    if project.project_no_tasks <= 0:
        project.project_pct_complete = 0
        project.save()
        return

    # Loop through tasks to determine total percent complete and calculate average
    project_pct_complete = 0
    for task in Task.objects.filter(project=project_pk):
        project_pct_complete = project_pct_complete + task.task_pct_complete
    project.project_pct_complete = project_pct_complete / project.project_no_tasks

    # set project completed flag
    if project.project_pct_complete == 100:
        project.project_completed = True
    else:
        project.project_completed = False
    project.save()
    return

# Set task completed flag
def update_task_fields(task):
    if task.task_pct_complete == 100:
        task.task_completed = True
    else:
        task.task_completed = False
    task.save()

