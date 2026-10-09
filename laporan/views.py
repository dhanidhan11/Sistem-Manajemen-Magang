from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse
from django.db import models
from peserta.models import Peserta
from absensi.models import Absensi
from logbook.models import Logbook
from penilaian.models import Penilaian
from datetime import date, datetime
import calendar

from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, PatternFill, Border, Side
from openpyxl.utils import get_column_letter

# Helper style untuk Excel
def get_excel_styles():
    bold_font = Font(bold=True)
    center_align = Alignment(horizontal='center', vertical='center')
    left_align = Alignment(horizontal='left', vertical='center')
    border = Border(
        left=Side(style='thin', color='D1D5DB'),
        right=Side(style='thin', color='D1D5DB'),
        top=Side(style='thin', color='D1D5DB'),
        bottom=Side(style='thin', color='D1D5DB')
    )
    header_fill = PatternFill(start_color="1E3A8A", end_color="1E3A8A", fill_type="solid")
    header_font = Font(bold=True, color="FFFFFF")
    section_fill = PatternFill(start_color="DBEAFE", end_color="DBEAFE", fill_type="solid")
    section_font = Font(bold=True, color="1E3A8A")
    return {
        'bold_font': bold_font,
        'center_align': center_align,
        'left_align': left_align,
        'border': border,
        'header_fill': header_fill,
        'header_font': header_font,
        'section_fill': section_fill,
        'section_font': section_font,
    }

MONTH_NAMES = [
    (1, 'Januari'), (2, 'Februari'), (3, 'Maret'), (4, 'April'),
    (5, 'Mei'), (6, 'Juni'), (7, 'Juli'), (8, 'Agustus'),
    (9, 'September'), (10, 'Oktober'), (11, 'November'), (12, 'Desember')
]


# ============================================================
# 1. LAPORAN PESERTA (Mandiri)
# ============================================================

@login_required(login_url='/')
def laporan_peserta(request):
    """Laporan mandiri peserta magang dengan tab Ringkasan, Harian, dan Bulanan"""
    
    try:
        peserta = Peserta.objects.get(user=request.user)
    except Peserta.DoesNotExist:
        messages.error(request, 'Anda tidak terdaftar sebagai peserta magang!')
        return redirect('/dashboard/peserta/')
    
    if peserta.status != 'aktif':
        status_label = dict(Peserta.STATUS_CHOICES).get(peserta.status, peserta.status)
        messages.warning(request, f'Fitur Laporan hanya dapat diakses setelah akun Anda disetujui (Status: {status_label}).')
        return redirect('/dashboard/peserta/')
    
    active_tab = request.GET.get('tab', 'ringkasan')
    today = date.today()
    
    # ---------------- TAB 1: RINGKASAN UMUM ----------------
    total_absensi = Absensi.objects.filter(peserta=peserta).count()
    total_logbook = Logbook.objects.filter(peserta=peserta).count()
    
    if peserta.tanggal_mulai:
        hari_ke = (today - peserta.tanggal_mulai).days + 1
        if hari_ke < 1:
            hari_ke = 0
    else:
        hari_ke = 0
    
    penilaian = Penilaian.objects.filter(peserta=peserta).first()
    
    status_absensi = Absensi.objects.filter(peserta=peserta).values('status').annotate(
        total=models.Count('id')
    )
    for item in status_absensi:
        item['get_status_display'] = dict(Absensi.STATUS_CHOICES).get(item['status'], item['status'])
    
    riwayat_absensi_ringkas = Absensi.objects.filter(peserta=peserta).order_by('-tanggal')[:15]
    logbooks_ringkas = Logbook.objects.filter(peserta=peserta).order_by('-tanggal')[:10]
    
    # ---------------- TAB 2: LAPORAN HARIAN ----------------
    selected_date_str = request.GET.get('tanggal', today.strftime('%Y-%m-%d'))
    try:
        selected_date = datetime.strptime(selected_date_str, '%Y-%m-%d').date()
    except ValueError:
        selected_date = today
        selected_date_str = today.strftime('%Y-%m-%d')
        
    absensi_harian = Absensi.objects.filter(peserta=peserta, tanggal=selected_date).first()
    logbook_harian = Logbook.objects.filter(peserta=peserta, tanggal=selected_date)
    
    # ---------------- TAB 3: LAPORAN BULANAN ----------------
    selected_month = int(request.GET.get('bulan', today.month))
    selected_year = int(request.GET.get('tahun', today.year))
    
    # Ambil data absensi dan logbook pada bulan yang dipilih
    absensi_bulanan = Absensi.objects.filter(
        peserta=peserta,
        tanggal__year=selected_year,
        tanggal__month=selected_month
    ).order_by('tanggal')
    
    logbook_bulanan = Logbook.objects.filter(
        peserta=peserta,
        tanggal__year=selected_year,
        tanggal__month=selected_month
    ).order_by('tanggal')
    
    # Statistik bulanan peserta
    hadir_bln = absensi_bulanan.filter(status='hadir').count()
    izin_bln = absensi_bulanan.filter(status='izin').count()
    sakit_bln = absensi_bulanan.filter(status='sakit').count()
    alpha_bln = absensi_bulanan.filter(status='alpha').count()
    total_absen_bln = absensi_bulanan.count()
    
    context = {
        'peserta': peserta,
        'active_tab': active_tab,
        'today': today,
        
        # Tab Ringkasan
        'total_absensi': total_absensi,
        'total_logbook': total_logbook,
        'hari_ke': hari_ke,
        'penilaian': penilaian,
        'status_absensi': status_absensi,
        'riwayat_absensi_ringkas': riwayat_absensi_ringkas,
        'logbooks_ringkas': logbooks_ringkas,
        
        # Tab Harian
        'selected_date': selected_date,
        'selected_date_str': selected_date_str,
        'absensi_harian': absensi_harian,
        'logbook_harian': logbook_harian,
        
        # Tab Bulanan
        'selected_month': selected_month,
        'selected_year': selected_year,
        'month_names': MONTH_NAMES,
        'available_years': range(today.year - 2, today.year + 2),
        'absensi_bulanan': absensi_bulanan,
        'logbook_bulanan': logbook_bulanan,
        'hadir_bln': hadir_bln,
        'izin_bln': izin_bln,
        'sakit_bln': sakit_bln,
        'alpha_bln': alpha_bln,
        'total_absen_bln': total_absen_bln,
        'total_logbook_bln': logbook_bulanan.count(),
    }
    return render(request, 'laporan_peserta.html', context)


