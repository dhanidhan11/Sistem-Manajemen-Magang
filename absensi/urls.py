from django.urls import path
from . import views

app_name = 'absensi'

urlpatterns = [
    path('', views.absensi_view, name='absensi'),
    path('edit/<int:absensi_id>/', views.absensi_admin_edit, name='absensi_admin_edit'),
]