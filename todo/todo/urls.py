from django.contrib import admin
from django.urls import path, include


urlpatterns = [
    path('admin/', admin.site.urls),
    path('projects/', include('todo_app.urls')),
    path('accounts/', include('user_app.urls'))
   # path('api-auth', include('rest_framework.urls')),
]
