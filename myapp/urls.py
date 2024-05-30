from django.urls import path
from .import views

urlpatterns = [
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('upload/', views.upload_view, name='upload'),
    path('graphical/', views.graphical_view, name='graphical'),
    path('files/', views.list_files_view, name='list_files'),
]