# ============================================================
# 2. LAPORAN ADMIN (Semua Peserta)
# ============================================================

@login_required(login_url='/')
def laporan_admin(request):
    """Laporan admin dengan tab Ringkasan, Laporan Harian, dan Laporan Bulanan"""
    
    if not (request.user.is_superuser or request.user.groups.filter(name='Admin').exists()):
        messages.error(request, 'Anda tidak memiliki akses ke halaman Laporan Admin!')
        return redirect('/dashboard/admin/')
    
    active_tab = request.GET.get('tab', 'ringkasan')
    today = date.today()
    
    # ---------------- TAB 1: RINGKASAN UMUM ----------------
    total_peserta = Peserta.objects.count()
    total_peserta_aktif = Peserta.objects.filter(status='aktif').count()
    total_absensi_hari_ini = Absensi.objects.filter(tanggal=today).count()
    
    bidang_data = Peserta.objects.values('bidang_penempatan').annotate(
        total=models.Count('id')
    )
    mentor_data = Peserta.objects.values('mentor__first_name', 'mentor__last_name').annotate(
        total=models.Count('id')
    )
    absensi_terakhir = Absensi.objects.all().order_by('-tanggal')[:20]
    
    # ---------------- TAB 2: LAPORAN HARIAN (SEMUA PESERTA) ----------------
    selected_date_str = request.GET.get('tanggal', today.strftime('%Y-%m-%d'))
    try:
        selected_date = datetime.strptime(selected_date_str, '%Y-%m-%d').date()
    except ValueError:
        selected_date = today
        selected_date_str = today.strftime('%Y-%m-%d')
    
    peserta_aktif_list = Peserta.objects.filter(status='aktif').select_related('user', 'mentor')
    all_peserta_filter = peserta_aktif_list.order_by('user__first_name')
    
    peserta_id = request.GET.get('peserta_id')
    if peserta_id:
        try:
            peserta_id = int(peserta_id)
            peserta_aktif_list_filtered = peserta_aktif_list.filter(id=peserta_id)
        except ValueError:
            peserta_aktif_list_filtered = peserta_aktif_list
            peserta_id = None
    else:
        peserta_aktif_list_filtered = peserta_aktif_list
        peserta_id = None

    absensi_harian_map = {
        a.peserta_id: a for a in Absensi.objects.filter(tanggal=selected_date)
    }
    
    rekap_harian_peserta = []
    count_hadir_hr = 0
    count_izin_hr = 0
    count_sakit_hr = 0
    count_alpha_hr = 0
    count_belum_hr = 0
    
    for p in peserta_aktif_list_filtered:
        absen = absensi_harian_map.get(p.id)
        status_absen = absen.status if absen else 'belum'
        if status_absen == 'hadir':
            count_hadir_hr += 1
        elif status_absen == 'izin':
            count_izin_hr += 1
        elif status_absen == 'sakit':
            count_sakit_hr += 1
        elif status_absen == 'alpha':
            count_alpha_hr += 1
        else:
            count_belum_hr += 1
            
        rekap_harian_peserta.append({
            'peserta': p,
            'absen': absen,
            'status': status_absen,
        })
    
    logbooks_harian_all = Logbook.objects.filter(tanggal=selected_date).select_related('peserta', 'peserta__user')
    if peserta_id:
        logbooks_harian_all = logbooks_harian_all.filter(peserta_id=peserta_id)
    
    # ---------------- TAB 3: LAPORAN BULANAN (REKAPITULASI) ----------------
    selected_month = int(request.GET.get('bulan', today.month))
    selected_year = int(request.GET.get('tahun', today.year))
    
    # Ambil semua absensi & logbook pada bulan tersebut
    absensi_bln_qs = Absensi.objects.filter(tanggal__year=selected_year, tanggal__month=selected_month)
    logbook_bln_qs = Logbook.objects.filter(tanggal__year=selected_year, tanggal__month=selected_month)
    
    if peserta_id:
        absensi_bln_qs = absensi_bln_qs.filter(peserta_id=peserta_id)
        logbook_bln_qs = logbook_bln_qs.filter(peserta_id=peserta_id)
        
    rekap_bulanan_peserta = []
    total_hadir_all_bln = 0
    total_izin_all_bln = 0
    total_sakit_all_bln = 0
    total_alpha_all_bln = 0
    
    for p in peserta_aktif_list_filtered:
        p_absensi = absensi_bln_qs.filter(peserta=p)
        h = p_absensi.filter(status='hadir').count()
        i = p_absensi.filter(status='izin').count()
        s = p_absensi.filter(status='sakit').count()
        a = p_absensi.filter(status='alpha').count()
        tot_absen = p_absensi.count()
        
        total_hadir_all_bln += h
        total_izin_all_bln += i
        total_sakit_all_bln += s
        total_alpha_all_bln += a
        
        persentase = round((h / tot_absen * 100), 1) if tot_absen > 0 else 0
        tot_log = logbook_bln_qs.filter(peserta=p).count()
        
        rekap_bulanan_peserta.append({
            'peserta': p,
            'hadir': h,
            'izin': i,
            'sakit': s,
            'alpha': a,
            'total_absen': tot_absen,
            'persentase_hadir': persentase,
            'total_logbook': tot_log,
        })
    
    context = {
        'active_tab': active_tab,
        'today': today,
        
        # Filter Dropdown
        'all_peserta_filter': all_peserta_filter,
        'selected_peserta_id': peserta_id,
        
        # Tab Ringkasan
        'total_peserta': total_peserta,
        'total_peserta_aktif': total_peserta_aktif,
        'total_absensi_hari_ini': total_absensi_hari_ini,
        'bidang_data': bidang_data,
        'mentor_data': mentor_data,
        'absensi_terakhir': absensi_terakhir,
        
        # Tab Harian
        'selected_date': selected_date,
        'selected_date_str': selected_date_str,
        'rekap_harian_peserta': rekap_harian_peserta,
        'count_hadir_hr': count_hadir_hr,
        'count_izin_hr': count_izin_hr,
        'count_sakit_hr': count_sakit_hr,
        'count_alpha_hr': count_alpha_hr,
        'count_belum_hr': count_belum_hr,
        'logbooks_harian_all': logbooks_harian_all,
        
        # Tab Bulanan
        'selected_month': selected_month,
        'selected_year': selected_year,
        'month_names': MONTH_NAMES,
        'selected_month_name': dict(MONTH_NAMES).get(selected_month, ''),
        'available_years': range(today.year - 2, today.year + 2),
        'rekap_bulanan_peserta': rekap_bulanan_peserta,
        'total_hadir_all_bln': total_hadir_all_bln,
        'total_izin_all_bln': total_izin_all_bln,
        'total_sakit_all_bln': total_sakit_all_bln,
        'total_alpha_all_bln': total_alpha_all_bln,
        'total_logbook_all_bln': logbook_bln_qs.count(),
    }
    return render(request, 'laporan_admin.html', context)


