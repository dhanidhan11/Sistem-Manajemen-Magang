from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User, Group
from datetime import date
import random

# Import model
from peserta.models import Peserta
from absensi.models import Absensi
from logbook.models import Logbook
from penilaian.models import Penilaian
from users.models import MentorProfile


def login_view(request):
    """Halaman login untuk semua user"""
    
    if request.user.is_authenticated:
        return redirect_user_dashboard(request.user)
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            messages.success(request, f'Selamat datang, {user.get_full_name() or user.username}!')
            return redirect_user_dashboard(user)
        else:
            messages.error(request, 'Username atau password salah!')
            return redirect('/')
    
    return render(request, 'login.html')


def logout_view(request):
    """Proses logout"""
    logout(request)
    messages.info(request, 'Anda telah logout.')
    return redirect('/')


def get_captcha_data():
    chars = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789" # Tanpa I, O, 0, 1 untuk menghindari kebingungan
    code = "".join(random.choices(chars, k=6))
    return code


def register_peserta(request):
    """Halaman registrasi untuk peserta baru"""
    if request.user.is_authenticated:
        return redirect_user_dashboard(request.user)
    
    if request.method == 'POST':
        # Validasi Captcha
        user_answer = request.POST.get('captcha_answer', '').upper()
        session_answer = request.session.get('captcha_answer')
        
        if not user_answer or user_answer != session_answer:
            messages.error(request, 'Kode Keamanan (Captcha) salah!')
            return redirect('users:register')
            
        # Ambil data dari form
        username = request.POST.get('username')
        password = request.POST.get('password')
        nama_depan = request.POST.get('nama_depan')
        nama_belakang = request.POST.get('nama_belakang')
        email = request.POST.get('email')
        nim = request.POST.get('nim')
        institusi = request.POST.get('institusi')
        jurusan = request.POST.get('jurusan')
        no_hp = request.POST.get('no_hp')
        alamat = request.POST.get('alamat')
        bidang_penempatan = request.POST.get('bidang_penempatan')
        mentor_id = request.POST.get('mentor')
        tanggal_mulai = request.POST.get('tanggal_mulai')
        tanggal_selesai = request.POST.get('tanggal_selesai')
        
        # Validasi Username
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username sudah digunakan!')
            return redirect('users:register')
            
        # Buat user baru
        user = User.objects.create_user(
            username=username,
            password=password,
            first_name=nama_depan,
            last_name=nama_belakang,
            email=email
        )
        group_peserta, _ = Group.objects.get_or_create(name='Peserta')
        user.groups.add(group_peserta)
        
        # Buat data peserta
        mentor = None
        if mentor_id:
            mentor = User.objects.filter(id=mentor_id, groups__name='Mentor').first()
            
        Peserta.objects.create(
            user=user,
            nim=nim,
            institusi=institusi,
            jurusan=jurusan,
            no_hp=no_hp,
            alamat=alamat,
            bidang_penempatan=bidang_penempatan,
            mentor=mentor,
            tanggal_mulai=tanggal_mulai,
            tanggal_selesai=tanggal_selesai,
            status='terdaftar'
        )
        
        messages.success(request, 'Registrasi berhasil! Silakan tunggu verifikasi dari mentor.')
        return redirect('/')
        
    # Generate Captcha baru
    captcha_code = get_captcha_data()
    request.session['captcha_answer'] = captcha_code
    
    # Ambil mentor lengkap dengan profilnya agar bisa tahu bidangnya
    mentors = User.objects.filter(groups__name='Mentor').select_related('mentor_profile')
    
    # Ambil bidang unik yang ada pada mentor
    from users.models import MentorProfile
    available_bidang = MentorProfile.objects.exclude(bidang='').values_list('bidang', flat=True).distinct()
    
    # Map label untuk bidang (opsional, bisa diambil dari BIDANG_CHOICES)
    bidang_map = dict(MentorProfile.BIDANG_CHOICES)
    available_bidang_data = [{'val': b, 'label': bidang_map.get(b, b)} for b in available_bidang]
    
    context = {
        'captcha_code': captcha_code,
        'mentors': mentors,
        'available_bidang': available_bidang_data
    }
    return render(request, 'register.html', context)


