from django.db import models
from django.contrib.auth.models import User


class MentorProfile(models.Model):
    """Model untuk menyimpan data profil tambahan Mentor."""
    BIDANG_CHOICES = (
        ('Sekretariat', 'Sekretariat'),
        ('IKP', 'Informasi & Komunikasi Publik (IKP)'),
        ('Aptika', 'Aplikasi & Informatika (Aptika)'),
        ('Persandian', 'Persandian & Statistik'),
        ('IT', 'IT Support / Infrastruktur'),
        ('Humas', 'Humas & Protokol'),
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='mentor_profile')
    bidang = models.CharField(max_length=50, choices=BIDANG_CHOICES, blank=True)
    no_hp = models.CharField(max_length=15, blank=True)
    gelar = models.CharField(max_length=100, blank=True, help_text='Contoh: S.Kom., M.T.')
    foto = models.ImageField(upload_to='mentor_photos/', blank=True, null=True)

    def __str__(self):
        return f"Profil Mentor - {self.user.get_full_name() or self.user.username}"