# ============================================================
# 3. LAPORAN MENTOR (Peserta Bimbingan)
# ============================================================

@login_required(login_url='/')
def laporan_mentor(request):
    """Laporan khusus untuk mentor (hanya peserta bimbingannya)"""
    
    if not (request.user.groups.filter(name='Mentor').exists() or request.user.is_superuser):
        messages.error(request, 'Anda tidak memiliki akses ke halaman Laporan Mentor!')
        return redirect('/dashboard/mentor/')
    
    active_tab = request.GET.get('tab', 'ringkasan')
    today = date.today()
    
    bimbingan_list = Peserta.objects.filter(mentor=request.user, status='aktif').select_related('user')
    total_bimbingan = bimbingan_list.count()
    all_bimbingan_filter = bimbingan_list.order_by('user__first_name')
    
    peserta_id = request.GET.get('peserta_id')
    if peserta_id:
        try:
            peserta_id = int(peserta_id)
            bimbingan_list_filtered = bimbingan_list.filter(id=peserta_id)
        except ValueError:
            bimbingan_list_filtered = bimbingan_list
            peserta_id = None
    else:
        bimbingan_list_filtered = bimbingan_list
        peserta_id = None

    # ---------------- TAB 1: RINGKASAN UMUM ----------------
    absensi_hari_ini_mentor = Absensi.objects.filter(
        peserta__in=bimbingan_list, tanggal=today
    ).count()
    
    logbook_pending_mentor = Logbook.objects.filter(
        peserta__in=bimbingan_list, status='dikirim'
    ).count()
    
    # ---------------- TAB 2: LAPORAN HARIAN ----------------
    selected_date_str = request.GET.get('tanggal', today.strftime('%Y-%m-%d'))
    try:
        selected_date = datetime.strptime(selected_date_str, '%Y-%m-%d').date()
    except ValueError:
        selected_date = today
        selected_date_str = today.strftime('%Y-%m-%d')
        
    absensi_harian_map = {
        a.peserta_id: a for a in Absensi.objects.filter(peserta__in=bimbingan_list, tanggal=selected_date)
    }
    
    rekap_harian_mentor = []
    count_hadir_hr = 0
    count_izin_hr = 0
    count_sakit_hr = 0
    count_alpha_hr = 0
    count_belum_hr = 0
    
    for p in bimbingan_list_filtered:
        absen = absensi_harian_map.get(p.id)
        status_absen = absen.status if absen else 'belum'
        if status_absen == 'hadir':
            count_hadir_hr += 1
        elif status_absen == 'izin':
            count_izin_hr += 1
        elif status_absen == 'sakit':
            count_sakit_hr += 1
        elif status_absen == 'alpha':
            count_alpha_hr += 1
        else:
            count_belum_hr += 1
            
        rekap_harian_mentor.append({
            'peserta': p,
            'absen': absen,
            'status': status_absen,
        })
        
    logbooks_harian_mentor = Logbook.objects.filter(
        peserta__in=bimbingan_list_filtered, tanggal=selected_date
    ).select_related('peserta', 'peserta__user')
    
    # ---------------- TAB 3: LAPORAN BULANAN ----------------
    selected_month = int(request.GET.get('bulan', today.month))
    selected_year = int(request.GET.get('tahun', today.year))
    
    absensi_bln_qs = Absensi.objects.filter(
        peserta__in=bimbingan_list_filtered,
        tanggal__year=selected_year,
        tanggal__month=selected_month
    )
    logbook_bln_qs = Logbook.objects.filter(
        peserta__in=bimbingan_list_filtered,
        tanggal__year=selected_year,
        tanggal__month=selected_month
    )
    
    rekap_bulanan_mentor = []
    for p in bimbingan_list_filtered:
        p_absensi = absensi_bln_qs.filter(peserta=p)
        h = p_absensi.filter(status='hadir').count()
        i = p_absensi.filter(status='izin').count()
        s = p_absensi.filter(status='sakit').count()
        a = p_absensi.filter(status='alpha').count()
        tot_absen = p_absensi.count()
        persentase = round((h / tot_absen * 100), 1) if tot_absen > 0 else 0
        tot_log = logbook_bln_qs.filter(peserta=p).count()
        
        rekap_bulanan_mentor.append({
            'peserta': p,
            'hadir': h,
            'izin': i,
            'sakit': s,
            'alpha': a,
            'total_absen': tot_absen,
            'persentase_hadir': persentase,
            'total_logbook': tot_log,
        })
        
    context = {
        'active_tab': active_tab,
        'today': today,
        'total_bimbingan': total_bimbingan,
        'absensi_hari_ini_mentor': absensi_hari_ini_mentor,
        'logbook_pending_mentor': logbook_pending_mentor,
        'bimbingan_list': bimbingan_list,
        
        # Filter Dropdown
        'all_bimbingan_filter': all_bimbingan_filter,
        'selected_peserta_id': peserta_id,
        
        # Tab Harian
        'selected_date': selected_date,
        'selected_date_str': selected_date_str,
        'rekap_harian_mentor': rekap_harian_mentor,
        'count_hadir_hr': count_hadir_hr,
        'count_izin_hr': count_izin_hr,
        'count_sakit_hr': count_sakit_hr,
        'count_alpha_hr': count_alpha_hr,
        'count_belum_hr': count_belum_hr,
        'logbooks_harian_mentor': logbooks_harian_mentor,
        
        # Tab Bulanan
        'selected_month': selected_month,
        'selected_year': selected_year,
        'month_names': MONTH_NAMES,
        'selected_month_name': dict(MONTH_NAMES).get(selected_month, ''),
        'available_years': range(today.year - 2, today.year + 2),
        'rekap_bulanan_mentor': rekap_bulanan_mentor,
        'total_logbook_mentor_bln': logbook_bln_qs.count(),
    }
    return render(request, 'laporan_mentor.html', context)


