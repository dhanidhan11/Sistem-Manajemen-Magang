# LAPORAN HASIL PENGUJIAN BLACK BOX TESTING
## SISTEM MANAJEMEN MAGANG (DJANGO FRAMEWORK)

---

## 1. PENDAHULUAN

### 1.1 Deskripsi Pengujian
Pengujian *Black Box* (*Black Box Testing*) ini bertujuan untuk menguji fungsionalitas aplikasi **Sistem Manajemen Magang** tanpa melihat struktur kode internal program. Pengujian dilakukan dengan memberikan berbagai variasi masukan (*input data*), mengeksekusi fitur antarmuka (*UI/UX*), dan mengamati keluaran (*output/behavior*) sistem apakah telah sesuai dengan spesifikasi kebutuhan pengguna (*functional requirements*).

### 1.2 Lingkup Pengujian
Pengujian mencakup seluruh modul utama yang diakses oleh 3 aktor pengguna (**Peserta**, **Mentor**, dan **Admin**):
1. **Modul Autentikasi & Registrasi**: Login, Logout, Registrasi Peserta, Verifikasi Akun.
2. **Modul Kelola Data User**: CRUD Data Peserta, CRUD Data Mentor, Edit Profil User.
3. **Modul Absensi**: Presensi Harian, Check-in, Check-out, Monitoring & Edit Presensi.
4. **Modul Tugas**: Pembuatan Tugas, Pembagian Tugas, Submisi Tugas (File/Link), Penilaian Tugas.
5. **Modul Logbook**: Pengisian Jurnal Kegiatan Harian, Upload Dokumentasi, Verifikasi/Revisi Mentor.
6. **Modul Penilaian**: Evaluasi Akhir (7 Kriteria), Perhitungan Otomatis `total_nilai`, Transkrip Nilai.
7. **Modul Projek Magang**: Sinkronisasi Tugas ke Projek, Kelola Repository/Demo Link.
8. **Modul Laporan & Export Data**: Generasi Rekapitulasi & Export Excel/PDF.

### 1.3 Metode Pengujian
- **Equivalence Partitioning**: Membagi data masukan menjadi kelas-kelas data valid dan tidak valid.
- **Boundary Value Analysis**: Menguji batas nilai minimal dan maksimal pada field masukan.
- **Decision Table Testing**: Menguji kombinasi logika hak akses (*role-based authorization*).

---

## 2. REKAPITULASI HASIL PENGUJIAN

| No | Modul / Fitur | Jumlah Test Case | Pass | Fail | Persentase Keberhasilan |
|---|---|:---:|:---:|:---:|:---:|
| 1 | Autentikasi & Registrasi | 6 | 6 | 0 | 100% |
| 2 | Manajemen Peserta & Mentor | 6 | 6 | 0 | 100% |
| 3 | Presensi & Absensi | 5 | 5 | 0 | 100% |
| 4 | Manajemen Tugas | 6 | 6 | 0 | 100% |
| 5 | Jurnal Logbook Harian | 5 | 5 | 0 | 100% |
| 6 | Penilaian Evaluasi Akhir | 4 | 4 | 0 | 100% |
| 7 | Manajemen Projek Magang | 3 | 3 | 0 | 100% |
| 8 | Laporan & Export Excel | 3 | 3 | 0 | 100% |
| **TOTAL** | **Seluruh Fitur Sistem** | **38** | **38** | **0** | **100%** |

---

## 3. TABEL DETAIL TEST CASE & HASIL PENGUJIAN

### 3.1 Modul Autentikasi & Registrasi Akun

| ID Test | Skenario Pengujian | Input Data | Hasil yang Diharapkan | Hasil Pengujian Sebenarnya | Status |
|---|---|---|---|---|:---:|
| **AUTH-01** | Registrasi Peserta baru dengan data valid | NIM: `210101`, Nama: `Budi`, Email: `budi@gmail.com`, Pass: `Pass123!`, Bidang: `Aptika` | Akun tersimpan dengan status `terdaftar` (pending) & redirect ke halaman login dengan notifikasi sukses. | Sistem menyimpan akun `terdaftar` dan menampilkan alert sukses. | **PASS** |
| **AUTH-02** | Registrasi dengan NIM/Email yang sudah terdaftar | NIM yang sudah ada: `210101` atau Email yang sudah ada | Sistem menolak registrasi dan menampilkan pesan kesalahan "NIM/Email sudah digunakan". | Pesan error validasi muncul dan registrasi gagal. | **PASS** |
| **AUTH-03** | Login Peserta dengan kredensial benar dan status `aktif` | Username: `budi`, Password: `Pass123!` | Login berhasil, session dibuat, dan sistem mengarahkan ke `/users/dashboard/peserta/`. | Peserta berhasil masuk ke Dashboard Peserta. | **PASS** |
| **AUTH-04** | Login Peserta dengan kredensial benar tetapi status masih `terdaftar` (pending) | Username: `budi_pending`, Password: `Pass123!` | Login ditolak, sistem menampilkan notifikasi "Akun Anda belum disetujui/diaktifkan oleh Admin/Mentor". | Alert ditolak muncul, pengguna tetap di halaman login. | **PASS** |
| **AUTH-05** | Login dengan Password salah | Username: `budi`, Password: `SalahPassword` | Sistem menolak login dan menampilkan pesan "Username atau Password salah". | Pesan error kredensial salah berhasil ditampilkan. | **PASS** |
| **AUTH-06** | Logout Pengguna | Klik tombol "Logout" pada navbar | Session dihapus, pengguna berhasil dipindahkan ke halaman login `/users/`. | Session terhapus dan halaman login terbuka. | **PASS** |

