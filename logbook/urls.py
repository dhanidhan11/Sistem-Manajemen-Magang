from django.urls import path
from . import views

app_name = 'logbook'

urlpatterns = [
    path('', views.logbook_list, name='logbook_list'),
    path('create/', views.logbook_create, name='logbook_create'),
    path('mentor/', views.logbook_mentor, name='logbook_mentor'),
    path('verify/<int:logbook_id>/', views.logbook_verify, name='logbook_verify'),
    path('edit/<int:pk>/', views.logbook_edit, name='logbook_edit'),
]