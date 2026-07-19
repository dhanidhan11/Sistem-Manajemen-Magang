from django.db import models
from django.contrib.auth.models import User

class Peserta(models.Model):
    STATUS_CHOICES = (
        ('terdaftar', 'Terdaftar (Pending)'),
        ('aktif', 'Aktif'),
        ('ditolak', 'Ditolak'),
        ('selesai', 'Selesai'),
    )
    
    BIDANG_CHOICES = (
        ('Sekretariat', 'Sekretariat'),
        ('IKP', 'Informasi & Komunikasi Publik (IKP)'),
        ('Aptika', 'Aplikasi & Informatika (Aptika)'),
        ('Persandian', 'Persandian & Statistik'),
        ('IT', 'IT Support / Infrastruktur'),
        ('Humas', 'Humas & Protokol'),
    )
    
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    nim = models.CharField(max_length=20, unique=True)
    institusi = models.CharField(max_length=100)
    jurusan = models.CharField(max_length=100)
    no_hp = models.CharField(max_length=15, blank=True)
    alamat = models.TextField(blank=True)
    bidang_penempatan = models.CharField(max_length=50, choices=BIDANG_CHOICES)
    mentor = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='bimbingan'
    )
    tanggal_mulai = models.DateField()
    tanggal_selesai = models.DateField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='terdaftar')
    foto = models.ImageField(upload_to='peserta_photos/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.get_full_name()} - {self.nim}"