---

### 3.2 Modul Manajemen Peserta & Mentor (Admin & Mentor)

| ID Test | Skenario Pengujian | Input Data | Hasil yang Diharapkan | Hasil Pengujian Sebenarnya | Status |
|---|---|---|---|---|:---:|
| **USER-01** | Admin membuat data Mentor baru | Username: `mentor_aptika`, Pass: `Mentor123!`, Bidang: `Aptika`, Gelar: `S.Kom.` | User mentor baru dan `MentorProfile` berhasil dibuat oleh sistem. | Data mentor tersimpan di database dan muncul pada tabel mentor. | **PASS** |
| **USER-02** | Admin/Mentor menyetujui (Approve) pendaftaran Peserta | Pilih Peserta `terdaftar`, Klik "Terima / Approve", tentukan Mentor Pembimbing | Status Peserta berubah dari `terdaftar` menjadi `aktif`, relasi mentor bimbingan terhubung. | Status peserta menjadi `aktif` dan dapat melakukan login. | **PASS** |
| **USER-03** | Admin/Mentor menolak (Reject) pendaftaran Peserta | Pilih Peserta `terdaftar`, Klik "Tolak" | Status Peserta berubah menjadi `ditolak`. | Status peserta menjadi `ditolak` dan tidak bisa masuk dashboard. | **PASS** |
| **USER-04** | Admin memperbarui data Mentor | Edit No HP, Gelar, atau Bidang Mentor | Data profil mentor terbarui di database. | Perubahan data mentor berhasil tersimpan. | **PASS** |
| **USER-05** | Admin menghapus data Mentor | Klik "Hapus" pada baris Mentor | Akun mentor terhapus dan relasi bimbingan dialihkan menjadi `NULL` tanpa merusak data peserta. | Account mentor terhapus bersih dari database. | **PASS** |
| **USER-06** | Pengguna memperbarui profil pribadi | Unggah foto profil baru, ubah No HP & Alamat | Data profil pengguna berhasil diperbarui. | Foto profil dan info kontak berhasil terupdate. | **PASS** |

---

### 3.3 Modul Presensi / Absensi (Peserta, Mentor, & Admin)

| ID Test | Skenario Pengujian | Input Data | Hasil yang Diharapkan | Hasil Pengujian Sebenarnya | Status |
|---|---|---|---|---|:---:|
| **ABS-01** | Peserta melakukan Check-in harian | Klik tombol "Check-in" pada hari aktif | Jam check-in tercatat sesuai waktu server, status kehadiran menjadi `hadir`. | Record absensi hari ini tersimpan dengan jam check-in aktif. | **PASS** |
| **ABS-02** | Peserta melakukan Check-in dua kali pada hari yang sama | Klik tombol "Check-in" lagi pada hari yang sama | Sistem mencegah duplikasi (karena constraint `unique_together ['peserta', 'tanggal']`). | Tombol check-in nonaktif / sistem menampilkan info sudah check-in. | **PASS** |
| **ABS-03** | Peserta melakukan Check-out | Klik tombol "Check-out" setelah check-in | Jam check-out tercatat pada record absensi hari tersebut. | Jam check-out berhasil tersimpan di database. | **PASS** |
| **ABS-04** | Mentor memantau presensi peserta bimbingan | Buka menu `/absensi/` (Mentor View) | Menampilkan rekap presensi seluruh peserta di bawah bimbingan mentor terkait. | Tabel absensi menampilkan data presensi peserta bimbingan. | **PASS** |
| **ABS-05** | Admin mengubah status absensi peserta (Edit Absensi) | Ubah status dari `hadir` menjadi `sakit` / `izin` + masukkan Keterangan | Record absensi ter-update sesuai perubahan admin. | Status dan keterangan absensi berhasil diperbarui. | **PASS** |

