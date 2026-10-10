import fs from 'fs';
import path from 'path';

const OUT_PATH = path.resolve(import.meta.dirname, '../../documentation/dokumen/Buku_Panduan_Pengguna_KePin.md');

const content = `# 📘 BUKU PANDUAN PENGGUNA RESMI (USER MANUAL)
# KePin — Keuangan Pintar
### *Sistem ERP & SaaS Terpadu untuk Manajemen Keuangan, Kasir Digital (POS), Inventori, dan Operasional Bisnis UMKM*

---

| Dokumen | Informasi |
|---|---|
| **Judul** | Buku Panduan Pengguna KePin (Keuangan Pintar) |
| **Versi Aplikasi** | v1.0.0 (Production Release) |
| **Penyusun** | Tim Produk & Dokumentasi KePin |
| **Target Pembaca** | Pemilik Usaha (Owner), Manajer Keuangan, Kasir/Staf Operasional, Administrator Sistem |
| **Tanggal Pembaruan** | Oktober 2026 |
| **Status Dokumen** | Dokumen Resmi & Panduan Operasional Lapangan |

---

## 📑 DAFTAR ISI

1. [BAB 1: PENDAHULUAN & PROFIL APLIKASI](#bab-1-pendahuluan--profil-aplikasi)
   - 1.1 Mengenal KePin — Solusi Pembukuan Terpadu UMKM
   - 1.2 Konsep Arsitektur Multi-Tenant SaaS
   - 1.3 Aliran Integrasi Data Otomatis (*Seamless Sync Engine*)
   - 1.4 Matriks Hak Akses & Pembagian Peran Pengguna (RBAC)
   - 1.5 Kebutuhan Sistem & Kompatibilitas Perangkat
2. [BAB 2: HALAMAN PUBLIK & AUTENTIKASI PENGGUNA](#bab-2-halaman-publik--autentikasi-pengguna)
   - 2.1 Menjelajahi Landing Page Resmi
   - 2.2 Panduan Masuk ke Sistem (Login)
   - 2.3 Pendaftaran Akun Baru (Register)
   - 2.4 Membuat Perusahaan Baru (Create Tenant)
   - 2.5 Bergabung ke Perusahaan dengan Kode Undangan (Join Code)
   - 2.6 Pemulihan Kata Sandi (Forgot & Reset Password)
   - 2.7 Autentikasi Dua Faktor (MFA)
3. [BAB 3: WORKSPACE PERUSAHAAN (TENANT DASHBOARD)](#bab-3-workspace-perusahaan-tenant-dashboard)
   - 3.1 Tata Letak Workspace (Bilah Navigasi, Header, & Profil)
   - 3.2 Menelaah Indikator Kinerja Utama (KPI Metrics)
   - 3.3 Grafik Tren Omzet, Biaya, dan Arus Kas Bersih
   - 3.4 Ringkasan Piutang & Utang Berjalan (*Aging Summary*)
4. [BAB 4: MESIN KASIR DIGITAL (POINT OF SALE / POS)](#bab-4-mesin-kasir-digital-point-of-sale--pos)
   - 4.1 Antarmuka Kasir Digital KePin
   - 4.2 Alur Transaksi Kasir: Memilih Barang, Jumlah, & Diskon
   - 4.3 Pemrosesan Pembayaran (Tunai, QRIS, Transfer Bank)
   - 4.4 Pengurangan Stok Otomatis & Cetak Struk Penjualan
5. [BAB 5: MODUL PENJUALAN (SALES MANAGEMENT)](#bab-5-modul-penjualan-sales-management)
   - 5.1 Riwayat Transaksi Penjualan Lengkap
   - 5.2 Pengelolaan Faktur Penjualan (Invoicing & Piutang)
   - 5.3 Manajemen Basis Data Pelanggan (Customer Directory)
6. [BAB 6: MODUL PEMBELIAN & PENGADAAN (PURCHASING)](#bab-6-modul-pembelian--pengadaan-purchasing)
   - 6.1 Pembuatan Pesanan Pembelian (Purchase Orders - PO)
   - 6.2 Penerimaan Barang & Integrasi Otomatis Stok
   - 6.3 Pembayaran Tagihan Pemasok (Supplier Bills & Payments)
   - 6.4 Manajemen Basis Data Pemasok (Vendor Management)
7. [BAB 7: MODUL INVENTORI & MANAJEMEN GUDANG](#bab-7-modul-inventori--manajemen-gudang)
   - 7.1 Katalog Produk, SKU, Barcode, & Stok Minimum
   - 7.2 Log Mutasi Stok Barang (Stock Movements)
   - 7.3 Multi-Gudang & Lokasi Inventori
8. [BAB 8: MODUL AKUNTANSI & PEMBUKUAN KEUANGAN](#bab-8-modul-akuntansi--pembukuan-keuangan)
   - 8.1 Bagan Akun Standar (Chart of Accounts / CoA)
   - 8.2 Konfigurasi Modal Awal Usaha (Initial Capital Engine)
   - 8.3 Jurnal Umum (General Journal Entries)
   - 8.4 Rekonsiliasi Bank Otomatis & Manual
9. [BAB 9: MODUL LAPORAN KEUANGAN & EKSEKUTIF](#bab-9-modul-laporan-keuangan--eksekutif)
   - 9.1 Laporan Laba Rugi (Profit & Loss Statement)
   - 9.2 Laporan Neraca Keuangan (Balance Sheet)
   - 9.3 Laporan Arus Kas (Cash Flow Statement)
   - 9.4 Buku Besar (General Ledger)
   - 9.5 Analisis Penuaan Piutang (AR) & Utang (AP Aging)
   - 9.6 Laporan Ringkasan Investor & Eksekutif
10. [BAB 10: WAWASAN BISNIS OTOMATIS (AI INSIGHTS) & AUDIT KEAMANAN](#bab-10-wawasan-bisnis-otomatis-ai-insights--audit-keamanan)
    - 10.1 Analisis Wawasan Bisnis Otomatis (*Automated Insights*)
    - 10.2 Log Jejak Audit Aktivitas (Audit Trail)
    - 10.3 Pusat Pemberitahuan & Notifikasi
11. [BAB 11: PENGATURAN PERUSAHAAN & KUSTOMISASI WORKSPACE](#bab-11-pengaturan-perusahaan--kustomisasi-workspace)
    - 11.1 Profil Organisasi, Legalitas, & NPWP
    - 11.2 Manajemen Anggota Tim & Staf
    - 11.3 Manajemen Peran & Pembatasan Wewenang (Roles & Permissions)
    - 11.4 Pengelolaan Cabang Toko / Outlet
    - 11.5 Kustomisasi Susunan Menu Bilah Sisi (Sidebar Settings)
    - 11.6 Keamanan Akun & Konfigurasi MFA
    - 11.7 Paket Langganan & Tagihan (Subscription & Billing)
    - 11.8 Tur Panduan Interaktif Aplikasi (Tutorial System)
12. [BAB 12: STUDI KASUS OPERASIONAL & PERBANDINGAN PERAN](#bab-12-studi-kasus-operasional--perbandingan-peran)
    - 12.1 Skenario Pemilik vs Karyawan di Toko Maju Jaya
    - 12.2 Skenario Operasional Multi-Tenant Warung Segar
13. [BAB 13: PORTAL ADMINISTRATOR PLATFORM (SUPERADMIN)](#bab-13-portal-administrator-platform-superadmin)
    - 13.1 Beranda Admin & Metrik Sistem Global
    - 13.2 Manajemen Tenant & Badan Usaha Terdaftar
    - 13.3 Manajemen Pengguna Platform
    - 13.4 Pengelolaan Paket & Langganan SaaS
    - 13.5 Manajemen Insiden & Log Audit Sistem
    - 13.6 Pengawasan Keamanan Platform
14. [BAB 14: PANDUAN PEMECAHAN MASALAH, FAQ, & GLOSARIUM](#bab-14-panduan-pemecahan-masalah-faq--glosarium)
    - 14.1 Panduan Pemecahan Masalah (Troubleshooting)
    - 14.2 Pertanyaan yang Sering Diajukan (FAQ)
    - 14.3 Glosarium Istilah Akuntansi & ERP

---

# BAB 1: PENDAHULUAN & PROFIL APLIKASI

## 1.1 Mengenal KePin — Solusi Pembukuan Terpadu UMKM
Banyak pemilik bisnis mikro, kecil, dan menengah (UMKM) menghadapi kendala klasik: transaksi dicatat di buku tulis, stok dihitung manual lewat ingatan kasir, tagihan pelanggan tercecer di aplikasi pesan singkat, dan utang ke pemasok sering terlupakan. Dampaknya, pemilik tidak dapat mengetahui secara pasti apakah usahanya sedang untung atau rugi.

**KePin (Keuangan Pintar)** hadir sebagai platform ERP (*Enterprise Resource Planning*) modern berbasis Cloud dan web browser. KePin menyatukan seluruh siklus bisnis:
- **Penjualan Kasir (POS):** Input kasir cepat, dukung barcode scanner dan struk termal.
- **Manajemen Inventori:** Stok terpotong saat terjual dan bertambah saat pembelian diterima.
- **Akuntansi Otomatis:** Setiap transaksi kasir atau faktur langsung membentuk jurnal berpasangan (*double-entry*) tanpa perlu entri manual oleh akuntan.
- **Laporan Keuangan Real-Time:** Neraca, Laba Rugi, dan Arus Kas selalu siap saji setiap detik.

---

## 1.2 Konsep Arsitektur Multi-Tenant SaaS
KePin mengadopsi model **Multi-Tenant terisolasi**. Setiap perusahaan (*tenant*) memiliki ruang kerja mandiri, basis data terisolasi secara logis melalui ID Tenant, serta peran pengguna yang independen. Satu pengguna dapat menjadi pemilik pada perusahaannya sendiri, sekaligus menjadi staf pada usaha rekannya, tanpa ada kebocoran data (*cross-tenant data leakage*).

---

## 1.3 Aliran Integrasi Data Otomatis (*Seamless Sync Engine*)
Keunggulan utama KePin terletak pada **mesin kanonik akuntansi**:
\`\`\`text
[ Kasir POS / Faktur Penjualan ] ──▶ [ Pengurangan Stok Otomatis ]
              │                                      │
              ▼                                      ▼
[ Jurnal Otomatis: Debit Kas / Kredit Penjualan ] ──▶ [ Jurnal HPP / Persediaan ]
              │                                      │
              ▼                                      ▼
   [ Buku Besar & Neraca ] ◀──────────────▶ [ Laporan Laba Rugi ]
\`\`\`
Tidak ada lagi rekonsiliasi manual yang memakan waktu berhari-hari di akhir bulan.

---

## 1.4 Matriks Hak Akses & Pembagian Peran Pengguna (RBAC)
KePin menerapkan sistem keamanan terintegrasi berbasis peran (*Role-Based Access Control* / RBAC) untuk memastikan pemisahan kewenangan (*segregation of duties*), menjaga kerahasiaan data finansial strategis, serta mencegah penyalahgunaan data operasional perusahaan:

| Tingkatan Peran | Fungsi & Tanggung Jawab | Modul yang Dapat Diakses | Batasan Akses (*Restrictions*) |
|---|---|---|---|
| **Pemilik Usaha (Owner)** | Pengendali tertinggi dan penanggung jawab penuh badan usaha tenant. | Akses penuh (*Full Control*): POS Kasir, Penjualan, Pembelian, Inventori, Akuntansi & Jurnal Umum, Laporan Keuangan, Modal Awal, Anggota Tim, Cabang, dan Billing Langganan. | Tidak ada pembatasan dalam lingkup tenant terkait. |
| **Manajer Keuangan (Finance)** | Pengelola pembukuan, rekonsiliasi arus kas, penagihan piutang, dan pelaporan perpajakan. | Faktur Penjualan, Tagihan & PO Pembelian, Inventori, Bagan Akun (CoA), Jurnal Umum, Rekonsiliasi Bank, dan Laporan Finansial. | Dibatasi dari mutasi kepemilikan tenant, paket langganan SaaS, dan perubahan hak akses tim. |
| **Kasir / Karyawan (Employee)** | Pelaksana operasional pelayanan transaksi jual-beli langsung di gerai/toko. | Terminal Kasir (POS), Pencarian Katalog & Cek Stok Produk, serta Riwayat Transaksi Penjualan shift berjalan. | Tertutup secara ketat dari modul Akuntansi, Jurnal Umum, Laba Rugi, Pengaturan Modal Awal, dan Pengaturan Organisasi. |
| **Administrator Platform (Superadmin)** | Pengelola operasional sistem cloud global KePin (multi-tenant infrastructure). | Portal Admin Platform (\`/admin\`), Monitoring Tenant Global, Log Jejak Audit Keamanan, Manajemen Insiden, dan Pengaturan Paket Layanan. | Tidak mengintervensi atau mengubah data transaksi pembukuan privat milik masing-masing tenant. |

---

## 1.5 Kebutuhan Sistem & Kompatibilitas Perangkat
- **Perangkat Keras:** Laptop, Komputer Desktop, Tablet (iPad / Android), atau Smartphone modern.
- **Peramban Web (Browser):** Google Chrome (v110+), Mozilla Firefox (v110+), Safari (v16+), Microsoft Edge (v110+).
- **Koneksi Jaringan:** Akses internet stabil (minimal 512 Kbps) dengan dukungan enkripsi HTTPS/TLS 1.3.

---

# BAB 2: HALAMAN PUBLIK & AUTENTIKASI PENGGUNA

## 2.1 Menjelajahi Landing Page Resmi
Landing page KePin dirancang untuk memberikan informasi komprehensif bagi calon pengguna, mencakup pemaparan masalah UMKM, solusi komprehensif, fitur utama, arsitektur keamanan, paket harga, hingga FAQ.

![Landing Page Hero - KePin](images/01_landing_hero.png)
*Gambar 2.1: Tampilan Utama Landing Page (Header Sticky, Hero Section, & Call-to-Action)*

### Bagian Fitur & Solusi
Menampilkan bagaimana KePin menyelesaikan masalah pembukuan tradisional melalui otomatisasi alur kasir, stok, dan pencatatan laporan laba rugi.

![Fitur & Solusi KePin](images/02_landing_features.png)
*Gambar 2.2: Bagian Solusi & Fitur Unggulan untuk Efisiensi Bisnis UMKM*

### Pilihan Paket & FAQ
KePin menyediakan paket berjenjang (Starter, Pro, dan Enterprise/Platinum) yang disesuaikan dengan skala omzet dan kebutuhan jumlah cabang.

![Paket Harga & FAQ](images/03_landing_pricing.png)
*Gambar 2.3: Matriks Harga Berlangganan dan Tanya Jawab (FAQ)*

---

## 2.2 Panduan Masuk ke Sistem (Login)
Untuk mengakses ruang kerja atau portal admin:
1. Kunjungi halaman \`/auth/login\`.
2. Masukkan alamat **Email** dan **Kata Sandi** yang terdaftar.
3. Klik tombol **Masuk**.
4. Sistem secara otomatis mendeteksi peran:
   - Jika akun memiliki tenant, langsung diarahkan ke Dashboard Workspace tenant terkait (\`/app/[slug]\`).
   - Jika akun adalah Superadmin, diarahkan ke Dashboard Platform Admin (\`/admin\`).

![Halaman Login KePin](images/04_auth_login.png)
*Gambar 2.4: Formulir Masuk Sistem KePin*

---

## 2.3 Pendaftaran Akun Baru (Register)
Pengguna baru yang belum memiliki akun dapat mendaftar dengan mudah:
1. Buka \`/auth/register\`.
2. Isi Nama Lengkap, Alamat Email Aktif, Nomor WhatsApp/Telepon, dan Buat Kata Sandi yang kuat.
3. Klik tombol **Daftar Akun**.

![Halaman Register KePin](images/05_auth_register.png)
*Gambar 2.5: Formulir Registrasi Akun Pengguna Baru*

---

## 2.4 Membuat Perusahaan Baru (Create Tenant)
Setelah akun dibuat, pengguna dapat mendirikan ruang kerja perusahaannya sendiri:
1. Isi Nama Perusahaan (misal: *PT Berkah Abadi* atau *Toko Maju Jaya*).
2. Tentukan Slug URL (misal: *toko-maju*).
3. Pilih Sektor Bisnis (Ritel, F&B, Jasa, Manufaktur, dll.) serta Mata Uang dasar (IDR).
4. Klik **Buat Perusahaan**.

![Buat Perusahaan Baru](images/06_auth_create_company.png)
*Gambar 2.6: Formulir Pembuatan Tenant / Perusahaan Baru*

---

## 2.5 Bergabung ke Perusahaan dengan Kode Undangan (Join Code)
Bagi staf atau karyawan yang diundang oleh pemilik perusahaan:
1. Dapatkan **Kode Undangan (Join Code)** 16-karakter dari pemilik usaha.
2. Buka menu \`/auth/join-company\`.
3. Masukkan kode undangan tersebut dan klik **Gabung Perusahaan**.
4. Akun Anda langsung terhubung sebagai anggota resmi tenant tersebut.

![Gabung Perusahaan](images/07_auth_join_company.png)
*Gambar 2.7: Formulir Penggabungan Anggota Melalui Join Code*

---

## 2.6 Pemulihan Kata Sandi & 2.7 Verifikasi Dua Langkah (MFA)
KePin menyediakan sistem reset password berbasis token email yang aman (\`/auth/forgot-password\`) serta perlindungan autentikasi dua faktor berbasis OTP (TOTP/MFA) untuk melindungi akun dari akses tidak sah.

---

# BAB 3: WORKSPACE PERUSAHAAN (TENANT DASHBOARD)

## 3.1 Tata Letak Workspace
Workspace KePin memiliki struktur ergonomis:
- **Header Atas:** Menampilkan nama tenant aktif, switcher cabang, lonceng notifikasi, dan menu profil.
- **Sidebar Kiri Dinamis:** Navigasi cepat ke seluruh modul (Dashboard, POS, Penjualan, Pembelian, Inventori, Akuntansi, Laporan, Insights, Audit, Pengaturan).
- **Area Kerja Utama:** Menampilkan tabel, grafik interaktif, formulir aksi, dan metrik bisnis.

![Dashboard Utama Tenant](images/08_workspace_dashboard.png)
*Gambar 3.1: Dashboard Ruang Kerja Tenant Toko Maju Jaya*

---

## 3.2 Menelaah Indikator Kinerja Utama (KPI Metrics)
Di bagian atas dashboard, terdapat 4 kartu metrik utama:
- **Total Omzet / Pendapatan:** Akumulasi penjualan kotor dan bersih pada periode yang dipilih.
- **Laba Kotor:** Pendapatan dikurangi Beban Pokok Penjualan (HPP).
- **Pengeluaran Operasional:** Akumulasi beban listrik, sewa, gaji, dan biaya operasional.
- **Saldo Kas & Bank:** Posisi likuiditas kas tunai dan rekening bank saat ini.

---

## 3.3 Grafik Tren Omzet & 3.4 Ringkasan Piutang/Utang
- **Grafik Tren Penjualan:** Visualisasi harian/mingguan performa omzet toko.
- **Kartu Aging Piutang (AR):** Menampilkan tagihan ke konsumen yang belum lunas (0-30 hari, 31-60 hari, >60 hari).
- **Kartu Aging Utang (AP):** Mengingatkan jatuh tempo tagihan ke supplier agar tidak terkena denda.

---

# BAB 4: MESIN KASIR DIGITAL (POINT OF SALE / POS)

## 4.1 Antarmuka Kasir Digital KePin
Modul POS KePin didesain untuk transaksi kasir super cepat dan responsif:
- Panel kiri menampilkan kartu-kartu produk dengan foto, harga jual, dan stok tersisa.
- Kolom pencarian instan dan filter kategori produk memudahkan pencarian dalam hitungan detik.
- Panel kanan menampilkan **Keranjang Belanja Aktif (Cart)**, rincian subtotal, diskon, dan pajak (PPN).

![Mesin Kasir Digital POS](images/09_pos_cashier.png)
*Gambar 4.1: Antarmuka Mesin Kasir Digital (POS) Toko Maju Jaya*

---

## 4.2 Alur Transaksi Kasir Step-by-Step
1. **Pilih Produk:** Klik pada kartu produk atau scan barcode menggunakan scanner fisik. Produk akan langsung masuk ke keranjang.
2. **Atur Kuantitas:** Gunakan tombol \`+\` atau \`-\` untuk mengubah jumlah beli.
3. **Beri Diskon:** Masukkan persentase atau nominal diskon jika ada promosi toko.
4. **Pilih Pelanggan:** Pilih pelanggan umum (Walk-in Customer) atau pilih nama pelanggan terdaftar.
5. **Klik Tombol Pembayaran (Bayar).**

---

## 4.3 Pemrosesan Pembayaran & Cetak Struk
- **Pembayaran Tunai:** Masukkan nominal uang yang diterima pembeli. Sistem otomatis menghitung jumlah kembalian secara tepat.
- **Pembayaran Non-Tunai:** Tersedia opsi QRIS Dinamis dan Transfer Bank.
- **Selesai & Cetak Struk:** Klik tombol Selesaikan Transaksi. Dialog cetak struk nota kasir otomatis terbuka untuk printer kasir thermal (58mm / 80mm).

---

# BAB 5: MODUL PENJUALAN (SALES MANAGEMENT)

## 5.1 Riwayat Transaksi Penjualan Lengkap
Semua transaksi kasir dan penjualan grosir tersimpan dalam buku transaksi penjualan. Pengguna dapat memfilter berdasarkan tanggal, metode pembayaran, kasir bertugas, maupun status lunas.

![Faktur Penjualan Invoices](images/10_sales_invoices.png)
*Gambar 5.1: Daftar Faktur Penjualan (Invoicing) Toko Maju Jaya*

---

## 5.2 Pengelolaan Faktur Penjualan (Invoices)
Untuk transaksi penjualan secara kredit atau bertempo:
1. Buat invoice baru melalui tombol **Tambah Faktur**.
2. Masukkan nomor faktur, tanggal terbit, jatuh tempo, serta item barang.
3. Pantau status faktur: \`DRAFT\`, \`TERKIRIM\`, \`LUNAS\`, atau \`JATUH TEMPO\`.
4. Saat pembayaran diterima, catat pelunasan parsial atau lunas. Sistem otomatis memperbarui saldo kas dan mengurangi piutang usaha di neraca.

---

## 5.3 Manajemen Basis Data Pelanggan (Customer Directory)
KePin menyediakan modul CRM sederhana untuk mengelola relasi pelanggan:
- Menyimpan nama, nomor kontak, email, alamat pengiriman, dan batas kredit piutang (*credit limit*).
- Menampilkan total akumulasi belanja dan sisa piutang setiap pelanggan.

![Daftar Pelanggan](images/11_sales_customers.png)
*Gambar 5.2: Manajemen Direktori Pelanggan Toko Maju Jaya*

---

# BAB 6: MODUL PEMBELIAN & PENGADAAN (PURCHASING)

## 6.1 Pembuatan Pesanan Pembelian (Purchase Orders - PO)
Saat stok barang di toko menipis, manajer operasional dapat membuat Purchase Order (PO) ke pemasok:
1. Buka menu **Pembelian > Pesanan Pembelian (PO)**.
2. Klik **Buat Pesanan Baru**, pilih pemasok, tanggal perkiraan kirim, dan daftar produk serta harga beli disepakati.
3. PO dapat dicetak atau diekspor ke PDF untuk dikirimkan ke pemasok via WhatsApp / Email.

![Pesanan Pembelian PO](images/12_purchasing_orders.png)
*Gambar 6.1: Daftar Pesanan Pembelian (Purchase Orders) Toko Maju Jaya*

---

## 6.2 Penerimaan Barang & Pembayaran Tagihan Pemasok
- **Penerimaan Barang:** Ketika barang kiriman dari pemasok tiba, lakukan verifikasi fisik dan klik **Konfirmasi Terima Barang**. Stok produk di gudang secara otomatis bertambah.
- **Pembayaran Pemasok:** Pada modul Pembayaran Pemasok, catat transfer pembayaran utang dagang beserta bukti potong atau nomor referensi bank.

![Pembayaran Pemasok](images/13_purchasing_payments.png)
*Gambar 6.2: Pengelolaan Pembayaran Tagihan Pemasok (Bills & Payments)*

---

## 6.3 Manajemen Basis Data Pemasok (Vendor Management)
Kelola profil seluruh pemasok, PIC yang dapat dihubungi, termin pembayaran (misal: Net 30 hari, COD), serta riwayat pengadaan historis.

![Daftar Pemasok Vendor](images/14_purchasing_suppliers.png)
*Gambar 6.3: Direktori Pemasok Bahan Baku & Barang Dagangan*

---

# BAB 7: MODUL INVENTORI & MANAJEMEN GUDANG

## 7.1 Katalog Produk, SKU, & Manajemen Stok
Modul inventori KePin memberikan visibilitas penuh terhadap seluruh barang dagangan:
- **Informasi Produk:** Kode SKU unik, Nama Produk, Kategori, Satuan (Pcs, Box, Kg, Liter), Harga Beli Pokok, dan Harga Jual.
- **Ambang Batas Minimum (*Min Stock Alert*):** Jika stok berada di bawah batas minimum, sistem otomatis memunculkan indikator warna merah dan mengirimkan notifikasi restock.

![Katalog Produk Inventori](images/15_inventory_products.png)
*Gambar 7.1: Katalog Produk & Pemantauan Stok Toko Maju Jaya*

---

## 7.2 Log Mutasi Stok Barang (Stock Movements)
Setiap keluar-masuknya barang tercatat secara permanen tanpa celah kebocoran:
- **Penjualan Kasir:** Stok berkurang otomatis dengan referensi nomor struk.
- **Penerimaan PO:** Stok bertambah dengan referensi nomor PO.
- **Penyesuaian Stok (Stock Opname):** Penyesuaian jika ditemukan barang rusak, kadaluarsa, atau selisih hitung fisik.

![Mutasi Stok Inventori](images/16_inventory_movements.png)
*Gambar 7.2: Log Riwayat Mutasi Keluar-Masuk Stok Barang*

---

# BAB 8: MODUL AKUNTANSI & PEMBUKUAN KEUANGAN

## 8.1 Bagan Akun Standar (Chart of Accounts / CoA)
KePin menyediakan struktur Bagan Akun terstandarisasi PSAK yang langsung aktif sejak perusahaan didirikan:
- **1000 - Aset / Aktiva:** Kas Toko, Rekening Bank BCA/Mandiri, Piutang Dagang, Persediaan Barang Dagang.
- **2000 - Kewajiban / Utang:** Utang Usaha Dagang, Utang Gaji, Utang Pajak PPN.
- **3000 - Modal / Ekuitas:** Modal Pemilik Usaha, Laba Ditahan (*Retained Earnings*).
- **4000 - Pendapatan:** Pendapatan Penjualan Ritel, Pendapatan Jasa, Pendapatan Lain-lain.
- **5000 - Beban Pokok Penjualan (HPP):** Biaya Pembelian Barang Terjual.
- **6000 - Beban Operasional:** Beban Sewa Ruko, Listrik, Air, Gaji Pegawai, Pemeliharaan Toko.

![Bagan Akun CoA](images/17_accounting_chart_of_accounts.png)
*Gambar 8.1: Daftar Bagan Akun (Chart of Accounts) Toko Maju Jaya*

---

## 8.2 Konfigurasi Modal Awal Usaha (Initial Capital Engine)
Fitur unggulan KePin yang membedakannya dari aplikasi akuntansi lain adalah **Mesin Modal Awal Terpadu**:
- Pemilik usaha dapat memasukkan nominal Modal Awal saat mendirikan toko (misal: Rp 50.000.000).
- Sistem otomatis menerbitkan jurnal kanonik pembuka: **Debit Kas (1000) / Kredit Modal Pemilik (3000)**.
- Seluruh neraca, laporan laba rugi, dan arus kas otomatis tersinkronisasi tanpa menyebabkan selisih neraca tidak seimbang (*unbalanced balance sheet*).

---

## 8.3 Jurnal Umum (General Journal Entries)
Untuk transaksi-transaksi non-kasir (seperti setoran modal tambahan, penyusutan inventaris, atau penyesuaian akhir bulan):
1. Buka menu **Akuntansi > Jurnal Umum**.
2. Klik **Buat Entri Jurnal**.
3. Pilih akun Debit dan Kredit beserta nominalnya.
4. Sistem memverifikasi bahwa total Debit harus sama dengan total Kredit sebelum jurnal dapat disimpan.

![Jurnal Umum Akuntansi](images/18_accounting_journals.png)
*Gambar 8.2: Buku Jurnal Umum & Entri Jurnal Transaksi*

---

## 8.4 Rekonsiliasi Bank
Membantu menyamakan saldo antara buku besar bank di KePin dengan rekening koran mutasi bank asli, menandai transaksi yang cocok (*matched*) dan menyoroti transaksi yang belum tercatat (*unreconciled*).

![Rekonsiliasi Bank](images/19_accounting_reconciliation.png)
*Gambar 8.3: Antarmuka Pencocokan & Rekonsiliasi Bank*

---

# BAB 9: MODUL LAPORAN KEUANGAN & EKSEKUTIF

## 9.1 Laporan Finansial Komprehensif
KePin menyediakan laporan keuangan standar audit yang dapat dicetak maupun diekspor ke PDF dan Excel:
1. **Laporan Laba Rugi (P&L):** Menampilkan perolehan pendapatan kotor, HPP, laba kotor, seluruh biaya beban operasional, hingga Laba Bersih Usaha (*Net Profit*).
2. **Laporan Neraca (Balance Sheet):** Menggambarkan posisi kekayaan usaha: \`Total Aset = Total Kewajiban + Total Ekuitas\`.
3. **Laporan Arus Kas (Cash Flow):** Menunjukkan aliran uang kas masuk dan keluar dari aktivitas operasi, investasi, dan pendanaan.
4. **Buku Besar (General Ledger):** Rincian mutasi setiap akun CoA secara mendalam.

![Laporan Keuangan Utama](images/20_reports_financial.png)
*Gambar 9.1: Pusat Laporan Keuangan (Laba Rugi, Neraca, Arus Kas)*

---

## 9.2 Laporan Khusus Investor & Ringkasan Eksekutif
Bagi UMKM yang memiliki pemodal luar atau ingin mengajukan pinjaman kredit perbankan, KePin menyediakan **Investor & Executive Summary Report**:
- Merangkum metrik valuasi, pertumbuhan penjualan bulan-ke-bulan (MoM Growth), margin laba bersih, serta tingkat perputaran persediaan barang (*inventory turnover*).

![Laporan Investor](images/21_reports_investor.png)
*Gambar 9.2: Laporan Eksekutif & Ringkasan Performa untuk Investor*

---

# BAB 10: WAWASAN BISNIS OTOMATIS (AI INSIGHTS) & AUDIT KEAMANAN

## 10.1 Analisis Wawasan Bisnis Otomatis (*Automated Insights*)
KePin memiliki mesin analitik pintar yang secara proaktif menganalisis data keuangan:
- **Deteksi Tren Penjualan:** Memberi tahu jika ada lonjakan atau penurunan transaksi yang signifikan.
- **Peringatan Margin Menipis:** Menyorot produk-produk yang dijual terlalu mendekati harga modal beli.
- **Rekomendasi Restock:** Menghitung perkiraan tanggal kehabisan stok berdasarkan kecepatan penjualan rata-rata.

![Wawasan Bisnis Otomatis](images/22_insights_analytics.png)
*Gambar 10.1: Dasbor Wawasan Bisnis Otomatis (Insights Analytics)*

---

## 10.2 Log Jejak Audit Aktivitas (Audit Trail)
Demi mencegah kecurangan (*fraud*) internal, KePin mencatat setiap aktivitas di ruang kerja secara mendalam:
- Siapa yang melakukan aksi (Nama & Email Pengguna).
- Jenis aksi (Login, Tambah Produk, Ubah Harga, Hapus Faktur, Posting Jurnal).
- Alamat IP pengguna dan waktu kejadian presisi (*timestamp*).
- Detail data sebelum vs sesudah perubahan (*diff view*).

![Log Audit Trail](images/23_audit_trail.png)
*Gambar 10.2: Buku Catatan Jejak Audit Keamanan Sistem*

---

## 10.3 Pusat Pemberitahuan & Notifikasi
Menampilkan seluruh pemberitahuan operasional penting: invoice yang mendekati tanggal jatuh tempo, stok barang yang telah habis, pembayaran supplier yang telah lunas, hingga notifikasi keamanan akun.

![Pusat Notifikasi](images/24_notifications.png)
*Gambar 10.3: Pusat Notifikasi dan Peringatan Sistem*

---

# BAB 11: PENGATURAN PERUSAHAAN & KUSTOMISASI WORKSPACE

## 11.1 Profil Organisasi, Legalitas, & Modal Awal
Pemilik usaha dapat melengkapi identitas legal perusahaannya:
- Nama Legal Badan Usaha (CV/PT/Toko).
- Nomor Pokok Wajib Pajak (NPWP).
- Alamat kantor/toko fisik dan nomor kontak resmi.
- Pengaturan nilai **Modal Awal Usaha** dan rekening default kas operasional.

![Pengaturan Organisasi](images/27_settings_organization.png)
*Gambar 11.1: Formulir Pengaturan Organisasi & Modal Awal*

---

## 11.2 Manajemen Anggota Tim & 11.3 Manajemen Peran (Roles & RBAC)
- **Undang Anggota:** Masukkan email staf untuk mengundangnya bergabung ke toko.
- **Penetapan Peran:** Tentukan peran apakah sebagai Owner, Manajer Keuangan, atau Kasir/Karyawan.
- **Manajemen Wewenang:** Sesuaikan hak akses agar kasir hanya bisa mengakses menu POS dan penjualan, tanpa bisa mengintip laporan laba rugi atau mengubah bagan akun.

![Manajemen Anggota Tim](images/28_settings_members.png)
*Gambar 11.2: Daftar Anggota Tim & Manajemen Hak Akses Karyawan*

![Manajemen Peran RBAC](images/29_settings_roles.png)
*Gambar 11.3: Konfigurasi Matriks Peran & Izin Pengguna*

---

## 11.4 Pengelolaan Multi-Cabang / Outlet
Bagi bisnis yang memiliki lebih dari satu toko atau gerai:
- Buat cabang baru (misal: *Cabang Pusat*, *Cabang Mall Kelapa Gading*).
- Pisahkan kasir, inventori stok, dan laporan omzet per masing-masing cabang, dengan konsolidasi laporan di tingkat pusat.

![Pengaturan Cabang Outlet](images/30_settings_branches.png)
*Gambar 11.4: Pengelolaan Cabang Toko & Outlet*

---

## 11.5 Kustomisasi Susunan Menu Bilah Sisi (Sidebar Settings)
Pengguna dapat menyesuaikan menu sidebar sesuai preferensi kerja harian:
- Sembunyikan modul yang tidak sering dipakai.
- Ubah urutan menu melalui antarmuka drag-and-drop.
- Simpan tata letak khusus untuk kasir agar fokus pada layar kasir tanpa distraksi menu lain.

![Kustomisasi Menu Sidebar](images/31_settings_sidebar.png)
*Gambar 11.5: Pengaturan Visibilitas & Tata Letak Menu Sidebar*

---

## 11.6 Keamanan Akun, 11.7 Paket Langganan, & 11.8 Tutorial Interaktif
- **Keamanan:** Ganti kata sandi berkala, aktifkan verifikasi 2 langkah (MFA), dan pantau daftar sesi login aktif.
- **Langganan (Billing):** Menampilkan paket berlangganan saat ini, masa aktif, kapasitas kuota transaksi, dan opsi upgrade paket.
- **Tutorial Interaktif:** Panduan langsung langkah-demi-langkah (tour walkthrough) di dalam layar aplikasi bagi pengguna pemula.

![Pengaturan Keamanan Akun](images/32_settings_security.png)
*Gambar 11.6: Pengaturan Keamanan Sandi & MFA Pengguna*

![Paket Langganan Billing](images/33_settings_billing.png)
*Gambar 11.7: Status Paket Langganan & Tagihan Tenant*

![Tutorial Interaktif Aplikasi](images/25_tutorial.png)
*Gambar 11.8: Fitur Panduan Interaktif (Walkthrough Tour) Bagi Pengguna Baru*

---

# BAB 12: STUDI KASUS OPERASIONAL & PERBANDINGAN PERAN

## 12.1 Skenario Pemilik vs Karyawan di Toko Maju Jaya
Toko Maju Jaya mencontohkan implementasi Role-Based Access Control yang ideal:

1. **Peran Pemilik Usaha (Owner):**
   - Memiliki visibilitas 100% terhadap seluruh sistem.
   - Mengontrol modal awal, mengatur hak akses gaji dan anggota, mengawasi laporan laba rugi dan penuaan utang dagang.
   
2. **Peran Karyawan / Kasir (Employee):**
   - Saat staf kasir masuk ke sistem, menu sidebar otomatis disaring (*restricted view*).
   - Kasir hanya melihat menu Kasir POS, Riwayat Transaksi Kasir, dan Cek Stok Barang.
   - Menu Akuntansi, Jurnal Umum, Pengaturan Modal Awal, dan Pengaturan Anggota disembunyikan secara aman.

![Tampilan Workspace Karyawan](images/34_employee_dashboard.png)
*Gambar 12.1: Tampilan Dashboard Dibatasi untuk Peran Karyawan / Kasir*

---

## 12.2 Skenario Operasional Multi-Tenant Warung Segar
Tenant kedua, **Warung Segar**, menggambarkan isolasi data multi-tenant yang sempurna:
- Menjalankan usaha ritel komoditas produk segar (sayur, buah, daging) dengan ruang kerja terisolasi mandiri.
- Memiliki katalog produk segar, harga jual, dan pelanggan yang terpisah 100% dari Toko Maju Jaya.
- Data transaksi dan laporan keuangan Warung Segar tidak dapat diakses oleh tenant lain, menjaga kerahasiaan dan privasi bisnis antar-tenant.

![Dashboard Warung Segar](images/35_warung_segar_dashboard.png)
*Gambar 12.2: Workspace Terpisah Milik Tenant Warung Segar*

![POS Kasir Warung Segar](images/36_warung_segar_pos.png)
*Gambar 12.3: Antarmuka Mesin Kasir Produk Segar di Warung Segar*

---

# BAB 13: PORTAL ADMINISTRATOR PLATFORM (SUPERADMIN)

Bagi pengelola pusat sistem dengan peran Platform Superadmin, tersedia portal backend tingkat sistem (\`/admin\`) untuk memantau performa platform secara global.

## 13.1 Beranda Admin & Metrik Sistem Global
Menampilkan total seluruh tenant yang terdaftar, total pengguna aktif harian (*Daily Active Users*), volume transaksi yang diproses di server, serta status kesehatan microservices dan API.

![Dashboard Admin Platform](images/37_admin_dashboard.png)
*Gambar 13.1: Beranda Platform Administrator KePin*

---

## 13.2 Manajemen Tenant & Badan Usaha
Superadmin dapat melihat daftar seluruh perusahaan yang menggunakan KePin, mengubah status tenant (*Active*, *Suspended*, *Archived*), serta menyesuaikan limit kuota transaksi.

![Manajemen Tenant Admin](images/38_admin_tenants.png)
*Gambar 13.2: Daftar Seluruh Tenant Perusahaan Terdaftar di Platform*

---

## 13.3 Manajemen Pengguna Platform Global
Daftar seluruh pengguna dari semua tenant. Admin platform dapat membantu membuka blokir akun, mereset status MFA atas permintaan resmi pemilik usaha, atau meninjau aktivitas pengguna mencurigakan.

![Manajemen Pengguna Admin](images/39_admin_users.png)
*Gambar 13.3: Direktori Pengguna Global Platform KePin*

---

## 13.4 Pengelolaan Paket & Langganan SaaS
Admin dapat mengatur paket langganan (Free Tier, Starter, Pro, Platinum), harga per bulan/tahun, serta fitur modul apa saja yang terbuka pada tiap tingkatan paket.

![Manajemen Langganan Admin](images/40_admin_subscriptions.png)
*Gambar 13.4: Manajemen Paket Berlangganan SaaS*

---

## 13.5 Manajemen Insiden & Log Audit Sistem Global
- **Manajemen Insiden:** Mencatat gangguan teknis, error 500, kegagalan antrean email, atau lonjakan latensi database.
- **Audit Global:** Menelusuri seluruh tindakan administratif tingkat platform untuk kepatuhan regulasi data pribadi (*data compliance*).

![Manajemen Insiden Admin](images/41_admin_incidents.png)
*Gambar 13.5: Panel Pemantauan & Manajemen Insiden Sistem*

![Audit Log Admin](images/42_admin_audit.png)
*Gambar 13.6: Buku Jejak Audit Global Platform Administrator*

![Keamanan Platform Admin](images/43_admin_security.png)
*Gambar 13.7: Parameter Konfigurasi Keamanan & Zero Trust Platform*

---

# BAB 14: PANDUAN PEMECAHAN MASALAH, FAQ, & GLOSARIUM

## 14.1 Panduan Pemecahan Masalah (Troubleshooting)

### Kasus 1: Selisih Neraca Tidak Seimbang (Unbalanced Balance Sheet)
- **Gejala:** Total Aset tidak sama dengan Total Kewajiban + Ekuitas.
- **Penyebab:** Ada entri jurnal umum manual yang tidak seimbang antara sisi Debit dan Kredit, atau modal awal belum diatur.
- **Solusi:** 
  1. Buka menu **Pengaturan > Organisasi**, pastikan nilai Modal Awal telah diisi dan tersimpan.
  2. Buka menu **Akuntansi > Jurnal Umum**, periksa apakah ada jurnal bertanda peringatan merah, lalu lakukan penyesuaian seimbang.

### Kasus 2: Stok Produk di Kasir Tidak Berkurang
- **Penyebab:** Opsi "Lacak Stok (Track Inventory)" pada produk tersebut dinonaktifkan saat produk dibuat.
- **Solusi:** Buka menu **Inventori > Produk**, klik Edit pada produk terkait, aktifkan opsi **Lacak Stok**, lalu simpan.

### Kasus 3: Karyawan Tidak Bisa Mengakses Menu Tertentu
- **Penyebab:** Pembatasan wewenang wajar oleh fitur Role-Based Access Control (RBAC).
- **Solusi:** Pemilik usaha (Owner) dapat membuka **Pengaturan > Peran & Izin** untuk memberikan izin modul yang bersangkutan jika diperlukan.

---

## 14.2 Pertanyaan yang Sering Diajukan (FAQ)

**T: Apakah data keuangan bisnis saya aman di KePin?**  
J: Sangat aman. KePin menggunakan enkripsi kelas industri (TLS 1.3 saat transmisi data, enkripsi AES-256 saat penyimpanan basis data), isolasi tenant logis yang ketat, serta fitur autentikasi dua faktor (MFA).

**T: Apakah struk kasir bisa dicetak tanpa internet?**  
J: Saat mencetak struk, browser berkomunikasi langsung dengan printer lokal (USB, Bluetooth, atau LAN) sehingga proses cetak tetap berjalan mulus.

**T: Apakah data laporan keuangan bisa diekspor ke Microsoft Excel?**  
J: Ya, seluruh laporan keuangan, daftar transaksi, dan inventori stok dapat diunduh dalam format Excel (.xlsx) dan dokumen PDF.

---

## 14.3 Glosarium Istilah Akuntansi & ERP

- **Tenant:** Entitas satu perusahaan atau badan usaha yang terdaftar di KePin dengan ruang kerja terisolasi.
- **CoA (Chart of Accounts):** Daftar nomor dan nama akun pembukuan standar (Kas, Piutang, Modal, Penjualan, dll.).
- **POS (Point of Sale):** Sistem mesin kasir digital tempat kasir menginput penjualan ke pembeli.
- **HPP (Harga Pokok Penjualan):** Total biaya modal yang dikeluarkan untuk memproduksi atau membeli barang yang berhasil terjual.
- **Jurnal Berpasangan (*Double-entry*):** Prinsip akuntansi di mana setiap transaksi dicatat pada minimal dua sisi yang setara: Debit dan Kredit.
- **Aging Piutang/Utang:** Pengelompokan umur tagihan berdasarkan lamanya waktu sejak tanggal jatuh tempo.
- **RBAC (Role-Based Access Control):** Mekanisme pembatasan wewenang fitur berdasarkan peran jabatan (Owner vs Karyawan).

---

*© 2026 KePin (Keuangan Pintar). Hak Cipta Dilindungi Undang-Undang.*  
*Dokumentasi Resmi KePin — Disimpan pada folder \`documentation/dokumen/\`.*
`;

fs.writeFileSync(OUT_PATH, content, 'utf8');
console.log('Successfully written Markdown guide to:', OUT_PATH);