# ============================================================
# 4. EXPORT EXCEL - ADMIN
# ============================================================

@login_required(login_url='/')
def export_excel_admin(request):
    """Export laporan keseluruhan admin ke Excel"""
    if not (request.user.is_superuser or request.user.groups.filter(name='Admin').exists()):
        messages.error(request, 'Anda tidak memiliki akses!')
        return redirect('/dashboard/admin/')
    
    st = get_excel_styles()
    wb = Workbook()
    ws = wb.active
    ws.title = "Rekapitulasi Admin"
    
    ws.merge_cells('A1:F1')
    ws['A1'] = 'LAPORAN REKAPITULASI MAGANG - DISKOMINFOSANTIK'
    ws['A1'].font = Font(bold=True, size=16, color="1E3A8A")
    ws['A1'].alignment = st['center_align']
    
    # Ringkasan Umum
    ws['A3'] = 'RINGKASAN SISTEM'
    ws['A3'].font = st['section_font']
    ws['A3'].fill = st['section_fill']
    
    statistik = [
        ['Total Peserta Terdaftar', Peserta.objects.count()],
        ['Total Peserta Aktif', Peserta.objects.filter(status='aktif').count()],
        ['Total Logbook Terisi', Logbook.objects.count()],
        ['Total Data Absensi', Absensi.objects.count()],
        ['Tanggal Unduh', date.today().strftime('%d/%m/%Y')],
    ]
    for i, (k, v) in enumerate(statistik, start=4):
        ws[f'A{i}'] = k
        ws[f'B{i}'] = v
        ws[f'A{i}'].font = st['bold_font']
        
    # Tabel Peserta Aktif
    start_row = 11
    ws[f'A{start_row}'] = 'DAFTAR PESERTA MAGANG AKTIF'
    ws[f'A{start_row}'].font = st['section_font']
    ws[f'A{start_row}'].fill = st['section_fill']
    
    headers = ['No', 'Nama Peserta', 'NIM', 'Institusi', 'Bidang', 'Mentor', 'Tgl Mulai', 'Tgl Selesai']
    for col, h in enumerate(headers, 1):
        cell = ws.cell(row=start_row + 1, column=col, value=h)
        cell.font = st['header_font']
        cell.fill = st['header_fill']
        cell.alignment = st['center_align']
        cell.border = st['border']
        
    peserta_aktif = Peserta.objects.filter(status='aktif').select_related('user', 'mentor')
    for i, p in enumerate(peserta_aktif, 1):
        r = start_row + 1 + i
        ws.cell(row=r, column=1, value=i).border = st['border']
        ws.cell(row=r, column=2, value=p.user.get_full_name()).border = st['border']
        ws.cell(row=r, column=3, value=p.nim).border = st['border']
        ws.cell(row=r, column=4, value=p.institusi).border = st['border']
        ws.cell(row=r, column=5, value=p.bidang_penempatan).border = st['border']
        ws.cell(row=r, column=6, value=p.mentor.get_full_name() if p.mentor else '-').border = st['border']
        ws.cell(row=r, column=7, value=p.tanggal_mulai.strftime('%d/%m/%Y') if p.tanggal_mulai else '-').border = st['border']
        ws.cell(row=r, column=8, value=p.tanggal_selesai.strftime('%d/%m/%Y') if p.tanggal_selesai else '-').border = st['border']
        
    for col in range(1, 9):
        ws.column_dimensions[get_column_letter(col)].width = 20
        
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = f'attachment; filename=Laporan_Rekap_Admin_{date.today().strftime("%Y%m%d")}.xlsx'
    wb.save(response)
    return response


