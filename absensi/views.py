from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.contrib import messages
from peserta.models import Peserta
from .models import Absensi


@login_required(login_url='/')
def absensi_view(request):
    """Halaman absensi - untuk peserta dan admin"""
    
    # CEK ROLE USER
    if request.user.groups.filter(name='Admin').exists():
        # Admin: tampilkan semua data absensi
        absensi_list = Absensi.objects.all().order_by('-tanggal')[:50]
        context = {
            'is_admin': True,
            'absensi_list': absensi_list,
        }
        return render(request, 'absensi_admin.html', context)
    
    # Peserta: tampilkan absensi sendiri
    try:
        peserta = Peserta.objects.get(user=request.user)
    except Peserta.DoesNotExist:
        messages.error(request, 'Anda tidak terdaftar sebagai peserta magang!')
        return redirect('/dashboard/peserta/')
    
    today = timezone.now().date()
    
    # Cari absensi hari ini
    absensi_hari_ini = Absensi.objects.filter(
        peserta=peserta,
        tanggal=today
    ).first()
    
    # Jika belum ada, buat baru
    if not absensi_hari_ini:
        absensi_hari_ini = Absensi(
            peserta=peserta,
            tanggal=today,
            check_in=None,
            check_out=None,
            status='hadir',
            keterangan=''
        )
        absensi_hari_ini.save()
    
    sudah_checkin = absensi_hari_ini.check_in is not None
    sudah_checkout = absensi_hari_ini.check_out is not None
    
    # Proses POST (Check-in / Check-out)
    if request.method == 'POST':
        action = request.POST.get('action')
        status = request.POST.get('status', 'hadir')
        keterangan = request.POST.get('keterangan', '')
        
        if action == 'checkin' and not sudah_checkin:
            absensi_hari_ini.check_in = timezone.now().time()
            absensi_hari_ini.status = status
            absensi_hari_ini.keterangan = keterangan
            absensi_hari_ini.save()
            messages.success(request, '✅ Check-in berhasil!')
            return redirect('/absensi/')
            
        elif action == 'checkout' and sudah_checkin and not sudah_checkout:
            absensi_hari_ini.check_out = timezone.now().time()
            absensi_hari_ini.save()
            messages.success(request, '✅ Check-out berhasil!')
            return redirect('/absensi/')
    
    # Riwayat absensi
    riwayat_absensi = Absensi.objects.filter(
        peserta=peserta
    ).order_by('-tanggal')[:30]
    
    context = {
        'today': today,
        'absensi_hari_ini': absensi_hari_ini,
        'sudah_checkin': sudah_checkin,
        'sudah_checkout': sudah_checkout,
        'riwayat_absensi': riwayat_absensi,
        'is_admin': False,
    }
    return render(request, 'absensi.html', context)


# ============================================================
# ADMIN - EDIT ABSENSI
# ============================================================

@login_required(login_url='/')
def absensi_admin_edit(request, absensi_id):
    """Admin mengedit absensi peserta"""
    
    if not request.user.groups.filter(name='Admin').exists():
        messages.error(request, 'Anda tidak memiliki akses!')
        return redirect('/dashboard/admin/')
    
    absensi = get_object_or_404(Absensi, id=absensi_id)
    
    if request.method == 'POST':
        check_in = request.POST.get('check_in')
        check_out = request.POST.get('check_out')
        status = request.POST.get('status')
        keterangan = request.POST.get('keterangan', '')
        
        if check_in:
            absensi.check_in = check_in
        if check_out:
            absensi.check_out = check_out
        absensi.status = status
        absensi.keterangan = keterangan
        absensi.save()
        
        messages.success(request, f'✅ Absensi {absensi.peserta.user.get_full_name()} berhasil diupdate!')
        return redirect('/absensi/')
    
    context = {
        'absensi': absensi,
    }
    return render(request, 'absensi_admin_edit.html', context)