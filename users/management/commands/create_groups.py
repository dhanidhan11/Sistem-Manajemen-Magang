from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from peserta.models import Peserta
from absensi.models import Absensi
from logbook.models import Logbook
from penilaian.models import Penilaian

class Command(BaseCommand):
    help = 'Membuat groups dan permissions default'

    def handle(self, *args, **options):
        # Buat groups
        admin_group, _ = Group.objects.get_or_create(name='Admin')
        mentor_group, _ = Group.objects.get_or_create(name='Mentor')
        peserta_group, _ = Group.objects.get_or_create(name='Peserta')
        
        self.stdout.write(self.style.SUCCESS('Groups berhasil dibuat!'))
        
        # Buat user admin default
        if not User.objects.filter(username='admin').exists():
            admin = User.objects.create_user(
                username='admin',
                password='admin123',
                first_name='Administrator',
                last_name='Diskominfo'
            )
            admin.groups.add(admin_group)
            admin.is_staff = True
            admin.is_superuser = True
            admin.save()
            self.stdout.write(self.style.SUCCESS('User admin berhasil dibuat!'))
        
        # Buat user mentor default
        if not User.objects.filter(username='mentor1').exists():
            mentor = User.objects.create_user(
                username='mentor1',
                password='mentor123',
                first_name='Budi',
                last_name='Santoso'
            )
            mentor.groups.add(mentor_group)
            mentor.save()
            self.stdout.write(self.style.SUCCESS('User mentor1 berhasil dibuat!'))
        
        # Buat user peserta default
        if not User.objects.filter(username='mahasiswa1').exists():
            peserta = User.objects.create_user(
                username='mahasiswa1',
                password='peserta123',
                first_name='Ahmad',
                last_name='Fauzi'
            )
            peserta.groups.add(peserta_group)
            peserta.save()
            self.stdout.write(self.style.SUCCESS('User mahasiswa1 berhasil dibuat!'))