@login_required(login_url='/')
def mentor_verification(request):
    """Halaman verifikasi pendaftaran peserta oleh mentor"""
    if not request.user.groups.filter(name='Mentor').exists():
        messages.error(request, 'Hanya mentor yang dapat mengakses halaman ini.')
        return redirect('/')
        
    # Ambil peserta yang menunjuk mentor ini dan masih terdaftar (pending)
    pending_peserta = Peserta.objects.filter(mentor=request.user, status='terdaftar').order_by('-created_at')
    
    context = {
        'pending_peserta': pending_peserta
    }
    return render(request, 'verification_list.html', context)


@login_required(login_url='/')
def mentor_approve_peserta(request, pk):
    """Menyetujui pendaftaran peserta"""
    if not request.user.groups.filter(name='Mentor').exists():
        return redirect('/')
        
    peserta = get_object_or_404(Peserta, pk=pk, mentor=request.user)
    peserta.status = 'aktif'
    peserta.save()
    
    messages.success(request, f'Peserta {peserta.user.get_full_name()} telah disetujui.')
    return redirect('users:mentor_verification')


@login_required(login_url='/')
def mentor_reject_peserta(request, pk):
    """Menolak pendaftaran peserta"""
    if not request.user.groups.filter(name='Mentor').exists():
        return redirect('/')
        
    peserta = get_object_or_404(Peserta, pk=pk, mentor=request.user)
    peserta.status = 'ditolak'
    peserta.save()
    
    messages.warning(request, f'Pendaftaran {peserta.user.get_full_name()} telah ditolak.')
    return redirect('users:mentor_verification')


def redirect_user_dashboard(user):
    """Redirect berdasarkan role/group user"""
    if user.is_superuser or user.groups.filter(name='Admin').exists():
        return redirect('/dashboard/admin/')
    elif user.groups.filter(name='Mentor').exists():
        return redirect('/dashboard/mentor/')
    elif user.groups.filter(name='Peserta').exists():
        return redirect('/dashboard/peserta/')
    else:
        return redirect('/admin/')


# ========== DASHBOARD VIEWS ==========

@login_required(login_url='/')
def dashboard_admin(request):
    """Dashboard untuk Admin"""
    if not request.user.groups.filter(name='Admin').exists():
        return redirect('/')
    
    total_peserta = Peserta.objects.count()
    peserta_aktif = Peserta.objects.filter(status='aktif').count()
    total_mentor = User.objects.filter(groups__name='Mentor').count()
    
    # Statistik tambahan
    absensi_hari_ini = Absensi.objects.filter(tanggal=date.today()).count()
    logbook_pending = Logbook.objects.filter(status='dikirim').count()
    
    # Ambil 5 peserta terbaru
    peserta_terbaru = Peserta.objects.all().order_by('-created_at')[:5]
    
    context = {
        'user': request.user,
        'total_peserta': total_peserta,
        'peserta_aktif': peserta_aktif,
        'total_mentor': total_mentor,
        'absensi_hari_ini': absensi_hari_ini,
        'logbook_pending': logbook_pending,
        'peserta_terbaru': peserta_terbaru,
    }
    return render(request, 'dashboard_admin.html', context)


@login_required(login_url='/')
def dashboard_mentor(request):
    """Dashboard untuk Mentor"""
    if not request.user.groups.filter(name='Mentor').exists():
        return redirect('/')
    
    from tugas.models import Tugas
    from absensi.models import Absensi
    
    # Ambil peserta bimbingan mentor ini
    peserta_bimbingan = Peserta.objects.filter(mentor=request.user).select_related('user')
    total_bimbingan = peserta_bimbingan.count()
    
    # Pasang data lengkap untuk setiap peserta (dipakai di modal)
    for p in peserta_bimbingan:
        p.penilaian = Penilaian.objects.filter(peserta=p, mentor=request.user).first()
        p.jumlah_logbook = Logbook.objects.filter(peserta=p).count()
        p.logbook_pending = Logbook.objects.filter(peserta=p, status='dikirim').count()
        p.jumlah_absensi = Absensi.objects.filter(peserta=p).count()
        p.tugas_list = Tugas.objects.filter(peserta=p).order_by('-deadline')
        p.logbook_terbaru = Logbook.objects.filter(peserta=p).order_by('-tanggal')[:3]
    
    # Hitung logbook bimbingan yang perlu diverifikasi
    logbook_pending = Logbook.objects.filter(
        peserta__in=peserta_bimbingan,
        status='dikirim'
    ).count()
    
    # Hitung penilaian yang sudah diberikan
    peserta_sudah_dinilai = Penilaian.objects.filter(
        peserta__in=peserta_bimbingan,
        mentor=request.user
    ).values_list('peserta_id', flat=True)
    
    total_sudah_dinilai = len(peserta_sudah_dinilai)
    total_belum_dinilai = total_bimbingan - total_sudah_dinilai
    
    # Hitung pendaftaran yang perlu diverifikasi
    pendaftaran_pending = Peserta.objects.filter(
        mentor=request.user,
        status='terdaftar'
    ).count()
    
    context = {
        'user': request.user,
        'peserta_bimbingan': peserta_bimbingan,
        'total_bimbingan': total_bimbingan,
        'logbook_pending': logbook_pending,
        'pendaftaran_pending': pendaftaran_pending,
        'total_sudah_dinilai': total_sudah_dinilai,
        'total_belum_dinilai': total_belum_dinilai,
    }
    return render(request, 'dashboard_mentor.html', context)