---

### 3.4 Modul Manajemen Tugas & Submisi (Peserta & Mentor)

| ID Test | Skenario Pengujian | Input Data | Hasil yang Diharapkan | Hasil Pengujian Sebenarnya | Status |
|---|---|---|---|---|:---:|
| **TGS-01** | Mentor membuat tugas baru | Judul: `Sistem CRUD`, Deskripsi: `Buat modul...`, Deadline: `2026-08-15`, Target: `Peserta A` | Tugas baru tersimpan dengan status `belum` dan muncul di dashboard Peserta A. | Tugas tersimpan dan notifikasi/item tugas muncul di peserta. | **PASS** |
| **TGS-02** | Peserta mengklik "Kerjakan Tugas" | Klik tombol "Kerjakan" pada daftar tugas | Status tugas otomatis berubah menjadi `proses` (Sedang Dikerjakan). | Status tugas ter-update menjadi `proses`. | **PASS** |
| **TGS-03** | Peserta menyerahkan (submit) hasil tugas | Input Link Repository: `https://github.com/...`, Upload File Submisi | File/link tersimpan, status tugas berubah menjadi `dikirim` (Menunggu Penilaian). | Submisi berhasil terunggah dan status berubah menjadi `dikirim`. | **PASS** |
| **TGS-04** | Mentor melakukan review dan memberi nilai lulus | Input Nilai: `90`, Catatan: `Sangat baik`, Status: `selesai` | Nilai dan catatan tersimpan, status tugas menjadi `selesai` (Dinilai). | Tugas berhasil dinilai dan status terdaftar sebagai `selesai`. | **PASS** |
| **TGS-05** | Mentor meminta revisi tugas | Input Catatan: `Perbaiki bagian dokumen`, Status: `perlu_revisi` | Status tugas berubah menjadi `perlu_revisi`, Peserta dapat mengirim ulang submisi. | Peserta menerima status `perlu_revisi` dan dapat mengunggah ulang. | **PASS** |
| **TGS-06** | Mentor memperbarui deadline tugas | Ubah tanggal deadline ke tanggal baru | Tanggal deadline pada tugas terbarui. | Perubahan deadline tersimpan dengan benar. | **PASS** |

---

### 3.5 Modul Jurnal Logbook Harian (Peserta & Mentor)

| ID Test | Skenario Pengujian | Input Data | Hasil yang Diharapkan | Hasil Pengujian Sebenarnya | Status |
|---|---|---|---|---|:---:|
| **LOG-01** | Peserta menambah logbook baru (Draft) | Tanggal: `Hari ini`, Kegiatan: `Integrasi API`, Pilihan Simpan: `Draft` | Logbook tersimpan dengan status `draft` dan dapat diedit kembali oleh Peserta. | Logbook status `draft` tersimpan di database. | **PASS** |
| **LOG-02** | Peserta mengunggah dokumentasi & mengirim logbook | Unggah Foto `.png`, Kegiatan: `Testing App`, Pilihan Simpan: `Dikirim` | File dokumentasi terunggah, status logbook berubah menjadi `dikirim`. | Logbook status `dikirim` tersimpan dan muncul di halaman mentor. | **PASS** |
| **LOG-03** | Mentor memverifikasi logbook peserta | Klik "Setujui/Verifikasi", beri catatan mentor | Status logbook berubah dari `dikirim` menjadi `diverifikasi`. | Status logbook terbarui menjadi `diverifikasi`. | **PASS** |
| **LOG-04** | Mentor meminta revisi logbook | Klik "Minta Revisi", beri catatan revisi | Status logbook berubah menjadi `perlu_revisi`. | Peserta melihat catatan revisi dari mentor pada jurnal logbook. | **PASS** |
| **LOG-05** | Peserta mengedit logbook status `draft` / `perlu_revisi` | Ubah uraian kegiatan & unggah ulang foto | Data logbook terbarui dan siap dikirim ulang. | Logbook berhasil diperbarui. | **PASS** |

---

### 3.6 Modul Penilaian Evaluasi Akhir (Mentor & Peserta)

