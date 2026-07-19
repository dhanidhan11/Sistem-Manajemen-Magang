from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import ProjekMagang
from peserta.models import Peserta

@login_required
def projek_detail(request, pk=None):
    """Melihat detail projek (untuk peserta sendiri atau mentornya)"""
    is_mentor = request.user.groups.filter(name='Mentor').exists()
    
    if pk is None:
        # Peserta melihat projeknya sendiri
        try:
            peserta = Peserta.objects.get(user=request.user)
            projek = ProjekMagang.objects.filter(peserta=peserta).first()
            if not projek:
                messages.info(request, 'Anda belum menyusun rencana projek. Silakan buat sekarang.')
                return redirect('projek:projek_manage')
        except Peserta.DoesNotExist:
            return redirect('/')
    else:
        # Mentor atau admin melihat projek peserta tertentu
        projek = get_object_or_404(ProjekMagang, pk=pk)
        # Keamanan: pastikan mentor yang bersangkutan atau admin
        is_admin = request.user.groups.filter(name='Admin').exists()
        if not is_admin:
            if is_mentor and projek.peserta.mentor != request.user:
                messages.error(request, 'Anda tidak memiliki akses ke projek ini.')
                return redirect('users:dashboard_mentor')
            elif not is_mentor and projek.peserta.user != request.user:
                return redirect('/')

    context = {
        'projek': projek,
        'is_mentor': is_mentor
    }
    return render(request, 'projek/projek_detail.html', context)

@login_required
def projek_manage(request):
    """Menambah atau mengedit projek (untuk Peserta)"""
    try:
        peserta = Peserta.objects.get(user=request.user)
    except Peserta.DoesNotExist:
        messages.error(request, 'Hanya peserta magang yang dapat mengelola projek.')
        return redirect('/')
    
    projek = ProjekMagang.objects.filter(peserta=peserta).first()
    
    if request.method == 'POST':
        judul = request.POST.get('judul')
        penjelasan = request.POST.get('penjelasan')
        alur_projek = request.POST.get('alur_projek')
        link_repo = request.POST.get('link_repo')
        link_demo = request.POST.get('link_demo')
        file_dokumen = request.FILES.get('file_dokumen')
        
        if not (judul and penjelasan and alur_projek):
            messages.error(request, 'Harap isi Judul, Penjelasan, dan Alur Projek!')
            return redirect('projek:projek_manage')

        if projek:
            projek.judul = judul
            projek.penjelasan = penjelasan
            projek.alur_projek = alur_projek
            projek.link_repo = link_repo
            projek.link_demo = link_demo
            if file_dokumen:
                projek.file_dokumen = file_dokumen
            projek.save()
            messages.success(request, '✅ Rencana projek berhasil diperbarui!')
        else:
            ProjekMagang.objects.create(
                peserta=peserta,
                judul=judul,
                penjelasan=penjelasan,
                alur_projek=alur_projek,
                link_repo=link_repo,
                link_demo=link_demo,
                file_dokumen=file_dokumen
            )
            messages.success(request, '✅ Rencana projek berhasil dibuat!')
        
        return redirect('projek:projek_detail')
        
    context = {
        'projek': projek,
    }
    return render(request, 'projek/projek_form.html', context)
