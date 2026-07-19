from django.db import models
from django.contrib.auth.models import User
from peserta.models import Peserta

class ProjekMagang(models.Model):
    """Model untuk proyek utama peserta magang"""
    peserta = models.OneToOneField(Peserta, on_delete=models.CASCADE, related_name='projek')
    judul = models.CharField(max_length=200)
    penjelasan = models.TextField(help_text="Penjelasan detail tentang projek")
    alur_projek = models.TextField(help_text="Alur atau langkah-langkah pengerjaan projek")
    link_repo = models.URLField(max_length=500, blank=True, null=True, help_text="Link Repository (GitHub/GitLab)")
    link_demo = models.URLField(max_length=500, blank=True, null=True, help_text="Link Demo/Live Projek")
    file_dokumen = models.FileField(upload_to='projek_docs/', blank=True, null=True, help_text="Dokumen teknis projek")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __cl__(self):
        return self.judul

    class Meta:
        verbose_name = "Projek Magang"
        verbose_name_plural = "Projek Magang"
