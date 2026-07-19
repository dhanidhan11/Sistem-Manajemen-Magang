# Sistem Manajemen Magang (SMM)

Sistem Manajemen Magang (SMM) adalah platform berbasis web yang dibangun menggunakan framework **Django 6.0** dan database **MySQL**. Sistem ini dirancang untuk mendigitalisasi dan mempermudah alur kerja program magang, menghubungkan interaksi antara Admin, Mentor, dan Peserta Magang secara real-time.

---

## 👥 Hak Akses & Fitur Utama

Sistem ini memiliki 3 peran (roles) utama dengan tanggung jawab sebagai berikut:

### 1. Admin
*   **Manajemen Akun:** Mengelola pendaftaran akun, data Peserta, dan data Mentor.
*   **Monitoring Sistem:** Melihat statistik aktivitas secara keseluruhan.
*   **Verifikasi:** Mengelola grup dan hak aksess pengguna.

### 2. Mentor
*   **Manajemen Tugas:** Membuat tugas baru, memberikan instruksi, batas waktu, dan mengunggah dokumen referensi.
*   **Verifikasi Logbook:** Memeriksa dan memverifikasi logbook harian yang diisi oleh peserta magang.
*   **Penilaian:** Memberikan nilai dan umpan balik (feedback) akhir terhadap kinerja peserta magang.

### 3. Peserta Magang
*   **Absensi Harian:** Melakukan presensi masuk (Clock In) dan presensi keluar (Clock Out) secara harian.
*   **Logbook Harian:** Mengisi catatan aktivitas harian beserta bukti kegiatan untuk diverifikasi oleh mentor.
*   **Pengerjaan Tugas & Projek:** Mengunduh tugas, mengirimkan tautan (link) tugas/projek, dan memantau status tugas (Belum -> Proses -> Selesai).
*   **Laporan & Dashboard:** Memantau kemajuan magang harian dan akumulasi nilai akhir.

---

## 🛠️ Teknologi & Dependensi

*   **Core Framework:** Django 6.0.6 (Python)
*   **Database:** MySQL (direkomendasikan menggunakan Laragon atau XAMPP)
*   **Aset & Media:** Pillow (Pemrosesan Gambar)
*   **Ekspor Data:** Openpyxl (untuk manipulasi dokumen excel)
*   **Desain & UI:** HTML5, CSS3 (Custom styling, modern layout, navbar responsif)

---

## 🚀 Langkah Instalasi & Menjalankan Proyek

Ikuti langkah-langkah di bawah ini untuk menjalankan proyek ini di lingkungan lokal Anda:

### 1. Prasyarat (Prerequisites)
Pastikan Anda sudah menginstal:
*   [Python 3.10+](https://www.python.org/downloads/)
*   [MySQL Server / Laragon / XAMPP](https://laragon.org/)
*   [Git](https://git-scm.com/)

### 2. Clone Repositori
Silakan klon repositori ini ke komputer lokal Anda:
```bash
git clone https://github.com/dhanidhan11/Sistem-Manajemen-Magang.git
cd Sistem-Manajemen-Magang
```

### 3. Buat dan Aktifkan Virtual Environment
Buat ruang kerja virtual terisolasi untuk dependensi Python:
```powershell
# Untuk Windows (PowerShell)
python -m venv venv
.\venv\Scripts\activate
```

### 4. Instal Dependensi
Instal pustaka Python yang dibutuhkan:
```bash
pip install -r requirements.txt
pip install mysqlclient
```
*(Catatan: Pastikan server database MySQL Anda sudah berjalan sebelum menginstal `mysqlclient` agar proses kompilasi berjalan lancar).*

### 5. Konfigurasi Database MySQL
1. Buka MySQL Client Anda (seperti phpMyAdmin atau HeidiSQL).
2. Buat database baru dengan nama:
   ```sql
   CREATE DATABASE db_magang;
   ```
3. Sesuaikan username dan password database pada file `manajemen_magang/settings.py` pada bagian objek `DATABASES` jika berbeda dengan default (`root` tanpa password):
   ```python
   DATABASES = {
       'default': {
           'ENGINE': 'django.db.backends.mysql',
           'NAME': 'db_magang',
           'USER': 'root',
           'PASSWORD': '',  # Isi password database Anda jika ada
           'HOST': '127.0.0.1',
           'PORT': '3306',
       }
   }
   ```

### 6. Melakukan Migrasi Database
Jalankan perintah migrasi Django untuk membuat tabel-tabel di database MySQL:
```bash
python manage.py migrate
```

### 7. Inisialisasi Grup & Data Awal (Opsional)
Jalankan perintah kustom untuk menginisialisasi grup pengguna (**Admin**, **Mentor**, **Peserta**):
```bash
python manage.py create_groups
```

Buat juga akun administrator (super-user) untuk dapat masuk ke menu admin panel Django:
```bash
python manage.py createsuperuser
```

### 8. Jalankan Server Lokal
Nyalakan server pengembangan Django:
```bash
python manage.py runserver
```
Buka browser Anda dan akses: [http://127.0.0.1:8000/](http://127.0.0.1:8000/)

---

## 📂 Struktur Folder Proyek
*   `absensi/` - Aplikasi untuk fitur absensi peserta magang.
*   `logbook/` - Aplikasi untuk pengisian & verifikasi logbook harian.
*   `penilaian/` - Aplikasi untuk penilaian akhir kinerja magang.
*   `peserta/` - Aplikasi manajemen biodata peserta magang.
*   `projek/` - Aplikasi manajemen tugas berbasis projek.
*   `tugas/` - Aplikasi pembuatan tugas oleh mentor dan pengumpulan tugas oleh peserta.
*   `users/` - Aplikasi autentikasi, manajemen profil, dan dashboard.
*   `manajemen_magang/` - Konfigurasi utama Django (settings, urls, wsgi).
*   `templates/` - Berkas tampilan (UI) berbasis HTML.
*   `static/` - Berkas statis pendukung (CSS, Javascript, Gambar UI).