@login_required(login_url='/')
def export_excel_harian_admin(request):
    """Export laporan harian admin ke Excel"""
    if not (request.user.is_superuser or request.user.groups.filter(name='Admin').exists()):
        messages.error(request, 'Anda tidak memiliki akses!')
        return redirect('/dashboard/admin/')
        
    today = date.today()
    selected_date_str = request.GET.get('tanggal', today.strftime('%Y-%m-%d'))
    try:
        selected_date = datetime.strptime(selected_date_str, '%Y-%m-%d').date()
    except ValueError:
        selected_date = today
        
    st = get_excel_styles()
    wb = Workbook()
    
    # Sheet 1: Absensi Harian
    ws1 = wb.active
    ws1.title = "Absensi Harian"
    
    ws1.merge_cells('A1:G1')
    ws1['A1'] = f'LAPORAN PRESENSI HARIAN - {selected_date.strftime("%d %B %Y")}'
    ws1['A1'].font = Font(bold=True, size=15, color="1E3A8A")
    ws1['A1'].alignment = st['center_align']
    
    headers = ['No', 'Nama Peserta', 'NIM', 'Bidang', 'Check-in', 'Check-out', 'Status']
    for col, h in enumerate(headers, 1):
        cell = ws1.cell(row=3, column=col, value=h)
        cell.font = st['header_font']
        cell.fill = st['header_fill']
        cell.alignment = st['center_align']
        cell.border = st['border']
        
    peserta_aktif = Peserta.objects.filter(status='aktif').select_related('user')
    peserta_id = request.GET.get('peserta_id')
    if peserta_id:
        try:
            peserta_aktif = peserta_aktif.filter(id=int(peserta_id))
        except ValueError:
            pass
            
    absensi_map = {a.peserta_id: a for a in Absensi.objects.filter(tanggal=selected_date)}
    
    for i, p in enumerate(peserta_aktif, 1):
        r = 3 + i
        absen = absensi_map.get(p.id)
        ws1.cell(row=r, column=1, value=i).border = st['border']
        ws1.cell(row=r, column=2, value=p.user.get_full_name()).border = st['border']
        ws1.cell(row=r, column=3, value=p.nim).border = st['border']
        ws1.cell(row=r, column=4, value=p.bidang_penempatan).border = st['border']
        ws1.cell(row=r, column=5, value=absen.check_in.strftime('%H:%M') if (absen and absen.check_in) else '-').border = st['border']
        ws1.cell(row=r, column=6, value=absen.check_out.strftime('%H:%M') if (absen and absen.check_out) else '-').border = st['border']
        ws1.cell(row=r, column=7, value=absen.get_status_display() if absen else 'Belum Absen').border = st['border']
        
    for col in range(1, 8):
        ws1.column_dimensions[get_column_letter(col)].width = 20
        
    # Sheet 2: Logbook Harian
    ws2 = wb.create_sheet(title="Logbook Harian")
    ws2.merge_cells('A1:E1')
    ws2['A1'] = f'LAPORAN LOGBOOK KEGIATAN HARIAN - {selected_date.strftime("%d %B %Y")}'
    ws2['A1'].font = Font(bold=True, size=15, color="1E3A8A")
    ws2['A1'].alignment = st['center_align']
    
    logbook_headers = ['No', 'Nama Peserta', 'NIM', 'Kegiatan', 'Status']
    for col, h in enumerate(logbook_headers, 1):
        cell = ws2.cell(row=3, column=col, value=h)
        cell.font = st['header_font']
        cell.fill = st['header_fill']
        cell.alignment = st['center_align']
        cell.border = st['border']
        
    logbooks = Logbook.objects.filter(tanggal=selected_date).select_related('peserta', 'peserta__user')
    if peserta_id:
        try:
            logbooks = logbooks.filter(peserta_id=int(peserta_id))
        except ValueError:
            pass
            
    for i, log in enumerate(logbooks, 1):
        r = 3 + i
        ws2.cell(row=r, column=1, value=i).border = st['border']
        ws2.cell(row=r, column=2, value=log.peserta.user.get_full_name()).border = st['border']
        ws2.cell(row=r, column=3, value=log.peserta.nim).border = st['border']
        ws2.cell(row=r, column=4, value=log.kegiatan).border = st['border']
        ws2.cell(row=r, column=5, value=log.get_status_display()).border = st['border']
        
    for col in range(1, 6):
        ws2.column_dimensions[get_column_letter(col)].width = 25
        
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = f'attachment; filename=Laporan_Harian_Admin_{selected_date.strftime("%Y%m%d")}.xlsx'
    wb.save(response)
    return response


