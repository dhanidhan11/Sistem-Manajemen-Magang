from django.urls import path
from . import views

app_name = 'peserta'

urlpatterns = [
    path('', views.peserta_list, name='peserta_list'),
    path('create/', views.peserta_create, name='peserta_create'),
    path('edit/<int:peserta_id>/', views.peserta_edit, name='peserta_edit'),
    path('delete/<int:peserta_id>/', views.peserta_delete, name='peserta_delete'),
]