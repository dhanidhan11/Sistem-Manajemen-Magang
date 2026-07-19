from django.urls import path
from . import views

app_name = 'projek'

urlpatterns = [
    path('my/', views.projek_detail, name='projek_detail'),
    path('view/<int:pk>/', views.projek_detail, name='projek_view'),
    path('manage/', views.projek_manage, name='projek_manage'),
]