@login_required(login_url='/')
def dashboard_peserta(request):
    """Dashboard untuk Peserta"""
    if not request.user.groups.filter(name='Peserta').exists():
        return redirect('/')
    
    try:
        data_peserta = Peserta.objects.get(user=request.user)
    except Peserta.DoesNotExist:
        data_peserta = None
    
    absensi_hari_ini = None
    sudah_absen = False
    total_absensi = 0
    total_logbook = 0
    hari_berjalan = 0
    
    if data_peserta:
        absensi_hari_ini = Absensi.objects.filter(
            peserta=data_peserta,
            tanggal=date.today()
        ).first()
        sudah_absen = absensi_hari_ini is not None
        
        total_absensi = Absensi.objects.filter(
            peserta=data_peserta
        ).count()
        
        total_logbook = Logbook.objects.filter(
            peserta=data_peserta
        ).count()
        
        if data_peserta.tanggal_mulai:
            hari_berjalan = (date.today() - data_peserta.tanggal_mulai).days + 1
    
    context = {
        'data_peserta': data_peserta,
        'absensi_hari_ini': absensi_hari_ini,
        'sudah_absen': sudah_absen,
        'total_absensi': total_absensi,
        'total_logbook': total_logbook,
        'hari_berjalan': hari_berjalan if hari_berjalan > 0 else 0,
    }
    return render(request, 'dashboard_peserta.html', context)


# ========== MENTOR CRUD VIEWS (FOR ADMIN) ==========

@login_required(login_url='/')
def mentor_list(request):
    """Daftar semua mentor (untuk Admin)"""
    if not request.user.groups.filter(name='Admin').exists():
        messages.error(request, 'Anda tidak memiliki akses!')
        return redirect('/dashboard/admin/')
    
    mentors = User.objects.filter(groups__name='Mentor').order_by('first_name')
    
    # Ambil peserta bimbingan untuk setiap mentor
    for mentor in mentors:
        mentor.peserta_bimbingan = Peserta.objects.filter(mentor=mentor).order_by('bidang_penempatan')
        
    context = {
        'mentors': mentors,
    }
    return render(request, 'mentor_list.html', context)


@login_required(login_url='/')
def mentor_create(request):
    """Tambah mentor baru (untuk Admin)"""
    if not request.user.groups.filter(name='Admin').exists():
        messages.error(request, 'Anda tidak memiliki akses!')
        return redirect('/dashboard/admin/')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        nama_depan = request.POST.get('nama_depan')
        nama_belakang = request.POST.get('nama_belakang')
        email = request.POST.get('email')
        
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username sudah digunakan!')
            return redirect('users:mentor_create')
            
        # Buat user baru
        user = User.objects.create_user(
            username=username,
            password=password,
            first_name=nama_depan,
            last_name=nama_belakang,
            email=email
        )
        
        # Tambahkan ke grup Mentor
        group_mentor, created = Group.objects.get_or_create(name='Mentor')
        user.groups.add(group_mentor)
        user.save()
        
        # Buat MentorProfile dengan bidang
        bidang = request.POST.get('bidang')
        from users.models import MentorProfile
        MentorProfile.objects.create(user=user, bidang=bidang)
        
        messages.success(request, f'✅ Mentor {user.get_full_name() or user.username} berhasil ditambahkan!')
        return redirect('users:mentor_list')
    
    from users.models import MentorProfile
    context = {
        'bidang_choices': MentorProfile.BIDANG_CHOICES
    }
    return render(request, 'mentor_form.html', context)


