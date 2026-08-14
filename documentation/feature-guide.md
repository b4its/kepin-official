# Panduan Fitur & Halaman KePin — Landing Page hingga Workspace Tenant

> **Baca dulu, ini yang paling penting** 🎯
>
> Dokumen ini menjelaskan **setiap halaman dan fitur** aplikasi KePin dengan dua cara sekaligus:
> - **Dalam bahasa manusia** — memakai kata-kata sehari-hari dan perumpamaan agar mudah dipahami siapa saja, bahkan yang tidak terbiasa dengan istilah akuntansi atau komputer.
> - **Detail teknis** — tabel dan istilah resmi untuk keperluan pengembang, penguji, dan dokumentasi.
>
> Jadi jika ada istilah yang membingungkan, cukup baca bagian **"Dalam bahasa sederhana"** di setiap bab.

---

## 📌 KePin Itu Apa Sih?

Bayangkan sebuah **toko atau usaha kecil** yang selama ini mencatat:

- Uang masuk/keluar di **buku catatan**,
- Stok barang di **aplikasi catatan ponsel**,
- Tagihan pelanggan di **spreadsheet**,
- Gaji dan utang pemasok **di kepala pemiliknya**.

Lalu suatu hari pemiliknya ingin tahu: *"Sebenarnya bulan ini saya untung atau rugi?"* — dan tidak bisa menjawab karena datanya berceceran di mana-mana.

**KePin adalah solusinya.** KePin menyatukan semua catatan itu dalam satu aplikasi yang bisa diakses lewat browser (Chrome, Firefox, dll). Semua angka otomatis terhubung: saat kasir menjual barang, stok berkurang dan uang masuk tercatat sendiri. Saat membeli barang dari pemasok, utang dan stok ikut ter-update. Di akhir bulan, laporan untung-rugi sudah jadi tanpa perlu hitung manual.

**Dalam bahasa sederhana:** KePin seperti **"pembukuan digital semua-dalam-satu"** untuk usaha kecil-menengah (UMKM). Sekali input di satu tempat, semua bagian lain ikut terisi otomatis.

---

## Daftar Isi

