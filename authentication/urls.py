from django.urls import path
from .views import userRegistration, userLogin, userLogout, userUpdate

urlpatterns = [
    path('register/', userRegistration, name = 'register'),
    path('login/', userLogin, name = 'login'),
    path('logout/', userLogout, name = 'logout'),
    path('user_update/', userUpdate, name = 'update'),
]