@login_required(login_url='/')
def export_excel_bulanan_admin(request):
    """Export rekapitulasi bulanan admin ke Excel"""
    if not (request.user.is_superuser or request.user.groups.filter(name='Admin').exists()):
        messages.error(request, 'Anda tidak memiliki akses!')
        return redirect('/dashboard/admin/')
        
    today = date.today()
    selected_month = int(request.GET.get('bulan', today.month))
    selected_year = int(request.GET.get('tahun', today.year))
    nama_bulan = dict(MONTH_NAMES).get(selected_month, str(selected_month))
    
    st = get_excel_styles()
    wb = Workbook()
    ws = wb.active
    ws.title = f"Rekap {nama_bulan} {selected_year}"
    
    ws.merge_cells('A1:I1')
    ws['A1'] = f'REKAPITULASI BULANAN PESERTA MAGANG - {nama_bulan.upper()} {selected_year}'
    ws['A1'].font = Font(bold=True, size=15, color="1E3A8A")
    ws['A1'].alignment = st['center_align']
    
    headers = ['No', 'Nama Peserta', 'NIM', 'Bidang', 'Hadir', 'Izin', 'Sakit', 'Alpha', '% Kehadiran', 'Total Logbook']
    for col, h in enumerate(headers, 1):
        cell = ws.cell(row=3, column=col, value=h)
        cell.font = st['header_font']
        cell.fill = st['header_fill']
        cell.alignment = st['center_align']
        cell.border = st['border']
        
    peserta_aktif = Peserta.objects.filter(status='aktif').select_related('user')
    peserta_id = request.GET.get('peserta_id')
    if peserta_id:
        try:
            peserta_aktif = peserta_aktif.filter(id=int(peserta_id))
        except ValueError:
            pass
            
    absensi_qs = Absensi.objects.filter(tanggal__year=selected_year, tanggal__month=selected_month)
    logbook_qs = Logbook.objects.filter(tanggal__year=selected_year, tanggal__month=selected_month)
    if peserta_id:
        try:
            absensi_qs = absensi_qs.filter(peserta_id=int(peserta_id))
            logbook_qs = logbook_qs.filter(peserta_id=int(peserta_id))
        except ValueError:
            pass
    
    for i, p in enumerate(peserta_aktif, 1):
        r = 3 + i
        p_absen = absensi_qs.filter(peserta=p)
        h = p_absen.filter(status='hadir').count()
        iz = p_absen.filter(status='izin').count()
        s = p_absen.filter(status='sakit').count()
        a = p_absen.filter(status='alpha').count()
        tot = p_absen.count()
        persen = round((h / tot * 100), 1) if tot > 0 else 0
        tot_log = logbook_qs.filter(peserta=p).count()
        
        ws.cell(row=r, column=1, value=i).border = st['border']
        ws.cell(row=r, column=2, value=p.user.get_full_name()).border = st['border']
        ws.cell(row=r, column=3, value=p.nim).border = st['border']
        ws.cell(row=r, column=4, value=p.bidang_penempatan).border = st['border']
        ws.cell(row=r, column=5, value=h).border = st['border']
        ws.cell(row=r, column=6, value=iz).border = st['border']
        ws.cell(row=r, column=7, value=s).border = st['border']
        ws.cell(row=r, column=8, value=a).border = st['border']
        ws.cell(row=r, column=9, value=f"{persen}%").border = st['border']
        ws.cell(row=r, column=10, value=tot_log).border = st['border']
        
    for col in range(1, 11):
        ws.column_dimensions[get_column_letter(col)].width = 18
        
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = f'attachment; filename=Laporan_Bulanan_Admin_{selected_year}_{selected_month:02d}.xlsx'
    wb.save(response)
    return response


# ============================================================
# 5. EXPORT EXCEL - MENTOR
# ============================================================

@login_required(login_url='/')
def export_excel_harian_mentor(request):
    """Export laporan harian bimbingan mentor ke Excel"""
    if not (request.user.groups.filter(name='Mentor').exists() or request.user.is_superuser):
        messages.error(request, 'Anda tidak memiliki akses!')
        return redirect('/dashboard/mentor/')
        
    today = date.today()
    selected_date_str = request.GET.get('tanggal', today.strftime('%Y-%m-%d'))
    try:
        selected_date = datetime.strptime(selected_date_str, '%Y-%m-%d').date()
    except ValueError:
        selected_date = today
        
    bimbingan = Peserta.objects.filter(mentor=request.user, status='aktif').select_related('user')
    peserta_id = request.GET.get('peserta_id')
    if peserta_id:
        try:
            bimbingan = bimbingan.filter(id=int(peserta_id))
        except ValueError:
            pass
            
    st = get_excel_styles()
    wb = Workbook()
    
    # Sheet 1: Absensi Harian Bimbingan
    ws1 = wb.active
    ws1.title = "Absensi Harian"
    ws1.merge_cells('A1:F1')
    ws1['A1'] = f'PRESENSI HARIAN BIMBINGAN - {selected_date.strftime("%d %B %Y")}'
    ws1['A1'].font = Font(bold=True, size=15, color="1E3A8A")
    ws1['A1'].alignment = st['center_align']
    
    headers = ['No', 'Nama Peserta', 'NIM', 'Check-in', 'Check-out', 'Status']
    for col, h in enumerate(headers, 1):
        cell = ws1.cell(row=3, column=col, value=h)
        cell.font = st['header_font']
        cell.fill = st['header_fill']
        cell.alignment = st['center_align']
        cell.border = st['border']
        
    absensi_map = {a.peserta_id: a for a in Absensi.objects.filter(peserta__in=bimbingan, tanggal=selected_date)}
    for i, p in enumerate(bimbingan, 1):
        r = 3 + i
        absen = absensi_map.get(p.id)
        ws1.cell(row=r, column=1, value=i).border = st['border']
        ws1.cell(row=r, column=2, value=p.user.get_full_name()).border = st['border']
        ws1.cell(row=r, column=3, value=p.nim).border = st['border']
        ws1.cell(row=r, column=4, value=absen.check_in.strftime('%H:%M') if (absen and absen.check_in) else '-').border = st['border']
        ws1.cell(row=r, column=5, value=absen.check_out.strftime('%H:%M') if (absen and absen.check_out) else '-').border = st['border']
        ws1.cell(row=r, column=6, value=absen.get_status_display() if absen else 'Belum Absen').border = st['border']
        
    for col in range(1, 7):
        ws1.column_dimensions[get_column_letter(col)].width = 20
        
    # Sheet 2: Logbook Harian Bimbingan
    ws2 = wb.create_sheet(title="Logbook Harian")
    ws2.merge_cells('A1:E1')
    ws2['A1'] = f'LOGBOOK HARIAN BIMBINGAN - {selected_date.strftime("%d %B %Y")}'
    ws2['A1'].font = Font(bold=True, size=15, color="1E3A8A")
    ws2['A1'].alignment = st['center_align']
    
    logbook_headers = ['No', 'Nama Peserta', 'NIM', 'Kegiatan', 'Status Verifikasi']
    for col, h in enumerate(logbook_headers, 1):
        cell = ws2.cell(row=3, column=col, value=h)
        cell.font = st['header_font']
        cell.fill = st['header_fill']
        cell.alignment = st['center_align']
        cell.border = st['border']
        
    logbooks = Logbook.objects.filter(peserta__in=bimbingan, tanggal=selected_date).select_related('peserta', 'peserta__user')
    for i, log in enumerate(logbooks, 1):
        r = 3 + i
        ws2.cell(row=r, column=1, value=i).border = st['border']
        ws2.cell(row=r, column=2, value=log.peserta.user.get_full_name()).border = st['border']
        ws2.cell(row=r, column=3, value=log.peserta.nim).border = st['border']
        ws2.cell(row=r, column=4, value=log.kegiatan).border = st['border']
        ws2.cell(row=r, column=5, value=log.get_status_display()).border = st['border']
        
    for col in range(1, 6):
        ws2.column_dimensions[get_column_letter(col)].width = 25
        
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = f'attachment; filename=Laporan_Harian_Mentor_{selected_date.strftime("%Y%m%d")}.xlsx'
    wb.save(response)
    return response


