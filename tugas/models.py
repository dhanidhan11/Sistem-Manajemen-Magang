from django.db import models
from django.contrib.auth.models import User
from peserta.models import Peserta

class Tugas(models.Model):
    STATUS_CHOICES = (
        ('belum', 'Belum Dikerjakan'),
        ('proses', 'Sedang Dikerjakan'),
        ('dikirim', 'Menunggu Penilaian'),
        ('perlu_revisi', 'Perlu Revisi'),
        ('selesai', 'Selesai (Dinilai)'),
    )
    
    judul = models.CharField(max_length=200)
    bentuk_projek = models.CharField(max_length=200, blank=True, null=True, help_text="Contoh: Website, Makalah, Desain UI, dll")
    deskripsi = models.TextField()
    mentor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tugas_dibuat')
    peserta = models.ForeignKey(Peserta, on_delete=models.CASCADE, related_name='tugas_saya')
    deadline = models.DateField()
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='belum')
    file_tugas = models.FileField(upload_to='tugas_submisi/', blank=True, null=True)
    link_tugas = models.URLField(max_length=500, blank=True, null=True, help_text="Link contoh: GitHub, Google Drive, atau Vercel")
    catatan_mentor = models.TextField(blank=True, null=True)
    nilai = models.IntegerField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.judul} - {self.peserta.user.get_full_name()}"
