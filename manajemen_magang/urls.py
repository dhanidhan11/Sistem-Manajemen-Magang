from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('users.urls')),
    path('absensi/', include('absensi.urls')),
    path('logbook/', include('logbook.urls')),
    path('penilaian/', include('penilaian.urls')),
    path('peserta/', include('peserta.urls')),
    path('laporan/', include('laporan.urls')),
    path('tugas/', include('tugas.urls')),
    path('projek/', include('projek.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)