@login_required(login_url='/')
def export_excel_bulanan_mentor(request):
    """Export rekap bulanan bimbingan mentor ke Excel"""
    if not (request.user.groups.filter(name='Mentor').exists() or request.user.is_superuser):
        messages.error(request, 'Anda tidak memiliki akses!')
        return redirect('/dashboard/mentor/')
        
    today = date.today()
    selected_month = int(request.GET.get('bulan', today.month))
    selected_year = int(request.GET.get('tahun', today.year))
    nama_bulan = dict(MONTH_NAMES).get(selected_month, str(selected_month))
    
    bimbingan = Peserta.objects.filter(mentor=request.user, status='aktif').select_related('user')
    peserta_id = request.GET.get('peserta_id')
    if peserta_id:
        try:
            bimbingan = bimbingan.filter(id=int(peserta_id))
        except ValueError:
            pass
            
    st = get_excel_styles()
    wb = Workbook()
    ws = wb.active
    ws.title = f"Rekap {nama_bulan} {selected_year}"
    
    ws.merge_cells('A1:I1')
    ws['A1'] = f'REKAPITULASI BULANAN BIMBINGAN - {nama_bulan.upper()} {selected_year}'
    ws['A1'].font = Font(bold=True, size=15, color="1E3A8A")
    ws['A1'].alignment = st['center_align']
    
    headers = ['No', 'Nama Peserta', 'NIM', 'Hadir', 'Izin', 'Sakit', 'Alpha', '% Kehadiran', 'Total Logbook']
    for col, h in enumerate(headers, 1):
        cell = ws.cell(row=3, column=col, value=h)
        cell.font = st['header_font']
        cell.fill = st['header_fill']
        cell.alignment = st['center_align']
        cell.border = st['border']
        
    absensi_qs = Absensi.objects.filter(peserta__in=bimbingan, tanggal__year=selected_year, tanggal__month=selected_month)
    logbook_qs = Logbook.objects.filter(peserta__in=bimbingan, tanggal__year=selected_year, tanggal__month=selected_month)
    
    for i, p in enumerate(bimbingan, 1):
        r = 3 + i
        p_absen = absensi_qs.filter(peserta=p)
        h = p_absen.filter(status='hadir').count()
        iz = p_absen.filter(status='izin').count()
        s = p_absen.filter(status='sakit').count()
        a = p_absen.filter(status='alpha').count()
        tot = p_absen.count()
        persen = round((h / tot * 100), 1) if tot > 0 else 0
        tot_log = logbook_qs.filter(peserta=p).count()
        
        ws.cell(row=r, column=1, value=i).border = st['border']
        ws.cell(row=r, column=2, value=p.user.get_full_name()).border = st['border']
        ws.cell(row=r, column=3, value=p.nim).border = st['border']
        ws.cell(row=r, column=4, value=h).border = st['border']
        ws.cell(row=r, column=5, value=iz).border = st['border']
        ws.cell(row=r, column=6, value=s).border = st['border']
        ws.cell(row=r, column=7, value=a).border = st['border']
        ws.cell(row=r, column=8, value=f"{persen}%").border = st['border']
        ws.cell(row=r, column=9, value=tot_log).border = st['border']
        
    for col in range(1, 10):
        ws.column_dimensions[get_column_letter(col)].width = 20
        
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = f'attachment; filename=Laporan_Bulanan_Mentor_{selected_year}_{selected_month:02d}.xlsx'
    wb.save(response)
    return response


# ============================================================
# 6. EXPORT EXCEL - PESERTA (Lengkap / Bulanan / Harian)
# ============================================================

