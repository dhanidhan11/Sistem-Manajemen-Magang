from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User, Group
from .models import Peserta

@login_required(login_url='/')
def peserta_list(request):
    """Daftar semua peserta (untuk Admin)"""
    
    if not request.user.groups.filter(name='Admin').exists():
        messages.error(request, 'Anda tidak memiliki akses!')
        return redirect('/dashboard/admin/')
    
    peserta_list = Peserta.objects.all().order_by('-created_at')
    
    context = {
        'peserta_list': peserta_list,
    }
    return render(request, 'peserta_list.html', context)

@login_required(login_url='/')
def peserta_create(request):
    """Tambah peserta baru (untuk Admin)"""
    
    if not request.user.groups.filter(name='Admin').exists():
        messages.error(request, 'Anda tidak memiliki akses!')
        return redirect('/dashboard/admin/')
    
    if request.method == 'POST':
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
        
        # Validasi
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username sudah digunakan!')
            return redirect('peserta:peserta_create')
        
        # Buat user baru
        user = User.objects.create_user(
            username=username,
            password=password,
            first_name=nama_depan,
            last_name=nama_belakang,
            email=email
        )
        user.groups.add(Group.objects.get(name='Peserta'))
        user.save()
        
        # Buat data peserta
        mentor = None
        if mentor_id:
            try:
                mentor = User.objects.get(id=mentor_id)
            except User.DoesNotExist:
                pass
        
        peserta = Peserta.objects.create(
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
            status='aktif'
        )
        
        messages.success(request, f'✅ Peserta {user.get_full_name()} berhasil ditambahkan!')
        return redirect('peserta:peserta_list')
    
    # Ambil daftar mentor untuk dropdown
    mentors = User.objects.filter(groups__name='Mentor')
    
    context = {
        'mentors': mentors,
    }
    return render(request, 'peserta_form.html', context)

@login_required(login_url='/')
def peserta_edit(request, peserta_id):
    """Edit data peserta (untuk Admin)"""
    
    if not request.user.groups.filter(name='Admin').exists():
        messages.error(request, 'Anda tidak memiliki akses!')
        return redirect('/dashboard/admin/')
    
    peserta = get_object_or_404(Peserta, id=peserta_id)
    user = peserta.user
    
    if request.method == 'POST':
        # Ambil data dari form
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
        status = request.POST.get('status')
        
        # Update user
        user.first_name = nama_depan
        user.last_name = nama_belakang
        user.email = email
        user.save()
        
        # Update peserta
        mentor = None
        if mentor_id:
            try:
                mentor = User.objects.get(id=mentor_id)
            except User.DoesNotExist:
                pass
        
        peserta.nim = nim
        peserta.institusi = institusi
        peserta.jurusan = jurusan
        peserta.no_hp = no_hp
        peserta.alamat = alamat
        peserta.bidang_penempatan = bidang_penempatan
        peserta.mentor = mentor
        peserta.tanggal_mulai = tanggal_mulai
        peserta.tanggal_selesai = tanggal_selesai
        peserta.status = status
        peserta.save()
        
        messages.success(request, f'✅ Data {user.get_full_name()} berhasil diupdate!')
        return redirect('peserta:peserta_list')
    
    # Ambil daftar mentor untuk dropdown
    mentors = User.objects.filter(groups__name='Mentor')
    
    context = {
        'peserta': peserta,
        'user': user,
        'mentors': mentors,
    }
    return render(request, 'peserta_edit.html', context)

@login_required(login_url='/')
def peserta_delete(request, peserta_id):
    """Hapus peserta (untuk Admin)"""
    
    if not request.user.groups.filter(name='Admin').exists():
        messages.error(request, 'Anda tidak memiliki akses!')
        return redirect('/dashboard/admin/')
    
    peserta = get_object_or_404(Peserta, id=peserta_id)
    user = peserta.user
    
    if request.method == 'POST':
        nama = user.get_full_name()
        user.delete()  # Akan menghapus peserta juga (karena OneToOne)
        messages.success(request, f'✅ Peserta {nama} berhasil dihapus!')
        return redirect('peserta:peserta_list')
    
    context = {
        'peserta': peserta,
        'user': user,
    }
    return render(request, 'peserta_delete.html', context)