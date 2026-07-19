from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    path('', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),  # <-- Pastikan ini ada
    path('dashboard/admin/', views.dashboard_admin, name='dashboard_admin'),
    path('dashboard/mentor/', views.dashboard_mentor, name='dashboard_mentor'),
    path('dashboard/peserta/', views.dashboard_peserta, name='dashboard_peserta'),
    
    # Kelola Mentor oleh Admin
    path('mentors/', views.mentor_list, name='mentor_list'),
    path('mentors/create/', views.mentor_create, name='mentor_create'),
    path('mentors/edit/<int:mentor_id>/', views.mentor_edit, name='mentor_edit'),
    path('mentors/delete/<int:mentor_id>/', views.mentor_delete, name='mentor_delete'),

    # Edit Profil User
    path('profile/', views.profile_edit, name='profile_edit'),
    
    # Registrasi Peserta
    path('register/', views.register_peserta, name='register'),
    
    # Verifikasi oleh Mentor
    path('verification/', views.mentor_verification, name='mentor_verification'),
    path('verification/approve/<int:pk>/', views.mentor_approve_peserta, name='mentor_approve'),
    path('verification/reject/<int:pk>/', views.mentor_reject_peserta, name='mentor_reject'),
]