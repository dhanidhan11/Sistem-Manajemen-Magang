from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from peserta.models import Peserta
from .models import Penilaian

@login_required(login_url='/')
def penilaian_list(request):
    """Daftar penilaian (untuk admin dan mentor)"""
    
    if request.user.groups.filter(name='Admin').exists():
        penilaian = Penilaian.objects.all().order_by('-tanggal_penilaian')
    elif request.user.groups.filter(name='Mentor').exists():
        peserta_bimbingan = Peserta.objects.filter(mentor=request.user)
        penilaian = Penilaian.objects.filter(
            peserta__in=peserta_bimbingan
        ).order_by('-tanggal_penilaian')
    else:
        try:
            peserta = Peserta.objects.get(user=request.user)
            penilaian = Penilaian.objects.filter(peserta=peserta).order_by('-tanggal_penilaian')
        except Peserta.DoesNotExist:
            penilaian = []
    
    context = {
        'penilaian': penilaian,
    }
    return render(request, 'penilaian_list.html', context)

@login_required(login_url='/')
def penilaian_create(request, peserta_id):
    """Mentor membuat penilaian untuk peserta"""
    
    if not request.user.groups.filter(name='Mentor').exists():
        messages.error(request, 'Anda bukan mentor!')
        return redirect('/dashboard/mentor/')
    
    peserta = get_object_or_404(Peserta, id=peserta_id)
    
    if peserta.mentor != request.user:
        messages.error(request, 'Anda tidak berhak menilai peserta ini!')
        return redirect('penilaian:penilaian_list')
    
    if Penilaian.objects.filter(peserta=peserta, mentor=request.user).exists():
        messages.warning(request, 'Peserta ini sudah dinilai!')
        return redirect('penilaian:penilaian_list')
    
    if request.method == 'POST':
        try:
            kedisiplinan  = int(request.POST.get('kedisiplinan',  0))
            kreativitas   = int(request.POST.get('kreativitas',   0))
            komunikasi    = int(request.POST.get('komunikasi',    0))
            teknis        = int(request.POST.get('teknis',        0))
            presensi      = int(request.POST.get('presensi',      0))
            presentasi    = int(request.POST.get('presentasi',    0))
            sikap         = int(request.POST.get('sikap',         0))
        except (TypeError, ValueError):
            messages.error(request, '⚠️ Harap pilih nilai untuk setiap aspek penilaian!')
            return redirect('penilaian:penilaian_create', peserta_id=peserta_id)
        catatan = request.POST.get('catatan', '')
        
        missing = [f for f, v in [('Kedisiplinan', kedisiplinan), ('Kreativitas', kreativitas), ('Komunikasi', komunikasi), ('Teknis', teknis), ('Presensi', presensi), ('Presentasi', presentasi), ('Sikap', sikap)] if request.POST.get(f.lower()) is None]
        if missing:
            missing_str = ', '.join(missing)
            messages.error(request, f'⚠️ Pilih nilai untuk: {missing_str}')
            return redirect('penilaian:penilaian_create', peserta_id=peserta_id)
        
        penilaian = Penilaian.objects.create(
            peserta=peserta,
            mentor=request.user,
            kedisiplinan=kedisiplinan,
            kreativitas=kreativitas,
            komunikasi=komunikasi,
            teknis=teknis,
            presensi=presensi,
            presentasi=presentasi,
            sikap=sikap,
            catatan=catatan
        )
        
        messages.success(request, f'✅ Penilaian untuk {peserta.user.get_full_name()} berhasil disimpan!')
        return redirect('penilaian:penilaian_list')
    
    context = {
        'peserta': peserta,
    }
    return render(request, 'penilaian_form.html', context)

@login_required(login_url='/')
def penilaian_detail(request, penilaian_id):
    """Lihat detail penilaian"""
    
    penilaian = get_object_or_404(Penilaian, id=penilaian_id)
    
    user = request.user
    if user.groups.filter(name='Peserta').exists():
        try:
            peserta = Peserta.objects.get(user=user)
            if penilaian.peserta != peserta:
                messages.error(request, 'Anda tidak berhak melihat penilaian ini!')
                return redirect('/dashboard/peserta/')
        except Peserta.DoesNotExist:
            messages.error(request, 'Anda tidak terdaftar sebagai peserta!')
            return redirect('/dashboard/peserta/')
    elif user.groups.filter(name='Mentor').exists():
        if penilaian.peserta.mentor != user:
            messages.error(request, 'Anda tidak berhak melihat penilaian ini!')
            return redirect('penilaian:penilaian_list')
    
    context = {
        'penilaian': penilaian,
    }
    return render(request, 'penilaian_detail.html', context)


@login_required(login_url='/')
def penilaian_edit(request, penilaian_id):
    """Mentor mengubah penilaian yang sudah ada"""
    
    if not request.user.groups.filter(name='Mentor').exists():
        messages.error(request, 'Anda bukan mentor!')
        return redirect('/dashboard/mentor/')
        
    penilaian = get_object_or_404(Penilaian, id=penilaian_id)
    peserta = penilaian.peserta
    
    if peserta.mentor != request.user:
        messages.error(request, 'Anda tidak berhak mengubah penilaian peserta ini!')
        return redirect('penilaian:penilaian_list')
        
    if request.method == 'POST':
        kedisiplinan = int(request.POST.get('kedisiplinan', 0))
        kreativitas = int(request.POST.get('kreativitas', 0))
        komunikasi = int(request.POST.get('komunikasi', 0))
        teknis = int(request.POST.get('teknis', 0))
        presensi = int(request.POST.get('presensi', 0))
        presentasi = int(request.POST.get('presentasi', 0))
        sikap = int(request.POST.get('sikap', 0))
        catatan = request.POST.get('catatan', '')
        
        if not all(0 <= n <= 100 for n in [kedisiplinan, kreativitas, komunikasi, teknis, presensi, presentasi, sikap]):
            messages.error(request, 'Nilai harus antara 0-100!')
            return redirect('penilaian:penilaian_edit', penilaian_id=penilaian_id)
            
        penilaian.kedisiplinan = kedisiplinan
        penilaian.kreativitas = kreativitas
        penilaian.komunikasi = komunikasi
        penilaian.teknis = teknis
        penilaian.presensi = presensi
        penilaian.presentasi = presentasi
        penilaian.sikap = sikap
        penilaian.catatan = catatan
        penilaian.save()
        
        messages.success(request, f'✅ Penilaian untuk {peserta.user.get_full_name()} berhasil diperbarui!')
        return redirect('penilaian:penilaian_list')
        
    context = {
        'peserta': peserta,
        'penilaian': penilaian,
        'edit_mode': True,
    }
    return render(request, 'penilaian_form.html', context)