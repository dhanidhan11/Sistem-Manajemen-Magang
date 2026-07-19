from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.core.paginator import Paginator
from datetime import date
from .models import Tugas
from peserta.models import Peserta

@login_required
def tugas_list_mentor(request):
    """Daftar tugas yang diberikan oleh mentor"""
    if not request.user.groups.filter(name='Mentor').exists():
        messages.error(request, 'Anda bukan mentor!')
        return redirect('/')
    
    tugas_list = Tugas.objects.filter(mentor=request.user).select_related('peserta__user').order_by('-created_at')
    peserta_bimbingan = Peserta.objects.filter(mentor=request.user)
    
    # Pencarian berdasarkan NIM atau Nama Peserta
    query = request.GET.get('q')
    if query:
        tugas_list = tugas_list.filter(
            Q(peserta__nim__icontains=query) |
            Q(peserta__user__first_name__icontains=query) |
            Q(peserta__user__last_name__icontains=query)
        )
    
    # Paginasi 10 per halaman
    paginator = Paginator(tugas_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    today = date.today()
    for t in page_obj:
        t.is_expired = t.deadline < today
    
    context = {
        'tugas_list': page_obj,
        'peserta_bimbingan': peserta_bimbingan,
        'search_query': query,
    }
    return render(request, 'tugas_list_mentor.html', context)

@login_required
def tugas_create(request):
    """Mentor membuat tugas baru"""
    if not request.user.groups.filter(name='Mentor').exists():
        return redirect('/')
        
    if request.method == 'POST':
        judul = request.POST.get('judul')
        deskripsi = request.POST.get('deskripsi')
        bentuk_projek = request.POST.get('bentuk_projek')
        peserta_id = request.POST.get('peserta')
        deadline = request.POST.get('deadline')
        
        if not (judul and peserta_id and deadline):
            messages.error(request, 'Harap isi semua field!')
            return redirect('tugas:tugas_list_mentor')
            
        peserta = get_object_or_404(Peserta, id=peserta_id, mentor=request.user)
        
        Tugas.objects.create(
            judul=judul,
            deskripsi=deskripsi,
            bentuk_projek=bentuk_projek,
            mentor=request.user,
            peserta=peserta,
            deadline=deadline
        )
        
        messages.success(request, '✅ Tugas berhasil diberikan!')
    return redirect('tugas:tugas_list_mentor')

@login_required
def tugas_list_peserta(request):
    """Daftar tugas untuk peserta"""
    try:
        peserta = Peserta.objects.get(user=request.user)
    except Peserta.DoesNotExist:
        messages.error(request, 'Peserta tidak ditemukan!')
        return redirect('/')
    
    today = date.today()
    tugas_saya = Tugas.objects.filter(peserta=peserta).order_by('deadline')
    
    # Auto-expire: tugas yang deadline-nya sudah lewat dan belum selesai → tandai expired
    for t in tugas_saya:
        if t.deadline < today and t.status == 'belum':
            t.status = 'selesai'
            t.catatan_mentor = (t.catatan_mentor or '') + ' [Otomatis ditutup: deadline telah berakhir]'
            t.save()
    
    # Refresh qs setelah update, dan pasang flag is_expired ke setiap tugas
    tugas_saya = list(Tugas.objects.filter(peserta=peserta).order_by('deadline'))
    for t in tugas_saya:
        t.is_expired = t.deadline < today
    
    context = {
        'tugas_saya': tugas_saya,
        'today': today,
    }
    return render(request, 'tugas_list_peserta.html', context)

@login_required
def tugas_kerjakan(request, pk):
    """Mengubah status tugas menjadi proses dan otomatis menempatkan di tabel ProjekMagang"""
    try:
        peserta = Peserta.objects.get(user=request.user)
    except Peserta.DoesNotExist:
        messages.error(request, 'Hanya peserta magang yang dapat mengerjakan tugas.')
        return redirect('/')
        
    tugas = get_object_or_404(Tugas, pk=pk, peserta=peserta)
    
    if tugas.deadline < date.today():
        messages.error(request, '⏰ Batas waktu tugas ini telah berakhir. Tidak dapat dikerjakan.')
        return redirect('tugas:tugas_list_peserta')
        
    if tugas.status == 'belum':
        tugas.status = 'proses'
        tugas.save()
        
        # Bawa model ProjekMagang
        from projek.models import ProjekMagang
        projek, created = ProjekMagang.objects.get_or_create(
            peserta=peserta,
            defaults={
                'judul': tugas.judul,
                'penjelasan': tugas.deskripsi,
                'alur_projek': 'Diberikan oleh mentor pendamping. Silakan perbarui alur pengerjaan jika dibutuhkan.',
            }
        )
        if not created:
            projek.judul = tugas.judul
            projek.penjelasan = tugas.deskripsi
            projek.save()
            
        messages.success(request, '🚀 Semangat mengerjakan! Projek/Tugas ini otomatis didaftarkan di Projek Saya.')
    else:
        messages.info(request, 'Tugas ini sudah dalam proses atau selesai.')
        
    return redirect('tugas:tugas_list_peserta')


@login_required
def tugas_submit(request, pk):
    """Peserta mengirimkan file tugas"""
    try:
        peserta = Peserta.objects.get(user=request.user)
    except Peserta.DoesNotExist:
        return redirect('/')
        
    tugas = get_object_or_404(Tugas, pk=pk, peserta=peserta)
    
    # Blokir pengiriman jika deadline sudah lewat
    if tugas.deadline < date.today():
        messages.error(request, '⏰ Batas waktu tugas ini telah berakhir. Pengiriman tidak dapat dilakukan.')
        return redirect('tugas:tugas_list_peserta')
    
    # Blokir jika status sudah selesai
    if tugas.status == 'selesai':
        messages.error(request, '✅ Tugas ini sudah selesai dan tidak dapat diubah lagi.')
        return redirect('tugas:tugas_list_peserta')
    
    if request.method == 'POST':
        file_tugas = request.FILES.get('file_tugas')
        link_tugas = request.POST.get('link_tugas')
        
        if not file_tugas and not link_tugas:
            messages.error(request, 'Harap upload file atau sertakan link sebagai bukti pengerjaan!')
            return redirect('tugas:tugas_list_peserta')
            
        if file_tugas:
            tugas.file_tugas = file_tugas
        if link_tugas:
            tugas.link_tugas = link_tugas
            
        tugas.status = 'dikirim'
        tugas.save()

        # Otomatis sinkronkan file & link tugas ke Projek Saya (ProjekMagang)
        from projek.models import ProjekMagang
        projek, created = ProjekMagang.objects.get_or_create(
            peserta=peserta,
            defaults={
                'judul': tugas.judul,
                'penjelasan': tugas.deskripsi,
                'alur_projek': 'Diberikan oleh mentor pendamping. Silakan perbarui alur pengerjaan jika dibutuhkan.',
            }
        )
        if link_tugas:
            if 'github' in link_tugas.lower() or 'gitlab' in link_tugas.lower():
                projek.link_repo = link_tugas
            else:
                projek.link_demo = link_tugas
        if file_tugas:
            projek.file_dokumen = file_tugas
        projek.save()
        
        messages.success(request, '✅ Tugas berhasil dikirim! File/Link pengerjaan otomatis terintegrasi ke menu Projek Saya.')
    return redirect('tugas:tugas_list_peserta')


@login_required
def tugas_review(request, pk):
    """Mentor menilai atau meminta revisi tugas"""
    if not request.user.groups.filter(name='Mentor').exists():
        return redirect('/')
        
    tugas = get_object_or_404(Tugas, pk=pk, mentor=request.user)
    
    if request.method == 'POST':
        action = request.POST.get('action')
        catatan = request.POST.get('catatan')
        nilai = request.POST.get('nilai')
        
        if action == 'approve':
            if not nilai:
                messages.error(request, 'Harap berikan nilai untuk tugas yang selesai!')
                return redirect('tugas:tugas_list_mentor')
            
            tugas.status = 'selesai'
            tugas.nilai = nilai
            tugas.catatan_mentor = catatan
            messages.success(request, f'✅ Tugas "{tugas.judul}" milik {tugas.peserta.user.get_full_name()} telah dinilai: {nilai}.')
        elif action == 'reject':
            tugas.status = 'perlu_revisi'
            tugas.catatan_mentor = catatan
            messages.warning(request, f'⚠️ Tugas "{tugas.judul}" milik {tugas.peserta.user.get_full_name()} dikembalikan untuk revisi.')
            
        tugas.save()
    return redirect('tugas:tugas_list_mentor')


@login_required
def tugas_delete(request, pk):
    """Mentor menghapus tugas"""
    if not request.user.groups.filter(name='Mentor').exists():
        return redirect('/')
        
    tugas = get_object_or_404(Tugas, pk=pk, mentor=request.user)
    judul = tugas.judul
    tugas.delete()
    
    messages.success(request, f'🗑️ Tugas "{judul}" berhasil dihapus.')
    return redirect('tugas:tugas_list_mentor')


@login_required
def tugas_edit_deadline(request, pk):
    """Mentor mengubah deadline tugas"""
    if not request.user.groups.filter(name='Mentor').exists():
        return redirect('/')
    
    tugas = get_object_or_404(Tugas, pk=pk, mentor=request.user)
    
    if request.method == 'POST':
        new_deadline_str = request.POST.get('deadline')
        if not new_deadline_str:
            messages.error(request, 'Deadline tidak boleh kosong!')
            return redirect('tugas:tugas_list_mentor')
        
        from datetime import datetime, date
        try:
            new_date = datetime.strptime(new_deadline_str, "%Y-%m-%d").date()
        except ValueError:
            messages.error(request, 'Format tanggal tidak valid!')
            return redirect('tugas:tugas_list_mentor')
            
        old_deadline = tugas.deadline
        tugas.deadline = new_date
        
        # Jika deadline diubah ke masa depan dan status selesai karena expired, kembalikan ke belum
        if new_date >= date.today() and tugas.status == 'selesai' and tugas.nilai is None:
            tugas.status = 'belum'
            if tugas.catatan_mentor:
                tugas.catatan_mentor = tugas.catatan_mentor.replace(' [Otomatis ditutup: deadline telah berakhir]', '')
        
        tugas.save()
        messages.success(request, f'✅ Deadline tugas "{tugas.judul}" berhasil diperbarui dari {old_deadline.strftime("%d %b %Y")} menjadi {tugas.deadline.strftime("%d %b %Y")}.')
    
    return redirect('tugas:tugas_list_mentor')