@login_required(login_url='/')
def mentor_edit(request, mentor_id):
    """Edit data mentor (untuk Admin)"""
    if not request.user.groups.filter(name='Admin').exists():
        messages.error(request, 'Anda tidak memiliki akses!')
        return redirect('/dashboard/admin/')
        
    mentor = get_object_or_404(User, id=mentor_id)
    
    # Pastikan user tersebut memang mentor
    if not mentor.groups.filter(name='Mentor').exists():
        messages.error(request, 'User tersebut bukan mentor!')
        return redirect('users:mentor_list')
        
    if request.method == 'POST':
        nama_depan = request.POST.get('nama_depan')
        nama_belakang = request.POST.get('nama_belakang')
        email = request.POST.get('email')
        
        mentor.first_name = nama_depan
        mentor.last_name = nama_belakang
        mentor.email = email
        mentor.save()
        
        # Update bidang di profil
        bidang = request.POST.get('bidang')
        from users.models import MentorProfile
        profile, created = MentorProfile.objects.get_or_create(user=mentor)
        profile.bidang = bidang
        profile.save()
        
        messages.success(request, f'✅ Data mentor {mentor.get_full_name()} berhasil diupdate!')
        return redirect('users:mentor_list')
        
    from users.models import MentorProfile
    context = {
        'mentor': mentor,
        'bidang_choices': MentorProfile.BIDANG_CHOICES
    }
    return render(request, 'mentor_edit.html', context)


@login_required(login_url='/')
def mentor_delete(request, mentor_id):
    """Hapus mentor (untuk Admin)"""
    if not request.user.groups.filter(name='Admin').exists():
        messages.error(request, 'Anda tidak memiliki akses!')
        return redirect('/dashboard/admin/')
        
    mentor = get_object_or_404(User, id=mentor_id)
    
    # Pastikan memang mentor
    if not mentor.groups.filter(name='Mentor').exists():
        messages.error(request, 'User tersebut bukan mentor!')
        return redirect('users:mentor_list')
        
    if request.method == 'POST':
        nama = mentor.get_full_name() or mentor.username
        mentor.delete()
        messages.success(request, f'✅ Mentor {nama} berhasil dihapus!')
        return redirect('users:mentor_list')
        
    context = {
        'mentor': mentor,
    }
    return render(request, 'mentor_delete.html', context)


# ========== PROFILE VIEWS ==========

@login_required(login_url='/')
def profile_edit(request):
    """Halaman edit profil untuk Mentor dan Peserta"""
    user = request.user
    is_mentor = user.groups.filter(name='Mentor').exists()
    is_peserta = user.groups.filter(name='Peserta').exists()

    if not (is_mentor or is_peserta):
        messages.error(request, 'Fitur edit profil hanya tersedia untuk Mentor dan Peserta.')
        return redirect('/')

    # Inisialisasi profil mentor jika belum ada
    mentor_profile = None
    peserta_profile = None

    if is_mentor:
        mentor_profile, _ = MentorProfile.objects.get_or_create(user=user)
    if is_peserta:
        try:
            peserta_profile = Peserta.objects.get(user=user)
        except Peserta.DoesNotExist:
            messages.error(request, 'Data peserta tidak ditemukan.')
            return redirect('users:dashboard_peserta')

    if request.method == 'POST':
        # Update field User bawaan Django
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        user.first_name = first_name
        user.last_name = last_name
        user.save()

        if is_mentor:
            mentor_profile.no_hp = request.POST.get('no_hp', '').strip()
            mentor_profile.gelar = request.POST.get('gelar', '').strip()
            if 'foto' in request.FILES:
                mentor_profile.foto = request.FILES['foto']
            mentor_profile.save()

        elif is_peserta:
            peserta_profile.no_hp = request.POST.get('no_hp', '').strip()
            peserta_profile.alamat = request.POST.get('alamat', '').strip()
            if 'foto' in request.FILES:
                peserta_profile.foto = request.FILES['foto']
            peserta_profile.save()

        messages.success(request, '✅ Profil berhasil diperbarui!')
        return redirect('users:profile_edit')

    context = {
        'user': user,
        'is_mentor': is_mentor,
        'is_peserta': is_peserta,
        'mentor_profile': mentor_profile,
        'peserta_profile': peserta_profile,
    }
    return render(request, 'profile_edit.html', context)