@login_required(login_url='/')
def export_excel_peserta(request):
    """Export laporan peserta ke Excel (bisa all / bulanan)"""
    try:
        peserta = Peserta.objects.get(user=request.user)
    except Peserta.DoesNotExist:
        messages.error(request, 'Anda tidak terdaftar sebagai peserta magang!')
        return redirect('/dashboard/peserta/')
    
    if peserta.status != 'aktif':
        status_label = dict(Peserta.STATUS_CHOICES).get(peserta.status, peserta.status)
        messages.warning(request, f'Fitur Ekspor Laporan hanya dapat diakses setelah akun Anda disetujui (Status: {status_label}).')
        return redirect('/dashboard/peserta/')
    
    tipe = request.GET.get('tipe', 'all')
    st = get_excel_styles()
    wb = Workbook()
    ws = wb.active
    ws.title = "Laporan Magang"
    
    # Header Utama
    ws.merge_cells('A1:F1')
    ws['A1'] = 'LAPORAN MAGANG - DISKOMINFOSANTIK'
    ws['A1'].font = Font(bold=True, size=16, color="1E3A8A")
    ws['A1'].alignment = st['center_align']
    
    # Data Diri
    row = 3
    ws[f'A{row}'] = 'DATA DIRI PESERTA'
    ws[f'A{row}'].font = st['section_font']
    ws[f'A{row}'].fill = st['section_fill']
    
    data_diri = [
        ['Nama Lengkap', peserta.user.get_full_name()],
        ['NIM', peserta.nim],
        ['Institusi / Kampus', peserta.institusi],
        ['Jurusan', peserta.jurusan],
        ['Bidang Penempatan', peserta.bidang_penempatan],
        ['Mentor Pembimbing', peserta.mentor.get_full_name() if peserta.mentor else '-'],
        ['Periode Magang', f"{peserta.tanggal_mulai.strftime('%d/%m/%Y') if peserta.tanggal_mulai else '-'} s/d {peserta.tanggal_selesai.strftime('%d/%m/%Y') if peserta.tanggal_selesai else '-'}"],
    ]
    for i, (label, value) in enumerate(data_diri):
        r = row + i + 1
        ws[f'A{r}'] = label
        ws[f'B{r}'] = value
        ws[f'A{r}'].font = st['bold_font']
    
    row = row + len(data_diri) + 2
    
    # Absensi
    if tipe == 'bulanan':
        today = date.today()
        selected_month = int(request.GET.get('bulan', today.month))
        selected_year = int(request.GET.get('tahun', today.year))
        nama_bulan = dict(MONTH_NAMES).get(selected_month, str(selected_month))
        absensi_list = Absensi.objects.filter(peserta=peserta, tanggal__year=selected_year, tanggal__month=selected_month).order_by('tanggal')
        logbooks = Logbook.objects.filter(peserta=peserta, tanggal__year=selected_year, tanggal__month=selected_month).order_by('tanggal')
        judul_absen = f'REKAPITULASI ABSENSI BULAN {nama_bulan.upper()} {selected_year}'
        judul_logbook = f'LOGBOOK KEGIATAN BULAN {nama_bulan.upper()} {selected_year}'
    else:
        absensi_list = Absensi.objects.filter(peserta=peserta).order_by('-tanggal')[:50]
        logbooks = Logbook.objects.filter(peserta=peserta).order_by('-tanggal')[:50]
        judul_absen = 'RIWAYAT ABSENSI TERAKHIR'
        judul_logbook = 'LOGBOOK KEGIATAN TERAKHIR'
        
    # Section Absensi
    ws[f'A{row}'] = judul_absen
    ws[f'A{row}'].font = st['section_font']
    ws[f'A{row}'].fill = st['section_fill']
    
    headers_absen = ['No', 'Tanggal', 'Check-in', 'Check-out', 'Status']
    for col, h in enumerate(headers_absen, 1):
        cell = ws.cell(row=row + 1, column=col, value=h)
        cell.font = st['header_font']
        cell.fill = st['header_fill']
        cell.alignment = st['center_align']
        cell.border = st['border']
        
    for i, a in enumerate(absensi_list, 1):
        r = row + 1 + i
        ws.cell(row=r, column=1, value=i).border = st['border']
        ws.cell(row=r, column=2, value=a.tanggal.strftime('%d/%m/%Y')).border = st['border']
        ws.cell(row=r, column=3, value=a.check_in.strftime('%H:%M') if a.check_in else '-').border = st['border']
        ws.cell(row=r, column=4, value=a.check_out.strftime('%H:%M') if a.check_out else '-').border = st['border']
        ws.cell(row=r, column=5, value=a.get_status_display()).border = st['border']
        
    row = row + (len(absensi_list) if absensi_list else 1) + 3
    
    # Section Logbook
    ws[f'A{row}'] = judul_logbook
    ws[f'A{row}'].font = st['section_font']
    ws[f'A{row}'].fill = st['section_fill']
    
    headers_log = ['No', 'Tanggal', 'Kegiatan', 'Status Verifikasi']
    for col, h in enumerate(headers_log, 1):
        cell = ws.cell(row=row + 1, column=col, value=h)
        cell.font = st['header_font']
        cell.fill = st['header_fill']
        cell.alignment = st['center_align']
        cell.border = st['border']
        
    for i, log in enumerate(logbooks, 1):
        r = row + 1 + i
        ws.cell(row=r, column=1, value=i).border = st['border']
        ws.cell(row=r, column=2, value=log.tanggal.strftime('%d/%m/%Y')).border = st['border']
        ws.cell(row=r, column=3, value=log.kegiatan).border = st['border']
        ws.cell(row=r, column=4, value=log.get_status_display()).border = st['border']
        
    for col in range(1, 6):
        ws.column_dimensions[get_column_letter(col)].width = 22
        
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    filename = f'Laporan_Magang_{peserta.user.get_full_name()}_{tipe}_{date.today().strftime("%Y%m%d")}.xlsx'
    response['Content-Disposition'] = f'attachment; filename={filename}'
    wb.save(response)
    return response