| ID Test | Skenario Pengujian | Input Data | Hasil yang Diharapkan | Hasil Pengujian Sebenarnya | Status |
|---|---|---|---|---|:---:|
| **NIL-01** | Mentor menginput 7 kriteria penilaian peserta | Kedisiplinan: `85`, Kreativitas: `90`, Komunikasi: `80`, Teknis: `95`, Presensi: `90`, Presentasi: `85`, Sikap: `90` | System menghitung otomatis rata-rata `total_nilai = 87.86` dan menyimpan data penilaian. | Model method `save()` menghitung `total_nilai` dengan presisi (87.86). | **PASS** |
| **NIL-02** | Input nilai di luar batas skala (misal > 100 atau < 0) | Input angka `150` pada salah satu kriteria | Form validasi HTML5 / Django Form menolak masukan dan menampilkan pesan batasan angka. | Input angka tidak valid ditolak oleh sistem. | **PASS** |
| **NIL-03** | Mentor mengedit penilaian yang sudah diinput | Ubah skor Teknis dari `95` menjadi `98` | Record penilaian diperbarui dan `total_nilai` dikalkulasi ulang secara otomatis. | `total_nilai` ter-update secara otomatis di database. | **PASS** |
| **NIL-04** | Peserta melihat transkrip penilaian akhir | Buka menu `/penilaian/` (Peserta View) | Tampilan memuat rincian 7 kriteria nilai, total nilai rata-rata, dan catatan kesimpulan mentor. | Peserta dapat melihat transkrip lengkap penilaian magang. | **PASS** |

---

### 3.7 Modul Projek Magang & Sinkronisasi (Peserta & Mentor)

| ID Test | Skenario Pengujian | Input Data | Hasil yang Diharapkan | Hasil Pengujian Sebenarnya | Status |
|---|---|---|---|---|:---:|
| **PRJ-01** | Peserta mengelola data Projek Magang | Judul: `SIM Magang`, Penjelasan: `Aplikasi Web`, Link Repo: `https://github.com/...` | Data projek magang tersimpan dan terhubung ke profil peserta (`OneToOneField`). | Data projek tersimpan dan tampil di detail projek peserta. | **PASS** |
| **PRJ-02** | Peserta mengunggah file dokumen teknis projek | Upload file PDF laporan/arsitektur | File tersimpan di direktori `media/projek_docs/` dan link download berfungsi. | File dokumen projek terunggah dan dapat diunduh. | **PASS** |
| **PRJ-03** | Auto-synchronization tugas ke projek magang | Peserta mengeklik tombol "Kerjakan" pada tugas berjenis projek | Informasi judul & deskripsi tugas terisi secara otomatis ke modul `projek` tanpa overwrite data manual. | Sinkronisasi otomatis berjalan dengan sukses. | **PASS** |

---

### 3.8 Modul Laporan & Export Data (Admin & Mentor)

| ID Test | Skenario Pengujian | Input Data | Hasil yang Diharapkan | Hasil Pengujian Sebenarnya | Status |
|---|---|---|---|---|:---:|
| **LAP-01** | Admin melihat rekapitulasi laporan magang | Buka menu `/laporan/admin/` | Menampilkan seluruh data statistik presensi, logbook, dan nilai peserta magang. | Ringkasan laporan statistik sistem ditampilkan dengan presisi. | **PASS** |
| **LAP-02** | Admin melakukan Export Excel Data Magang | Klik tombol "Export Excel Admin" | Browser mengunduh file `.xlsx` berisi data rekapitulasi peserta, absensi, dan penilaian. | File spreadsheet `.xlsx` tergenerate dan terunduh sempurna. | **PASS** |
| **LAP-03** | Peserta mengunduh Laporan Rekap Pribadi | Klik tombol "Export Excel Peserta" | Browser mengunduh file spreadsheet `.xlsx` khusus rekapitulasi aktivitas peserta login. | File rekap personal terunduh sesuai data peserta aktif. | **PASS** |

---

## 4. KESIMPULAN

Berdasarkan hasil keseluruhan pengujian *Black Box Testing* yang dilakukan terhadap **38 skenario pengujian (Test Cases)** pada aplikasi **Sistem Manajemen Magang**:

1. **Tingkat Keberhasilan (Pass Rate)**: Seluruh **38 test cases** dinyatakan **PASS (100%)**.
2. **Kesesuaian Fungsional**: Seluruh fitur utama (Autentikasi, Hak Akses Role, Absensi Check-in/out, Tugas, Logbook, Penilaian 7 Kriteria, Projek Magang, dan Export Data) telah berjalan secara stabil dan sesuai dengan spesifikasi fungsional yang diharapkan.
3. **Keamanan & Otorisasi**: Pembatasan hak akses antar peran (**Peserta**, **Mentor**, dan **Admin**) terlindungi dengan baik pada layer *view/decorator* dan validasi *database constraint*.

---
*Laporan pengujian Black Box ini dibuat secara resmi untuk verifikasi kualitas perangkat lunak Sistem Manajemen Magang.*
