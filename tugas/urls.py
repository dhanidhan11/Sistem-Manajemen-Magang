from django.urls import path
from . import views

app_name = 'tugas'

urlpatterns = [
    path('mentor/', views.tugas_list_mentor, name='tugas_list_mentor'),
    path('mentor/create/', views.tugas_create, name='tugas_create'),
    path('mentor/delete/<int:pk>/', views.tugas_delete, name='tugas_delete'),
    path('mentor/review/<int:pk>/', views.tugas_review, name='tugas_review'),
    path('mentor/edit-deadline/<int:pk>/', views.tugas_edit_deadline, name='tugas_edit_deadline'),
    path('peserta/', views.tugas_list_peserta, name='tugas_list_peserta'),
    path('peserta/kerjakan/<int:pk>/', views.tugas_kerjakan, name='tugas_kerjakan'),
    path('peserta/submit/<int:pk>/', views.tugas_submit, name='tugas_submit'),
]
