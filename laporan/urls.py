from django.urls import path
from . import views

app_name = 'laporan'

urlpatterns = [
    path('', views.laporan_peserta, name='laporan_peserta'),
    path('admin/', views.laporan_admin, name='laporan_admin'),
    path('export-excel/', views.export_excel_peserta, name='export_excel_peserta'),
    path('export-excel-admin/', views.export_excel_admin, name='export_excel_admin'),
]