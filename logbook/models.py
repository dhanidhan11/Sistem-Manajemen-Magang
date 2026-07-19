from django.db import models
from peserta.models import Peserta

class Logbook(models.Model):
    peserta = models.ForeignKey(Peserta, on_delete=models.CASCADE)
    tugas_terkait = models.ForeignKey('tugas.Tugas', on_delete=models.SET_NULL, null=True, blank=True, related_name='logbooks', help_text="Tugas atau Projek yang berkaitan dengan logbook ini")
    tanggal = models.DateField(auto_now_add=True)
    kegiatan = models.TextField()
    dokumentasi = models.FileField(upload_to='logbook/', blank=True, null=True)
    status = models.CharField(
        max_length=20,
        choices=[
            ('draft', 'Draft'),
            ('dikirim', 'Dikirim'),
            ('diverifikasi', 'Diverifikasi'),
            ('perlu_revisi', 'Perlu Revisi'),
        ],
        default='draft'
    )
    catatan_mentor = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.peserta.user.get_full_name()} - {self.tanggal}"