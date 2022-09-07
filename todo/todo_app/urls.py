from django.urls import path
from todo_app.views import TaskList, TaskDetail, ProjectList, ProjectDetail, TaskCreate, AssignUser, RemoveAssigned

urlpatterns = [
    # path('task/list/', TaskList.as_view(), name='task-list'),

    path('list/', ProjectList.as_view(), name='project-list'),
    path('<int:pk>/', ProjectDetail.as_view(), name='project-details'),
    path('<int:pk>/assign/', AssignUser.as_view(), name='assign-user'),
    path('<int:pk>/remove-assigned/', RemoveAssigned.as_view(), name='assign-user'),

    path('task/<int:pk>/', TaskDetail.as_view(), name='task-details'),
    path('<int:pk>/task-create/', TaskCreate.as_view(), name='task-create'),
    path('<int:pk>/tasks/', TaskList.as_view(), name='task-list'),

]
