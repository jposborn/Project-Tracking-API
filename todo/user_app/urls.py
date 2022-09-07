from rest_framework.authtoken.views import obtain_auth_token
from django.urls import path
from user_app.views import registation_view, logout_view
urlpatterns = [

    path('login/', obtain_auth_token, name='login'),
    path('register/', registation_view, name='register'),
    path('logout/', logout_view, name='logou'),
]