- [1. Landing Page (Halaman Depan)](#1-landing-page-halaman-depan)
  - [1.1 Header (Bilah Atas)](#11-header-bilah-atas)
  - [1.2 Hero (Kalimat Pembuka)](#12-hero-kalimat-pembuka)
  - [1.3 Trust Strip (Rakitan Angka Kepercayaan)](#13-trust-strip-rakitan-angka-kepercayaan)
  - [1.4 Masalah (`#solusi`)](#14-masalah-solusi)
  - [1.5 Alur Solusi (Cara Kerja Berantai)](#15-alur-solusi-cara-kerja-berantai)
  - [1.6 Fitur Unggulan (`#fitur`)](#16-fitur-unggulan-fitur)
  - [1.7 Keamanan Zero Trust (`#keamanan`)](#17-keamanan-zero-trust-keamanan)
  - [1.8 Cara Kerja (`#cara-kerja`)](#18-cara-kerja-cara-kerja)
  - [1.9 Untuk Siapa KePin?](#19-untuk-siapa-kepin)
  - [1.10 Harga (`#harga`)](#110-harga-harga)
  - [1.11 Program Early Adopter](#111-program-early-adopter)
  - [1.12 FAQ (`#faq`)](#112-faq-faq)
  - [1.13 Penutup (Final CTA)](#113-penutup-final-cta)
  - [1.14 Footer (Kaki Halaman)](#114-footer-kaki-halaman)
  - [1.15 Halaman Legal (Privasi / Syarat / Keamanan)](#115-halaman-legal-privasi--syarat--keamanan)
- [2. Halaman Masuk & Daftar (Auth)](#2-halaman-masuk--daftar-auth)
  - [2.1 Login (Masuk)](#21-login-masuk)
  - [2.2 Register (Daftar Akun)](#22-register-daftar-akun)
  - [2.3 Buat Perusahaan Baru](#23-buat-perusahaan-baru)
  - [2.4 Gabung Perusahaan](#24-gabung-perusahaan)
  - [2.5 Lupa Password](#25-lupa-password)
  - [2.6 Reset Password](#26-reset-password)
  - [2.7 Verifikasi 2 Langkah (MFA)](#27-verifikasi-2-langkah-mfa)
  - [2.8 Halaman Awal Setelah Login (Onboarding)](#28-halaman-awal-setelah-login-onboarding)
- [3. Workspace Tenant (Ruang Kerja Perusahaan)](#3-workspace-tenant-ruang-kerja-perusahaan)
  - [3.0 Kerangka & Navigasi Workspace](#30-kerangka--navigasi-workspace)
  - [3.1 Dashboard (Papan Pemantau)](#31-dashboard-papan-pemantau)
  - [3.2 POS (Mesin Kasir Digital)](#32-pos-mesin-kasir-digital)
  - [3.3 Penjualan (Sales)](#33-penjualan-sales)
  - [3.4 Pembelian (Purchasing)](#34-pembelian-purchasing)
  - [3.5 Inventori / Stok Barang](#35-inventori--stok-barang)
  - [3.6 Akuntansi / Pembukuan](#36-akuntansi--pembukuan)
  - [3.7 Laporan Keuangan (Reports)](#37-laporan-keuangan-reports)
  - [3.8 Insight (Wawasan Otomatis)](#38-insight-wawasan-otomatis)
  - [3.9 Audit (Jejak Perubahan)](#39-audit-jejak-perubahan)
  - [3.10 Notifikasi (Pemberitahuan)](#310-notifikasi-pemberitahuan)
  - [3.11 Tutorial (Panduan Berjalan)](#311-tutorial-panduan-berjalan)
  - [3.12 Transaksi Manual](#312-transaksi-manual)
  - [3.13 Pengaturan (Settings)](#313-pengaturan-settings)
- [4. Pemilik vs Karyawan (Dua Peran)](#4-pemilik-vs-karyawan-dua-peran)
- [5. Lampiran: Temuan Analisis](#5-lampiran-temuan-analisis)

---

# 1. Landing Page (Halaman Depan)

**Landing page** adalah halaman pertama yang dilihat orang ketika membuka situs KePin — alamatnya `/`. Fungsinya seperti **papan iklan dan etalase toko**: memperkenalkan produk, menjelaskan masalah yang dipecahkan, menampilkan harga, dan mengajak pengunjung untuk **daftar** atau **masuk**.

Selain halaman utama, ada 3 halaman tambahan: Kebijakan Privasi (`/privacy`), Syarat & Ketentuan (`/terms`), dan Keamanan (`/security`).

**Dalam bahasa sederhana:** Landing page itu seperti **brosur toko yang bisa diklik** — orang yang belum kenal KePin membaca di sini, lalu memutuskan mau mencoba atau tidak.

---

## 1.1 Header (Bilah Atas)

Bilah paling atas halaman yang **selalu ikut menggulir** (sticky).

**Dalam bahasa sederhana:** Ini adalah **pintu masuk dan papan navigasi**. Di sini orang bisa:
- Klik **logo KePin** untuk kembali ke halaman awal.
- Klik menu **Solusi, Fitur, Keamanan, Cara Kerja, Harga, FAQ** — tiap klik langsung melompat ke bagian tertentu di halaman yang sama.
- Klik tombol **"Masuk"** (kalau sudah punya akun) atau **"Coba Gratis"** (kalau belum).

Perilaku pintar (auth-aware):
- **Belum login** → terlihat tombol *Masuk* + *Coba Gratis*.
- **Sudah login sebagai pemilik bisnis** → tombol berubah menjadi **nama perusahaannya**, klik langsung masuk ke ruang kerja.
- **Sudah login sebagai admin platform** → tombol *Panel*.
- **Sudah login tapi belum punya perusahaan** → tombol *Lengkapi Profil*.

Ada juga tombol **tanya (`?`)** untuk memulai tur panduan, dan menu **tema** (terang/gelap) agar mata nyaman.

> **Catatan kecil**: status login di bilah ini hanya dibaca sekali saat halaman dimuat. Kalau pengguna login/logout di tab yang sama, perlu me-refresh halaman agar tombolnya berubah.

---

## 1.2 Hero (Kalimat Pembuka)

Bagian paling atas dan paling mencolok (90% tinggi layar).

**Dalam bahasa sederhana:** Ini **kalimat sapaan pertama**. Isinya:
- Judul besar: *"Keuangan rapi. Operasional terkendali. Bisnis lebih dipercaya."* — maksudnya: uang tercatat rapi, barang terkontrol, dan laporan bisa dipercaya (misalnya saat bicara dengan bank atau investor).
- Penjelasan singkat apa itu KePin.
- Dua tombol ajakan:
  - **"Coba Gratis 14 Hari"** → langsung ke halaman pendaftaran.
  - **"Lihat Cara Kerja"** → melompat ke bagian penjelasan.
- Catatan kecil: *"Tanpa kartu kredit. Batalkan kapan saja."* — artinya mencoba tidak dikenai biaya dan tidak mengikat.

Di sisi kanan (hanya di layar komputer) ada **gambar contoh dashboard** yang menunjukkan angka "Pendapatan Bulan Ini Rp 89,5 Jt" dan "Stok Kritis 3" — supaya calon pengguna membayangkan seperti apa tampilan aplikasinya.

---

## 1.3 Trust Strip (Rakitan Angka Kepercayaan)

Pita gelap berisi 4 angka besar.

**Dalam bahasa sederhana:** Ini **papan nilai jual** untuk meyakinkan pengunjung bahwa KePin sudah dipakai banyak orang dan aman:
- **5.000+ UMKM Terdaftar** — sudah banyak yang memakai.
- **50+ Kota Tersebar** — dipakai di banyak kota.
- **99.9% Uptime Platform** — hampir tidak pernah mati.
- **ISO 27001** — standar keamanan data internasional.

Angka-angka ini statis (tidak bisa diklik) — murni alat pemasaran.

---

## 1.4 Masalah (`#solusi`)

Tiga kartu yang menggambarkan **keluhan umum pemilik usaha kecil**.

**Dalam bahasa sederhana:** Sebelum menawarkan solusi, KePin "menyentuh luka" dulu — supaya pengunjung merasa *"ih, itu masalah saya!"* Tiga masalah itu:
1. **Fraud & selisih terlambat diketahui** — barang hilang atau uang tidak cocok baru ketahuan saat tutup buku. (Di KePin, ada peringatan real-time.)
2. **Data keuangan tersebar** — catatan di buku, stok di spreadsheet, bayaran di aplikasi lain, jadi sulit melihat gambaran utuh. (Di KePin, semua jadi satu.)
3. **Keputusan tanpa data** — beli stok asal-asalan tanpa lihat tren, akhirnya barang menumpuk dan uang macet. (Di KePin, ada laporan dan prediksi.)

---

## 1.5 Alur Solusi (Cara Kerja Berantai)

Rangkaian 6 langkah dengan panah: **Penjualan → Stok → Jurnal → Laporan → Insight → Keputusan**.

**Dalam bahasa sederhana:** Ini menjelaskan **efek bola salju** KePin. Sekali data penjualan masuk, otomatis:
1. **Penjualan** tercatat,
2. **Stok** barang berkurang,
3. **Jurnal** (catatan akuntansi) terisi,
4. **Laporan** keuangan jadi,
5. **Insight** (wawasan) muncul,
6. Pemilik bisa ambil **keputusan** — misalnya barang apa yang harus dibeli ulang.

Semua terjadi otomatis tanpa input ulang.  ini murni penjelasan visual, tidak ada tombol.

---

## 1.6 Fitur Unggulan (`#fitur`)

Enam kartu berisi kemampuan utama KePin.

**Dalam bahasa sederhana:** Ini **daftar menu andalan** — seperti daftar menu di restoran:

| Fitur | Artinya buat pengguna awam |
|---|---|
| **Akuntansi Dasar** | Mencatat pemasukan/pengeluaran, punya daftar akun, jurnal, dan laporan keuangan lengkap. |
| **ERP Ringan** | Semua urusan operasional (jual, beli, pemasok, pelanggan, produk, stok) ada di satu tempat. |
| **Audit Trail** | Setiap perubahan tercatat: siapa, kapan, mengubah apa. Seperti CCTV untuk data. |
| **AI Insight** | Komputer menganalisis data dan memberi prediksi penjualan + saran stok. |
| **Investor Report** | Laporan khusus yang rapi dan kredibel untuk investor / calon pendana. |
| **Multi-Format Export** | Data bisa diunduh dalam format PDF, CSV, XLSX — data milik pengguna, bisa dibawa kapan saja. |

---

## 1.7 Keamanan Zero Trust (`#keamanan`)

 dua kolom yang menjelaskan **seberapa aman data pengguna**.

**Dalam bahasa sederhana:** "Zero Trust" artinya **jangan percaya siapa pun secara otomatis** — setiap akses diperiksa. Diibaratkan gedung dengan banyak pintu keamanan berlapis:
- Setiap orang hanya bisa masuk sesuai **perannya** (pemilik vs karyawan beda akses).
- Data satu perusahaan **terisolasi** — perusahaan lain tidak bisa melihatnya.
- Ada **verifikasi 2 langkah (MFA)** — bukan cuma password.
- Ada **jejak audit** yang tidak bisa diubah-ubah.
- Data **dienkripsi** (disandikan) saat dikirim dan disimpan.

Tombol **"Pelajari Lebih Lanjut"** membawa ke halaman `/security` yang menjelaskan lebih detail.

---

## 1.8 Cara Kerja (`#cara-kerja`)

Empat langkah bernomor besar: 01–04.

**Dalam bahasa sederhana:** Ini **resep memulai KePin** dari nol:
1. **Buat Workspace** — daftar dan buat "kantor digital" bisnis.
2. **Setup Bisnis** — masukkan produk, pelanggan, pemasok, dan undang tim.
3. **Catat Transaksi** — input penjualan/pembelian/pengeluaran; stok dan jurnal otomatis ter-update.
4. **Pantau & Kembangkan** — lihat dashboard, laporan, dan insight untuk mengambil keputusan.

---

## 1.9 Untuk Siapa KePin?

Empat kartu segmen pengguna.

**Dalam bahasa sederhana:** **Siapa yang cocok memakai KePin?**
- **Ritel** (toko) → memantau selisih stok dan barang yang jarang laku.
- **F&B** (makanan/minuman) → mengelola bahan baku, pembelian, dan margin menu.
- **Manufaktur Kecil** → memantau bahan baku, proses produksi, dan biaya.
- **Startup** → laporan arus kas yang kredibel untuk investor.

---

## 1.10 Harga (`#harga`)

Tiga paket berlangganan.

**Dalam bahasa sederhana:** **Pilihan langganan bulanan** — seperti paket internet:
- **Basic Rp199.000/bulan** — untuk yang baru mulai; 50 transaksi/bulan, 1 pengguna, 1 cabang.
- **Premium Rp499.000/bulan** (diberi tanda **POPULER**) — paling seimbang; transaksi tak terbatas, 5 pengguna, 3 cabang, kelola stok & invoice, prediksi AI dasar.
- **Platinum Rp999.000/bulan** — untuk yang siap cari dana; pengguna & cabang tak terbatas, laporan investor, audit lengkap, rekonsiliasi bank, dukungan khusus.

Setiap paket punya tombol ajakan. Tombol paket Premium mengirim parameter `?plan=premium` ke halaman daftar.

> ⚠️ **Catatan temuan**: parameter `?plan=` sebenarnya **tidak dibaca** oleh halaman pendaftaran (lihat Lampiran #1). Jadi tombolnya tetap membuka halaman daftar biasa, tanpa paket terpilih otomatis.

---

## 1.11 Program Early Adopter

Banner merah mencolok.

**Dalam bahasa sederhana:** **Promo untuk pengguna pertama.** Diskon 50% untuk tahun pertama, tapi kuotanya terbatas 50 klien pertama, dan sebagai gantinya pengguna bersedia memberi testimoni & masukan. Ada tombol **"Ambil Diskon Early Adopter"** yang mengarah ke pendaftaran.

---

## 1.12 FAQ (`#faq`)

Enam pertanyaan yang bisa dibuka-tutup (accordion).

**Dalam bahasa sederhana:** Ini **tempat jawaban pertanyaan yang paling sering ditanyakan** — seperti "tanya jawab" di situs. Klik pertanyaan → jawaban muncul di bawahnya, ikon panah berputar. Klik lagi → tertutup. Hanya satu pertanyaan yang bisa terbuka dalam satu waktu.

Pertanyaannya antara lain: cocok untuk yang tidak punya staf akuntansi? bagaimana pemisahan data antar perusahaan? bisa kelola banyak cabang? apa yang terjadi setelah masa trial? bagaimana cara ekspor data? bagaimana cara kerja prediksi AI?

---

## 1.13 Penutup (Final CTA)

Bagian paling bawah sebelum footer.

**Dalam bahasa sederhana:** Ini **ajakan pamungkas** — "Siap Mengelola Bisnis dengan Lebih Percaya Diri?" dengan dua tombol: **"Coba Gratis 14 Hari"** dan **"Jadwalkan Demo"**. Sama seperti hero, ada catatan *"Tanpa kartu kredit. Dukungan setup gratis."*

---

## 1.14 Footer (Kaki Halaman)

Bagian paling bawah, berlatar gelap, berisi 4 kolom.

**Dalam bahasa sederhana:** Ini **papan petunjuk lengkap** di dasar halaman:
- **Brand** — logo + tagline.
- **Produk** — link cepat ke Fitur, Harga, Keamanan.
- **Perusahaan** — Kebijakan Privasi & Syarat Ketentuan.
- **Bantuan** — alamat email `hello@kepin.id` dan link FAQ.

Di bar paling bawah ada hak cipta tahun berjalan dan menu tema.

---

## 1.15 Halaman Legal (Privasi / Syarat / Keamanan)

Tiga halaman teks panjang dengan header dan breadcrumb (jejak lokasi).

**Dalam bahasa sederhana:**
- **Kebijakan Privasi** — janji KePin soal data pengguna: data apa yang dikumpulkan, dipakai untuk apa, bagaimana dijaga, hak pengguna, dan soal cookie.
- **Syarat & Ketentuan** — aturan main pemakaian layanan: layanan apa yang disediakan, tanggung jawab akun, pembayaran & langganan, batasan tanggung jawab, dan penghentian layanan.
- **Halaman Keamanan** — rincian cara KePin menjaga keamanan: 6 kartu (ISO 27001, Enkripsi, Isolasi Tenant, Audit Trail, MFA, Infrastruktur Aman) + praktik keamanan + alamat email untuk melaporkan celah keamanan (`security@kepin.id`).

Halaman-halaman ini statis — hanya dibaca, tidak ada tombol interaktif selain link email.

---

# 2. Halaman Masuk & Daftar (Auth)

Kelompok halaman ini adalah **gerbang masuk aplikasi**. Semua halaman di sini berbentuk kartu di tengah layar dengan logo di atas.

**Dalam bahasa sederhana:** Bayangkan pintu masuk gedung:
- **Belum punya kartu** → daftar dulu (Register).
- **Punya kartu** → tunjukkan kartunya (Login).
- **Lupa PIN** → minta kartu baru (Forgot/Reset Password).
- **Verifikasi 2 langkah** → tunjukkan kode dari aplikasi ponsel (MFA).
- **Pertama kali masuk** → dipandu memilih: buat perusahaan baru atau gabung perusahaan (Onboarding).

Catatan penting: semua data sesi disimpan di **localStorage browser** (penyimpanan lokal per perangkat). Artinya, kalau ganti perangkat atau hapus data browser, harus login ulang.

---

## 2.1 Login (Masuk)

Halaman untuk masuk dengan akun yang sudah ada.

**Dalam bahasa sederhana:** Form sederhana dua kolom — **email** dan **password** (ada ikon mata untuk melihat/menyembunyikan password). Lalu:
- Klik **"Lupa password?"** jika lupa kata sandi.
- Klik **"Daftar gratis"** jika belum punya akun.
- Setelah masuk berhasil, KePin mengarahkan otomatis:
  - Akun punya perusahaan → langsung ke **ruang kerja** perusahaan.
  - Akun belum punya perusahaan → ke halaman **pilihan buat/gabung**.
  - Akun admin platform → ke **panel admin**.
  - Akun dengan verifikasi 2 langkah aktif → ke halaman **verifikasi kode** dulu.

> ⚠️ **Catatan temuan**: kotak centang **"Ingat saya"** di halaman ini hanya hiasan — tidak menyimpan apa-apa (Lampiran #3).

---

## 2.2 Register (Daftar Akun)

Halaman untuk membuat akun baru.

**Dalam bahasa sederhana:** Isi 3 kolom: **nama lengkap, email, password** (minimal 8 karakter). Klik daftar → muncul pemberitahuan "Pendaftaran berhasil" → otomatis diarahkan ke **halaman login** untuk masuk dengan akun baru. (KePin sengaja tidak langsung login — pengguna diminta masuk manual sekali.)

> ⚠️ **Catatan temuan**: kalau datang dari tombol paket di landing (dengan `?plan=premium`), paket itu **tidak terbawa** — pengguna tetap harus memilih paket nanti di halaman buat perusahaan (Lampiran #1).

---

## 2.3 Buat Perusahaan Baru

Halaman untuk pengguna yang sudah login dan ingin **mendirikan perusahaan/workspace baru**.

**Dalam bahasa sederhana:** Ini seperti **mengisi formulir pendirian "kantor digital"**:
1. Tulis **Nama Perusahaan** — KePin otomatis membuat **tautan unik** (slug) dari nama tersebut, misal nama "Toko Maju" → tautan `/app/toko-maju`.
2. Pilih **Paket Langganan** (Free Rp0, Basic, Premium, Platinum).
3. Klik buat → muncul **Kode Bergabung** (kode khusus untuk mengundang orang lain bergabung ke perusahaan ini).
4. Klik **"Masuk ke Workspace"** → langsung dibawa ke ruang kerja perusahaan yang baru dibuat.

---

## 2.4 Gabung Perusahaan

Halaman untuk bergabung ke perusahaan orang lain memakai **kode bergabung**.

**Dalam bahasa sederhana:** Seperti **memasuki grup dengan kode undangan**. Ketik kode 16 karakter → KePin langsung memeriksa (tanpa perlu tombol) apakah kodenya valid → jika ya, muncul kartu nama perusahaannya → klik tombol gabung → langsung masuk ke workspace perusahaan tersebut.

Aturan penting: **satu akun hanya boleh bergabung ke satu perusahaan.** Kalau sudah punya perusahaan, halaman ini menampilkan peringatan dan menyarankan keluar dari perusahaan lama dulu (melalui menu profil).

---

## 2.5 Lupa Password

Halaman untuk meminta **tautan reset kata sandi**.

**Dalam bahasa sederhana:** Masukkan email → klik kirim → muncul pesan "Jika email terdaftar, tautan reset akan dikirim…" (pesan dibuat netral agar orang tidak bisa menebak email mana yang terdaftar).

**Khusus mode pengembangan:** karena layanan email belum tersambung, KePin menampilkan **token reset langsung di layar** dengan tombol **"Salin Token"** dan **"Lanjutkan Reset"** — ini jalan pintas untuk keperluan demo/pengujian.

---

## 2.6 Reset Password

Halaman untuk **membuat password baru** setelah mendapat token.

**Dalam bahasa sederhana:** Isi **token** (otomatis terisi jika datang dari tautan email, atau ketik manual), lalu **password baru** dan **ulangi password**. KePin memeriksa: dua password harus sama, dan password minimal 8 karakter. Jika cocok → password diganti → kembali ke halaman login.

---

## 2.7 Verifikasi 2 Langkah (MFA)

Halaman **lapisan keamanan tambahan** setelah login.

**Dalam bahasa sederhana:** Bayangkan selain password, ada **kunci kedua** yang berubah setiap 30 detik (dari aplikasi seperti Google Authenticator di ponsel). Ada dua cara memasukkan:
- **Tab Kode** — 6 kotak angka; saat mengetik, kursor otomatis pindah ke kotak berikutnya (dan mendukung tempel/paste).
- **Tab Recovery** — kode cadangan berbentuk `XXXX-XXXX` untuk keadaan darurat (misal ponsel hilang).

Kalau kode benar → lanjut ke ruang kerja. Kalau sesi verifikasinya sudah kedaluwarsa → diminta login ulang.

---

## 2.8 Halaman Awal Setelah Login (Onboarding)

Halaman **penentu arah** untuk pengguna yang baru login.

**Dalam bahasa sederhana:** Begitu masuk, KePin otomatis mengantar ke tempat yang tepat:
- Sudah punya perusahaan → langsung ke **ruang kerja**.
- Admin platform → ke **panel admin**.
- Belum punya perusahaan → ditanya mau **"Buat Perusahaan Baru"** atau **"Gabung Perusahaan"**, plus tombol **keluar (logout)**.

---

# 3. Workspace Tenant (Ruang Kerja Perusahaan)

Ini **inti aplikasi** — tempat pengguna bekerja setiap hari setelah login. Alamatnya `/app/{nama-perusahaan}` (misal `/app/toko-maju`). Setiap perusahaan punya ruang kerjanya sendiri yang **terpisah dari perusahaan lain** (isolasi data).

**Dalam bahasa sederhana:** Workspace itu seperti **kantor + gudang + ruang kasir dalam satu gedung digital**. Semua orang di perusahaan yang sama bisa masuk, tapi dengan **kunci akses berbeda** (lihat Bab 4: pemilik vs karyawan).

---

## 3.0 Kerangka & Navigasi Workspace

### Pintu masuk & pemeriksaan akses
Setiap kali membuka ruang kerja, KePin **memeriksa dulu** siapa penggunanya:
- Belum login → dilempar ke halaman login.
- Bukan anggota perusahaan → layar "Akses Ditolak".
- Nama perusahaan salah/tidak ada → "Tenant Tidak Ditemukan".
- Sudah sesuai → data seluruh modul (pelanggan, produk, stok, jurnal, dll) **dimuat sekaligus** agar halaman terasa cepat.

### Bilah samping (Sidebar)
Menu utama di sisi kiri, bisa **diciutkan** (jadi ikon saja) di komputer, atau jadi **laci geser** di layar ponsel. Isinya kelompok menu: Dashboard, Penjualan, Pembelian, Inventori, Akuntansi, Laporan, Pengaturan, dll.

**Khusus pemilik:** bisa **menyembunyikan/menampilkan menu** lewat Pengaturan → Sidebar, dan menu yang disembunyikan berlaku untuk semua anggota. Menu penting (Dashboard, Pengaturan, Keamanan Akun, Tutorial) selalu tampil dan tidak bisa disembunyikan.

### Bilah atas (TopBar)
Di sisi kanan ada:
- Tombol **?** → membuka halaman tutorial.
- Menu **tema** (terang/gelap).
- **Lonceng notifikasi** dengan angka merah (jumlah belum dibaca). Klik → daftar 5 notifikasi terbaru; klik satu → halaman detail; ada tombol "Lihat Semua Notifikasi".
- **Menu profil** (foto/nama) → berisi: edit profil, kembali ke beranda, gabung perusahaan (jika belum punya), **keluar dari perusahaan ini** (khusus karyawan), dan **keluar/logout**.

> ⚠️ **Catatan temuan**: ada banner "Cabang: Toko Pusat" dengan tombol "Ganti", tapi tombol itu **belum berfungsi penuh** — hanya menutup banner (Lampiran #4).

---

## 3.1 Dashboard (Papan Pemantau)

Halaman pertama saat masuk workspace.

**Dalam bahasa sederhana:** Dashboard itu seperti **dasbor mobil** — semua angka penting terlihat sekilas tanpa perlu buka banyak halaman:
- **4 kartu angka utama**: Pendapatan, Pengeluaran, Laba Bersih, dan Kas & Bank.
- **Grafik**: batang arus kas harian (hijau = uang masuk, merah = uang keluar) dan lingkaran komposisi pengeluaran (uang banyak habis untuk apa).
- **Piutang & Hutang**: kartu "Piutang Usaha" (uang yang harusnya diterima dari pelanggan) dan "Hutang Usaha" (uang yang harus dibayar ke pemasok), dipecah per umur (Lancar, 1-30 hari, 31-60, 61-90, >90 hari).
- **Kartu "Perhatian"**: daftar hal yang perlu ditindaklanjuti (misal tagihan lewat jatuh tempo, stok menipis).
- **Tabel transaksi terbaru** + tombol refresh.

Fitur pembanding:
- **Filter rentang waktu**: 1 minggu / 2 minggu / 3 minggu / 1 bulan / tanggal bebas.
- **Mode bandingkan**: centang "Bandingkan dengan periode sebelumnya" → angka metrik otomatis menampilkan selisih naik/turun dalam persen.

---

## 3.2 POS (Mesin Kasir Digital)

Halaman khusus untuk **melayani penjualan di kasir**, seperti mesin kasir di toko.

**Dalam bahasa sederhana:** Bayangkan **kasir toko kelontong**:
- **Kiri** — rak barang (katalog): cari produk dengan kotak pencarian, pilih lewat kartu produk yang menampilkan harga dan sisa stok (badge merah "Habis" atau "Stok N"). Tombol **"+ Keranjang"** memasukkan barang.
- **Kanan** — keranjang belanja: atur jumlah (tombol +/−), hapus barang, total otomatis terhitung.
- **Pembayaran**: masukkan jumlah uang yang diterima, ada tombol **"Uang Pas"** (uang pas tanpa kembalian), dan **kembalian dihitung otomatis**. Kalau uang kurang, muncul peringatan merah "kurang Rp X" dan tombol bayar terkunci.
- **Kelola stok cepat**: tombol "Stok" di tiap produk untuk menambah/mengurangi stok langsung dari kasir.
- Setelah bayar → transaksi tercatat otomatis, stok berkurang, dan muncul **nomor transaksi** sebagai bukti.

---

## 3.3 Penjualan (Sales)

### Daftar Pelanggan (`/sales/customers`)
**Dalam bahasa sederhana:** Ini **buku alamat pelanggan** — kode, nama, email, telepon, alamat. Bisa tambah/edit/hapus pelanggan, mencari dengan kotak pencarian, dan mengekspor daftarnya ke file. Ada tombol **"Kartu Piutang"** untuk melihat riwayat tagihan & pembayaran satu pelanggan (lengkap dengan saldo akhir, bisa diunduh PDF/Excel).

### Tagihan/Invoice (`/sales/invoices`)
**Dalam bahasa sederhana:** Ini **daftar tagihan** yang dikirim ke pelanggan. Membuat tagihan = memilih pelanggan, menambahkan baris barang/jasa (jumlah, harga, pajak PPN %, potongan), total dihitung otomatis. Status tagihan berjenjang: **Konsep → Terkirim → Sebagian → Dibayar** (atau **Dibatalkan**).
- Pemilik bisa **memposting** tagihan (konsep → diakui di pembukuan), **membatalkan**, atau **membalik** tagihan yang sudah diposting (jika salah).
- Ada kartu metrik: total piutang, tagihan bulan ini, dll. Bisa diekspor ke file.

---

## 3.4 Pembelian (Purchasing)

### Daftar Pemasok (`/purchasing/suppliers`)
**Dalam bahasa sederhana:** Ini **buku alamat pemasok** (yang menjual barang ke kita): kode, nama, kontak, kota. Bisa tambah/edit/hapus, cari, ekspor, dan lihat **"Kartu Hutang"** (riwayat utang ke pemasok tertentu).

### Purchase Order (`/purchasing/orders`)
**Dalam bahasa sederhana:** Ini **surat pesanan barang** ke pemasok — "tolong kirim 10 dus mie, 5 kg gula". Alurnya: **Konsep → Kirim → Sebagian diterima → Diterima** (atau **Dibatalkan**).
- Pemilik bisa **mengirim** pesanan (status jadi Terkirim), **menerima barang** (modal khusus: isi jumlah yang benar-benar diterima, stok otomatis bertambah), mengedit, membatalkan.
- Ada kartu metrik (PO terbuka, PO bulan ini, dll) dan ekspor.

### Pembayaran ke Pemasok (`/purchasing/payments`)
**Dalam bahasa sederhana:** Ini **catatan pembayaran utang** ke pemasok. Buat pembayaran (pilih pemasok, tanggal, metode: kas atau transfer, jumlah) → status **Konsep → Diposting** (diakui di pembukuan) → bisa **dibatalkan/void** jika salah. Ada kartu metrik dan ekspor.

---

## 3.5 Inventori / Stok Barang

### Produk (`/inventory/products`)
**Dalam bahasa sederhana:** Ini **daftar semua barang dagangan** — kode SKU, nama, kategori, stok, stok minimum, harga jual, harga modal. Dilengkapi kartu metrik penting:
- **Total Produk**, **Stok Kritis** (tinggal sedikit, ≤ batas minimum), **Nilai Stok** (harga semua barang), **Dead Stock** (barang yang nyaris tidak laku).
- Bisa tambah/edit/hapus produk, cari, dan ekspor.

### Pergerakan Stok (`/inventory/movements`)
**Dalam bahasa sederhana:** Ini **buku harian stok** — mencatat setiap barang masuk (in), keluar (out), penyesuaian (adjustment), atau pindah (transfer), lengkap dengan stok sebelum & sesudah serta alasannya. Hanya bisa dibaca & diekspor.

### Transaksi Produk (`/inventory/transactions`)
**Dalam bahasa sederhana:** Ini **daftar struk penjualan dari kasir (POS)** — nomor checkout, tanggal, ringkasan barang yang dibeli, total, uang dibayar, kembalian. Klik satu transaksi → detail barang per baris. Bisa dicari & diekspor.

---

## 3.6 Akuntansi / Pembukuan

> **Untuk orang awam:** bagian ini terdengar menakutkan, tapi intinya sederhana — **semua uang yang masuk & keluar dicatat rapi dalam aturan pembukuan standar**, sehingga laporan keuangan otomatis benar. Pemilik tidak perlu hafal istilah akuntansi karena KePin yang menghitung.

### Daftar Akun (Chart of Accounts, `/accounting/chart-of-accounts`)
**Dalam bahasa sederhana:** Ini **map-map pengelompokan uang**: Aset (harta), Kewajiban (utang), Ekuitas (modal), Pendapatan (pemasukan), Beban (pengeluaran). Setiap transaksi "dimasukkan ke map" yang tepat. Bisa tambah/edit/hapus akun, lihat saldonya, dan ekspor.

### Tahun Buku (`/accounting/fiscal-years`)
**Dalam bahasa sederhana:** Ini **kalender pembukuan** — dibagi per tahun dan per bulan (periode). Setiap akhir periode, pemilik bisa **menutup periode** (mengunci angka bulan itu) atau membukanya kembali. Hanya pemilik yang bisa menutup/membuka.

### Jurnal (`/accounting/journals`)
**Dalam bahasa sederhana:** Ini **catatan transaksi berpasangan** — setiap uang masuk/keluar dicatat dua sisi (debit & kredit) yang harus selalu seimbang. Formulir pembuatannya membantu: jika debit ≠ kredit, tombol simpan terkunci. Ada fitur **Buku Besar** (lihat riwayat satu akun dengan saldo berjalan) — seperti melihat mutasi satu map uang dari waktu ke waktu.

### Rekonsiliasi Bank (`/accounting/reconciliation`)
**Dalam bahasa sederhana:** Ini **mencocokkan catatan uang di aplikasi dengan mutasi bank sungguhan** — seperti mencocokkan struk di dompet dengan salinan dari bank. Fiturnya canggih:
- Daftar **rekening bank** (BCA, Mandiri, dll) beserta saldonya.
- Impor **mutasi bank** (satu per satu atau lewat **file CSV**).
- **Saran otomatis**: KePin menebak transaksi mana yang cocok dengan mutasi bank (dengan nilai skor keyakinan). Pemilik tinggal **"Cocokkan"** atau **"Cocokkan Semua Saran"** sekaligus.
- Transaksi yang sudah cocok ditandai "Terkait"; yang belum "Belum dicocokkan".

---

## 3.7 Laporan Keuangan (Reports)

Halaman terbesar dengan **7 tab** laporan.

**Dalam bahasa sederhana:** Ini **ruang cetak laporan** — semua laporan penting untuk tahu kondisi usaha:
- **Ringkasan** — gambaran cepat: pendapatan vs beban harian + daftar beban terbesar.
- **Neraca Saldo** — daftar semua akun dan saldonya, untuk memastikan pembukuan seimbang (debit = kredit).
- **Laba Rugi** — **yang paling penting**: untung atau rugi? Ditampilkan per bulan, lengkap dengan perbandingan naik/turun vs bulan sebelumnya.
- **Neraca** — harta, utang, dan modal pada satu waktu (foto kondisi keuangan).
- **Arus Kas** — uang masuk & keluar dari aktivitas operasi, investasi, dan pendanaan.
- **Aging** — rincian piutang (yang belum dibayar pelanggan) & hutang (yang belum dibayar ke pemasok) per umur; bisa digali per pelanggan/pemasok ("Kartu piutang/hutang").
- **Valuasi Stok** — nilai seluruh barang di gudang.

Semua laporan bisa **diunduh** sebagai PDF atau Excel (untuk aging, file Excel-nya punya 2 lembar: piutang & hutang). Ada juga tombol **"Tutup Periode"** (mengunci angka satu bulan) yang khusus pemilik.

### Laporan Investor (`/reports/investor`)
**Dalam bahasa sederhana:** Ini **laporan "grooming" untuk investor** — ringkasan eksekutif: pendapatan 6 bulan, margin kotor, posisi kas, dan berapa lama uang bertahan (runway). Bisa **dibagikan** (share) atau diekspor.

---

## 3.8 Insight (Wawasan Otomatis)

**Dalam bahasa sederhana:** Ini **asisten analis** — KePin membaca data lalu menampilkan kartu-kartu wawasan, misalnya *"Penjualan naik 15% minggu ini, kemungkinan karena promo"* atau *"Produk X mulai jarang laku, pertimbangkan stok ulang"*. Setiap wawasan punya **dampak** (positif/negatif) dan faktor pendukung. Mirip dashboard: ada metrik, grafik, dan filter waktu.

---

## 3.9 Audit (Jejak Perubahan)

**Dalam bahasa sederhana:** Ini **CCTV data** — mencatat siapa mengubah apa dan kapan (misal: "Budi menghapus pelanggan A jam 10:23"). Berguna untuk keamanan dan menyelesaikan sengketa. Bisa:
- **Filter** berdasarkan jenis objek (pelanggan, produk, dll) lewat tombol pil.
- Klik **"Detail"** → melihat nilai data **sebelum** dan **sesudah** diubah.
- **Ekspor** riwayat ke file.

---

## 3.10 Notifikasi (Pemberitahuan)

**Dalam bahasa sederhana:** Ini **kotak masuk pengingat** — misal "tagihan pelanggan jatuh tempo", "stok menipis", atau "ada anggota baru". Fiturnya:
- List notifikasi dengan **titik merah** untuk yang belum dibaca, waktu relatif ("2 jam lalu").
- Tombol **"Tandai Dibaca"** untuk menandai semua.
- Klik notifikasi → halaman detail (otomatis ditandai terbaca), bisa dihapus.
- Ada pagination 20 per halaman.

---

## 3.11 Tutorial (Panduan Berjalan)

**Dalam bahasa sederhana:** Ini **pemandu wisata aplikasi** — tur interaktif yang menyorot elemen layar satu per satu sambil menjelaskan. Dari halaman ini bisa melihat daftar semua langkah tur (di halaman mana, menjelaskan apa), **"Mulai Tur dari Awal"**, atau **"Mulai dari sini"** di langkah tertentu. Murni bantuan, tidak mengubah data apa pun.

---

## 3.12 Transaksi Manual

**Dalam bahasa sederhana:** Ini **kolom untuk mencatat transaksi sendiri** yang tidak lewat kasir — misal bayar listrik, beli alat tulis, atau uang masuk dari investor. Fitur:
- 4 kartu metrik: total pemasukan, pengeluaran, rata-rata harian, transaksi bulan ini.
- Tabel transaksi (tanggal, deskripsi, akun, tipe, jumlah, status).
- **Khusus pemilik**: membuat konsep → **Posting** (diakui di pembukuan), edit, hapus, atau **Void** (membatalkan yang sudah diposting). Karyawan hanya bisa melihat.

---

## 3.13 Pengaturan (Settings)

Ada 8 halaman pengaturan:

### Profil Perusahaan (`/settings/organization`)
**Dalam bahasa sederhana:** **Kartu identitas perusahaan** — nama tampilan, nama legal, NPWP, telepon, email, website, alamat, zona waktu, mata uang. Bisa diedit lewat tombol **Edit Profil** (zona waktu pilihan WIB/WITA/WIT; mata uang IDR).

### Anggota (`/settings/members`) — khusus pemilik
**Dalam bahasa sederhana:** **Daftar karyawan** yang punya akses ke workspace. Pemilik bisa:
- Melihat & menyalin **Kode Bergabung** (kode undangan untuk anggota baru), atau membuat kode baru.
- **Mengundang anggota** (kalau emailnya belum terdaftar, KePin otomatis membuatkan akun), mengubah perannya (pemilik/karyawan), atau menghapus.
- Karyawan hanya melihat daftar tanpa tombol.

### Cabang (`/settings/branches`)
**Dalam bahasa sederhana:** **Daftar toko/cabang** — misal "Toko Pusat" dan "Cabang Bandung". Bisa tambah/edit/hapus (nama, kode, alamat, status). Satu cabang ditandai sebagai pusat (utama).

### Peran (`/settings/roles`)
**Dalam bahasa sederhana:** Halaman **penjelasan dua peran**: `tenant_owner` (pemilik — bisa kelola semua) dan `employee` (karyawan — akses sesuai yang diizinkan). Hanya baca, tidak bisa diubah di sini.

### Keamanan Akun (`/settings/security`)
**Dalam bahasa sederhana:** **Tempat mengunci akun pribadi**:
- **Aktifkan MFA** — verifikasi 2 langkah. KePin menampilkan kode rahasia (secret) dan kode pemulihan (recovery codes) yang harus disimpan; lalu diminta memasukkan kode 6 digit untuk mengaktifkan.
- **Nonaktifkan MFA** — jika ingin mematikan (perlu konfirmasi kode).
- **Ganti Password** — masukkan password lama, password baru (min 8 karakter), dan ulangi.

### Tampilan Sidebar (`/settings/sidebar`) — khusus pemilik
**Dalam bahasa sederhana:** **Atur menu mana yang muncul** untuk semua anggota. Ada saklar on/off per menu; menu penting (Dashboard, Pengaturan, Keamanan, Tutorial) terkunci. Tombol **"Simpan Perubahan"** di bagian bawah; ada juga "Aktifkan Semua" / "Nonaktifkan Semua".

### Tagihan (`/settings/billing`)
**Dalam bahasa sederhana:** **Tempat melihat paket & riwayat bayar** — paket yang sedang aktif (nama, status, periode, daftar fitur) dan tabel riwayat langganan (paket, status, periode, biaya, tanggal mulai). Hanya baca.

> ⚠️ **Catatan temuan**: kartu metrik "Paket" di halaman ini selalu menampilkan angka **0** (belum dihubungkan ke data) — Lampiran #5.

### Integrasi (`/settings/integrations`)
**Dalam bahasa sederhana:** **Tempat menyambungkan aplikasi lain** (misal bank untuk sinkronisasi mutasi otomatis). Pemilik bisa menambah integrasi (memilih provider & nama tampilan), mengaktifkan/memutuskan koneksi, dan melihat status sinkronisasi terakhir. Jika tidak ada integrasi aktif, halaman menampilkan pesan kosong (sengaja tidak menampilkan data contoh/dummy).

---

# 4. Pemilik vs Karyawan (Dua Peran)

**Dalam bahasa sederhana:** Setiap workspace punya dua jenis kunci akses — seperti **pemilik kunci gudang** vs **karyawan dengan akses terbatas**.

| Hal yang bisa dilakukan | **Pemilik** (tenant_owner) | **Karyawan** (employee) |
|---|---|---|
| Melihat semua halaman & laporan | ✅ | ✅ (sebagian hanya baca) |
| Kasir (POS) | ✅ | ✅ (bisa jual & kelola stok) |
| **Memposting** transaksi, jurnal, tagihan, pembayaran, PO | ✅ | ❌ hanya lihat |
| **Membatalkan/void/reverse** transaksi yang sudah diposting | ✅ | ❌ |
| Menutup/membuka periode & tahun buku | ✅ | ❌ |
| Kelola anggota (undang, ubah peran, hapus) | ✅ | ❌ (lihat daftar saja) |
| Atur tampilan sidebar untuk semua anggota | ✅ | ❌ |
| Kelola integrasi | ✅ | hanya lihat |
| "Keluar dari Perusahaan Ini" | ❌ (pemilik tidak bisa keluar) | ✅ |
| Keamanan akun (MFA, ganti password) | ✅ | ✅ (untuk akun sendiri) |

> Catatan: meskipun di beberapa halaman (pelanggan, pemasok, cabang, daftar akun, profil perusahaan) karyawan tetap melihat tombol tambah/edit di layar, **keamanan sebenarnya dijaga di server (backend)** — aksi yang tidak diizinkan akan ditolak. Ini temuan yang perlu diperhatikan (Lampiran #9).

---

# 5. Lampiran: Temuan Analisis

Temuan berikut adalah hasil pemeriksaan kode (belum diverifikasi lewat pengujian interaktif). Ditulis dengan dua gaya: **intinya** (untuk orang awam) dan **detail teknis** (untuk pengembang).

| # | Intinya (bahasa awam) | Detail teknis | Lokasi |
|---|---|---|---|
| 1 | Tombol paket di landing membawa "kode paket", tapi halaman daftar **tidak membacanya** — paket tidak terpilih otomatis. | Query param `?plan=premium` / `?plan=platinum` dikirim ke `/auth/register` tetapi halaman register tidak membaca `searchParams`; juga `?onboarding=true` di login tidak dikonsumsi. | Landing pricing & final CTA, `/auth/register`, `/auth/login` |
| 2 | *(lanjutan #1)* | `?onboarding=true` (dari register) tidak dipakai di halaman login — param mati. | `/auth/register` → `/auth/login` |
| 3 | Kotak centang "Ingat saya" **tidak menyimpan apa pun** — hanya hiasan. | Checkbox tanpa state/logika persistensi. | `/auth/login` |
| 4 | Banner "Cabang: Toko Pusat" dengan tombol "Ganti" **belum berfungsi** — hanya menutup banner. | `WorkspaceShell.svelte` — tombol "Ganti" hanya menutup banner; belum ada switcher cabang. | WorkspaceShell |
| 5 | Kartu angka "Paket" di halaman Tagihan **selalu 0**. | MetricCard "Paket" hardcoded `0`; nama paket hanya tampil di kartu bawah. | `/settings/billing` |
| 6 | Saat logout, sisa data akun **tidak dibersihkan total**. | `logout()` tidak menghapus `kepin_tenants` & `kepin_mfa_token` dari localStorage. | `stores/auth.ts` |
| 7 | Ada file kode lama yang **tidak dipakai** (bisa membingungkan pengembang). | `lib/api/auth.ts` menunjuk endpoint `/dev-auth/*` dan tidak dipakai alur auth mana pun. | `frontend/src/lib/api/auth.ts` |
| 8 | Sebagian halaman **belum punya tombol unduh/ekspor**. | Halaman tanpa export: Dashboard, Insights, Transactions, Notifications, Tutorial, Fiscal Years, Reconciliation, Roles, Security, Sidebar, Organization, Branches, Members, Billing, Integrations. | Berbagai halaman |
| 9 | Di beberapa halaman, karyawan **masih melihat tombol ubah/hapus** di layar (walaupun server tetap menolak). | Tanpa gating role di UI: Customers, Suppliers, Branches, COA, Organization — CRUD tampak terbuka untuk employee; backend tetap menerapkan otorisasi. | Berbagai halaman |
| 10 | Unduhan PDF untuk invoice **belum jadi** (masih placeholder). | `GET /invoices/{id}/pdf` mengembalikan `not_available` (stub). | Backend sales |
| 11 | Menu di bilah atas landing **tidak berubah otomatis** setelah login/logout di tab yang sama. | `MarketingHeader.svelte` membaca status auth sekali saat mount (tidak reaktif). | MarketingHeader |
| 12 | Beberapa halaman admin platform **hanya tampil daftar**, belum ada form buat/ubah (di luar cakupan utama dokumen). | `/admin/users`, `/admin/incidents` — backend punya create/update, UI hanya list. | Platform admin |

---

## Penutup

Dokumen ini menjelaskan alur lengkap aplikasi KePin dari **halaman depan** (landing), **gerbang masuk** (auth), hingga **ruang kerja** (workspace tenant) — dengan dua gaya bahasa: manusiawi dan teknis.

**Akun demo** yang disediakan oleh seed data untuk mencoba langsung:

| Peran | Email | Password | Perusahaan |
|---|---|---|---|
| Pemilik | `budi@tokomaju.com` | `budi123` | toko-maju |
| Karyawan | `ani@tokomaju.com` | `ani12345` | toko-maju |
| Karyawan (lain) | `siti@warungsegar.com` | `siti123` | warung-segar |
| Admin platform | `admin@kepin.io` | `admin123` | — |

Cara mencoba: buka `http://localhost:3001` (jika stack berjalan), pilih **"Masuk"**, lalu gunakan akun di atas.
