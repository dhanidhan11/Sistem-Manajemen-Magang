from django.db import models
from peserta.models import Peserta

class Absensi(models.Model):
    STATUS_CHOICES = (
        ('hadir', 'Hadir'),
        ('sakit', 'Sakit'),
        ('izin', 'Izin'),
        ('alpha', 'Alpha'),
    )
    
    peserta = models.ForeignKey(Peserta, on_delete=models.CASCADE)
    tanggal = models.DateField()  # <-- HAPUS auto_now_add=True
    check_in = models.TimeField(null=True, blank=True)
    check_out = models.TimeField(null=True, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='hadir')
    keterangan = models.TextField(blank=True)
    
    class Meta:
        unique_together = ['peserta', 'tanggal']
    
    def __str__(self):
        return f"{self.peserta.user.get_full_name()} - {self.tanggal}"