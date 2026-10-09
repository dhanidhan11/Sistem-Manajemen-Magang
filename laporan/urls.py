from django.urls import path
from . import views

app_name = 'laporan'

urlpatterns = [
    # Peserta
    path('', views.laporan_peserta, name='laporan_peserta'),
    path('export-excel/', views.export_excel_peserta, name='export_excel_peserta'),

    # Admin
    path('admin/', views.laporan_admin, name='laporan_admin'),
    path('export-excel-admin/', views.export_excel_admin, name='export_excel_admin'),
    path('export-excel-harian-admin/', views.export_excel_harian_admin, name='export_excel_harian_admin'),
    path('export-excel-bulanan-admin/', views.export_excel_bulanan_admin, name='export_excel_bulanan_admin'),

    # Mentor
    path('mentor/', views.laporan_mentor, name='laporan_mentor'),
    path('export-excel-harian-mentor/', views.export_excel_harian_mentor, name='export_excel_harian_mentor'),
    path('export-excel-bulanan-mentor/', views.export_excel_bulanan_mentor, name='export_excel_bulanan_mentor'),
]