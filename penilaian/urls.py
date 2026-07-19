from django.urls import path
from . import views

app_name = 'penilaian'

urlpatterns = [
    path('', views.penilaian_list, name='penilaian_list'),
    path('create/<int:peserta_id>/', views.penilaian_create, name='penilaian_create'),
    path('detail/<int:penilaian_id>/', views.penilaian_detail, name='penilaian_detail'),
    path('edit/<int:penilaian_id>/', views.penilaian_edit, name='penilaian_edit'),
]