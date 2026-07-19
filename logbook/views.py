from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db.models import Q
from django.core.paginator import Paginator
from peserta.models import Peserta
from .models import Logbook
from tugas.models import Tugas

@login_required
def logbook_list(request):
    """Daftar logbook peserta (untuk peserta sendiri)"""
    
    try:
        peserta = Peserta.objects.get(user=request.user)
    except Peserta.DoesNotExist:
        messages.error(request, 'Anda tidak terdaftar sebagai peserta magang!')
        return redirect('/dashboard/peserta/')
    
    logbooks = Logbook.objects.filter(peserta=peserta).order_by('-tanggal')
    
    context = {
        'logbooks': logbooks,
        'peserta': peserta,
    }
    return render(request, 'logbook_list.html', context)

@login_required
def logbook_create(request):
    """Buat logbook baru"""
    
    try:
        peserta = Peserta.objects.get(user=request.user)
    except Peserta.DoesNotExist:
        messages.error(request, 'Anda tidak terdaftar sebagai peserta magang!')
        return redirect('/dashboard/peserta/')
    
    if request.method == 'POST':
        kegiatan = request.POST.get('kegiatan')
        dokumentasi = request.FILES.get('dokumentasi')
        tugas_id = request.POST.get('tugas_terkait')
        
        if not kegiatan:
            messages.error(request, 'Kegiatan harus diisi!')
            return redirect('logbook:logbook_create')
            
        tugas_terkait = None
        if tugas_id:
            try:
                tugas_terkait = Tugas.objects.get(id=tugas_id, peserta=peserta)
            except Tugas.DoesNotExist:
                pass
        
        logbook = Logbook.objects.create(
            peserta=peserta,
            kegiatan=kegiatan,
            dokumentasi=dokumentasi,
            tugas_terkait=tugas_terkait,
            status='dikirim'
        )
        
        messages.success(request, '✅ Logbook berhasil dikirim!')
        return redirect('logbook:logbook_list')
    
    tugas_aktif = Tugas.objects.filter(peserta=peserta).exclude(status='selesai')
    
    # Menangkap parameter GET jika ada
    selected_tugas_id = request.GET.get('tugas_id')
    if selected_tugas_id:
        try:
            selected_tugas_id = int(selected_tugas_id)
        except ValueError:
            selected_tugas_id = None
            
    context = {
        'tugas_aktif': tugas_aktif,
        'selected_tugas_id': selected_tugas_id
    }
    
    return render(request, 'logbook_form.html', context)

@login_required
def logbook_mentor(request):
    """Daftar logbook peserta bimbingan (untuk mentor)"""
    
    # Cek apakah user adalah mentor
    if not request.user.groups.filter(name='Mentor').exists():
        messages.error(request, 'Anda bukan mentor!')
        return redirect('/dashboard/mentor/')
    
    # Ambil semua peserta bimbingan mentor ini
    peserta_bimbingan = Peserta.objects.filter(mentor=request.user)
    
    # Ambil nilai pencarian dari URL (GET parameter)
    query = request.GET.get('q')
    
    # Ambil logbook dari peserta bimbingan
    logbooks = Logbook.objects.filter(
        peserta__in=peserta_bimbingan
    ).select_related('peserta__user', 'tugas_terkait').order_by('-tanggal')

    # Jika ada query pencarian, aplikasikan filter
    if query:
        logbooks = logbooks.filter(
            Q(peserta__user__first_name__icontains=query) |
            Q(peserta__user__last_name__icontains=query) |
            Q(peserta__nim__icontains=query)
        )
        
    # Terapkan Paginasi (maksimal 10 logbook per halaman)
    paginator = Paginator(logbooks, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'logbooks': page_obj,  # yang dikirim ke template sekarang adalah page_obj
        'search_query': query,
    }
    return render(request, 'logbook_mentor.html', context)

@login_required
def logbook_verify(request, logbook_id):
    """Verifikasi logbook oleh mentor"""
    
    # Cek apakah user adalah mentor
    if not request.user.groups.filter(name='Mentor').exists():
        messages.error(request, 'Anda bukan mentor!')
        return redirect('/dashboard/mentor/')
    
    logbook = get_object_or_404(Logbook, id=logbook_id)
    
    # Cek apakah logbook milik peserta bimbingan mentor ini
    if logbook.peserta.mentor != request.user:
        messages.error(request, 'Anda tidak berhak memverifikasi logbook ini!')
        return redirect('logbook:logbook_mentor')
    
    if request.method == 'POST':
        action = request.POST.get('action')
        catatan = request.POST.get('catatan')
        
        if action == 'approve':
            logbook.status = 'diverifikasi'
            logbook.catatan_mentor = catatan
            messages.success(request, f'✅ Logbook {logbook.peserta.user.get_full_name()} telah diverifikasi!')
        elif action == 'reject':
            logbook.status = 'perlu_revisi'
            logbook.catatan_mentor = catatan
            messages.warning(request, f'⚠️ Logbook {logbook.peserta.user.get_full_name()} dikembalikan untuk revisi.')
            
        logbook.save()
        return redirect('logbook:logbook_mentor')
    
    context = {
        'logbook': logbook,
    }
    return render(request, 'logbook_verify.html', context)


@login_required
def logbook_edit(request, pk):
    """Edit logbook jika status masih draft atau perlu revisi"""
    logbook = get_object_or_404(Logbook, pk=pk)
    
    # Keamanan: pastikan yang edit adalah pembuatnya
    if logbook.peserta.user != request.user:
        messages.error(request, 'Anda tidak berhak mengedit logbook ini!')
        return redirect('logbook:logbook_list')
        
    # Hanya boleh edit jika status Draft atau Perlu Revisi
    if logbook.status not in ['draft', 'perlu_revisi', 'dikirim']: # Biarkan 'dikirim' juga di edit jika perlu (request user)
        messages.error(request, 'Logbook yang sudah diverifikasi tidak dapat diedit.')
        return redirect('logbook:logbook_list')
        
    if request.method == 'POST':
        kegiatan = request.POST.get('kegiatan')
        dokumentasi = request.FILES.get('dokumentasi')
        tugas_id = request.POST.get('tugas_terkait')
        
        logbook.kegiatan = kegiatan
        if dokumentasi:
            logbook.dokumentasi = dokumentasi
            
        if tugas_id:
            try:
                logbook.tugas_terkait = Tugas.objects.get(id=tugas_id, peserta=logbook.peserta)
            except Tugas.DoesNotExist:
                pass
        else:
            logbook.tugas_terkait = None
        
        logbook.status = 'dikirim' # Kirim ulang setelah edit
        logbook.save()
        
        messages.success(request, '✅ Logbook berhasil diperbarui!')
        return redirect('logbook:logbook_list')
        
    tugas_aktif = Tugas.objects.filter(peserta=logbook.peserta).exclude(status='selesai')
    context = {
        'logbook': logbook,
        'edit_mode': True,
        'tugas_aktif': tugas_aktif
    }
    return render(request, 'logbook_form.html', context)