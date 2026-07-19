from django.db import models
from django.contrib.auth.models import User
from peserta.models import Peserta

class Penilaian(models.Model):
    peserta = models.ForeignKey(Peserta, on_delete=models.CASCADE)
    mentor = models.ForeignKey(User, on_delete=models.CASCADE)
    
    kedisiplinan = models.IntegerField()
    kreativitas = models.IntegerField()
    komunikasi = models.IntegerField()
    teknis = models.IntegerField()
    presensi = models.IntegerField()
    presentasi = models.IntegerField()
    sikap = models.IntegerField()
    
    total_nilai = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    catatan = models.TextField(blank=True)
    tanggal_penilaian = models.DateTimeField(auto_now_add=True)
    
    def save(self, *args, **kwargs):
        # Hitung total nilai otomatis
        total = (self.kedisiplinan + self.kreativitas + self.komunikasi + 
                 self.teknis + self.presensi + self.presentasi + self.sikap) / 7
        self.total_nilai = round(total, 2)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.peserta.user.get_full_name()} - {self.mentor.get_full_name()}"