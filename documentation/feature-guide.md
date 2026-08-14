# Panduan Fitur & Halaman KePin — Landing Page hingga Workspace Tenant

Dokumen ini menjelaskan secara rinci dan lengkap **setiap halaman dan setiap fitur** pada aplikasi KePin, dimulai dari **landing page** (marketing), dilanjutkan ke **halaman autentikasi (auth)**, hingga ke **workspace tenant** (`/app/{tenantSlug}`). Dokumen ini disusun sebagai referensi fitur, bukan panduan teknis pengembangan.

> **Konteks singkat**: KePin adalah ERP SaaS multi-tenant untuk manajemen keuangan dan operasional bisnis kecil-menengah. Backend FastAPI + SvelteKit 5 + PostgreSQL. Seluruh UI berbahasa Indonesia.

---

## Daftar Isi

- [1. Landing Page (Marketing)](#1-landing-page-marketing)
  - [1.1 Header (Marketing Header)](#11-header-marketing-header)
  - [1.2 Hero Section](#12-hero-section)
  - [1.3 Trust Strip](#13-trust-strip)
  - [1.4 Seksi Masalah (`#solusi`)](#14-seksi-masalah-solusi)
  - [1.5 Alur Solusi](#15-alur-solusi)
  - [1.6 Seksi Fitur Unggulan (`#fitur`)](#16-seksi-fitur-unggulan-fitur)
  - [1.7 Seksi Keamanan Zero Trust (`#keamanan`)](#17-seksi-keamanan-zero-trust-keamanan)
  - [1.8 Seksi Cara Kerja (`#cara-kerja`)](#18-seksi-cara-kerja-cara-kerja)
  - [1.9 Seksi Use Case](#19-seksi-use-case)
  - [1.10 Seksi Pricing (`#harga`)](#110-seksi-pricing-harga)
  - [1.11 Early Adopter](#111-early-adopter)
  - [1.12 Seksi FAQ (`#faq`)](#112-seksi-faq-faq)
  - [1.13 Final CTA](#113-final-cta)
  - [1.14 Footer](#114-footer)
  - [1.15 Halaman Legal (Privacy / Terms / Security)](#115-halaman-legal-privacy--terms--security)
- [2. Halaman Autentikasi (Auth)](#2-halaman-autentikasi-auth)
  - [2.1 Login (`/auth/login`)](#21-login-authlogin)
  - [2.2 Register (`/auth/register`)](#22-register-authregister)
  - [2.3 Create Company (`/auth/create-company`)](#23-create-company-authcreate-company)
  - [2.4 Join Company (`/auth/join-company`)](#24-join-company-authjoin-company)
  - [2.5 Forgot Password (`/auth/forgot-password`)](#25-forgot-password-authforgot-password)
  - [2.6 Reset Password (`/auth/reset-password`)](#26-reset-password-authreset-password)
  - [2.7 MFA (`/auth/mfa`)](#27-mfa-authmfa)
  - [2.8 Onboarding (`/auth/onboarding`)](#28-onboarding-authonboarding)
- [3. Workspace Tenant (`/app/{tenantSlug}`)](#3-workspace-tenant-apptenantslug)
  - [3.0 Layout & Shell Workspace](#30-layout--shell-workspace)
  - [3.1 Dashboard](#31-dashboard)
  - [3.2 POS (Point of Sale)](#32-pos-point-of-sale)
  - [3.3 Sales](#33-sales)
  - [3.4 Purchasing](#34-purchasing)
  - [3.5 Inventory](#35-inventory)
  - [3.6 Accounting](#36-accounting)
  - [3.7 Reports](#37-reports)
  - [3.8 Insights](#38-insights)
  - [3.9 Audit](#39-audit)
  - [3.10 Notifications](#310-notifications)
  - [3.11 Tutorial](#311-tutorial)
  - [3.12 Transactions](#312-transactions)
  - [3.13 Settings](#313-settings)
- [4. Ringkasan Peran (Owner vs Employee)](#4-ringkasan-peran-owner-vs-employee)
- [5. Lampiran: Temuan Analisis](#5-lampiran-temuan-analisis)

---

# 1. Landing Page (Marketing)

Landing page berada pada rute `/` (halaman utama) plus tiga halaman legal (`/privacy`, `/terms`, `/security`). Seluruh halaman marketing di-render secara client-side (tidak ada data server). Halaman ini terdiri dari **13 seksi** pada halaman utama, ditambah header dan footer.

## 1.1 Header (Marketing Header)

Header bersifat **sticky/fixed** di bagian atas:

| Elemen | Perilaku / Fungsi |
|---|---|
| Latar belakang | Transparan saat di atas halaman (`scrollY <= 20`); berubah menjadi kartu ber-latar + bayangan setelah di-scroll lebih dari 20px. |
| Logo KePin | Klik → kembali ke `/`. |
| Menu navigasi tengah (desktop) | 6 link anchor ke seksi: **Solusi** (`#solusi`), **Fitur** (`#fitur`), **Keamanan** (`#keamanan`), **Cara Kerja** (`#cara-kerja`), **Harga** (`#harga`), **FAQ** (`#faq`). |
| Tombol bantuan (ikon `?`) | Memulai **guided tour** (Driver.js) yang berjalan dari landing → auth → workspace. |
| Theme menu | Ganti tema **Light / Dark / System**; preferensi disimpan di cookie `kepin_theme`. |
| CTA auth-aware | Dihitung sekali saat halaman dimuat berdasarkan localStorage (`kepin_token`, `kepin_session`, `kepin_tenants`): |
| — Belum login | Tombol **"Masuk"** (ghost → `/auth/login`) dan **"Coba Gratis"** (primary → `/auth/register`). |
| — Login & superadmin | Tombol **"Panel"** → `/admin`. |
| — Login & punya tenant | Tombol berisi **nama tenant** (ikon gedung) → `/app/{slug tenant pertama}`. |
| — Login tanpa tenant | Tombol **"Lengkapi Profil"** → `/auth/onboarding`. |
| Mobile | Hamburger menu menampilkan dropdown berisi link anchor yang sama + link login/register/dashboard sesuai status login. |

> **Catatan**: status auth di header hanya dibaca **sekali saat mount**, tidak reaktif terhadap login/logout di tab yang sama (perlu reload).

## 1.2 Hero Section

Bagian pertama halaman (tinggi minimal 90vh), dengan latar dekoratif bentuk geometris (kotak, garis, lingkaran) bernuansa warna brand.

- **Headline** (3 baris, font besar):
  > Keuangan rapi. Operasional **terkendali**. Bisnis lebih **dipercaya**.
- **Sub-copy**: "KePin menyatukan akuntansi, inventaris, audit trail, dan insight bisnis untuk membantu UMKM tumbuh dengan keputusan yang lebih aman."
- **Dua CTA utama**:
  - **"Coba Gratis 14 Hari"** (tombol primary) → `/auth/register`.
  - **"Lihat Cara Kerja"** (tombol ghost) → scroll ke seksi `#solusi`.
- **Microcopy**: "Tanpa kartu kredit. Batalkan kapan saja."
- **Mock dashboard card** (hanya tampil di desktop, `lg:block`):
  - "Pendapatan Bulan Ini" — **Rp 89,5 Jt** dengan indikator **+12.5%** (hijau).
  - "Stok Kritis" — **3** dengan label **"Perlu restock"** (merah).
  - Placeholder grafik batang (ikon BarChart).
  - Footer kartu: ikon perisai "Audit trail aktif" + label "Live" (biru).

## 1.3 Trust Strip

Pita gelap (`#171714`) dengan 4 statistik statis (tanpa link):

| Statistik | Label |
|---|---|
| **5.000+** | UMKM Terdaftar |
| **50+** | Kota Tersebar |
| **99.9%** | Uptime Platform |
| **ISO 27001** | Sertifikasi Keamanan |

## 1.4 Seksi Masalah (`#solusi`)

Menampilkan 3 kartu masalah yang umum dialami UMKM, masing-masing dengan ikon kotak berwarna:

1. **Fraud & Selisih Terlambat Diketahui** (ikon jam, kotak merah) — stok hilang/uang tidak sesuai baru diketahui saat tutup buku; KePin memberi notifikasi real-time.
2. **Data Keuangan Tersebar** (ikon lapisan, kotak biru) — catatan di buku, stok di spreadsheet, pembayaran di aplikasi terpisah; sulit melihat gambaran utuh.
3. **Keputusan Tanpa Data** (ikon target, kotak kuning) — pembelian tanpa melihat tren; akibatnya dead stock, cash flow terhambat.

Kartu memakai gaya `card-hover` (efek hover). Tidak ada link keluar.

## 1.5 Alur Solusi

Flow horizontal 6 tahap yang dihubungkan panah (`ArrowRight`):

**Penjualan → Stok → Jurnal → Laporan → Insight → Keputusan**

- Setiap tahap berupa ikon lingkaran berwarna (merah, biru, hitam, kuning, hijau, merah) + label.
- Panah hanya tampil di layar `sm:` ke atas (tersembunyi di mobile).
- Murni informatif, tidak ada interaksi/link.

## 1.6 Seksi Fitur Unggulan (`#fitur`)

Grid 6 kartu fitur (3 kolom di desktop, 2 di tablet):

| Fitur | Ikon | Deskripsi |
|---|---|---|
| **Akuntansi Dasar** | Buku | Transaksi, chart of accounts, jurnal, buku besar, dan laporan keuangan lengkap. |
| **ERP Ringan** | Paket | Penjualan, pembelian, pemasok, pelanggan, produk, dan stok dalam satu platform. |
| **Audit Trail** | Perisai | Setiap perubahan tercatat: siapa, apa, kapan, tenant, dan nilai sebelum-sesudah. |
| **AI Insight** | Tren | Prediksi penjualan dan laba serta rekomendasi stok berdasarkan data bisnis. |
| **Investor Report** | Dokumen | Laporan kustom siap due diligence dengan metrik kredibel dan terverifikasi. |
| **Multi-Format Export** | Unduh | Ekspor laporan ke PDF, CSV, XLSX. Data tetap milik Anda. |

## 1.7 Seksi Keamanan Zero Trust (`#keamanan`)

Dua kolom:

- **Kolom kiri** — judul "Keamanan **Zero Trust**" + 5 poin safeguard dengan ikon centang hijau:
  1. Verifikasi identitas dan akses berdasarkan peran pengguna (RBAC).
  2. Isolasi data ketat antarorganisasi.
  3. Otentikasi multi-faktor (MFA) dan manajemen session.
  4. Audit trail append-only yang tidak dapat dimanipulasi.
  5. Enkripsi data dalam transit (TLS 1.3) dan penyimpanan.
  - **CTA "Pelajari Lebih Lanjut"** (ghost) → `/security`.
- **Kolom kanan** (desktop) — grid dekoratif 2×2: **ISO 27001** (merah), **Enkripsi** (hitam), **MFA** (biru), **Audit** (kuning).

## 1.8 Seksi Cara Kerja (`#cara-kerja`)

4 langkah bernomor besar (01–04) dengan gaya `card-hover`:

| No | Judul | Deskripsi |
|---|---|---|
| 01 | **Buat Workspace** | Daftar dan buat workspace bisnis. Isi profil, atur cabang, pilih template akun. |
| 02 | **Setup Bisnis** | Atur produk, pelanggan, pemasok, undang tim — semua dalam beberapa klik. |
| 03 | **Catat Transaksi** | Input penjualan, pembelian, pengeluaran. Stok dan jurnal ter-update otomatis. |
| 04 | **Pantau & Kembangkan** | Pantau dashboard, baca laporan, dapatkan insight AI, ambil keputusan lebih baik. |

## 1.9 Seksi Use Case

"Untuk Siapa KePin?" — 4 kartu segmen dengan ikon merah:

| Segmen | Ikon | Deskripsi |
|---|---|---|
| **Ritel** | Keranjang | Kontrol selisih stok dan identifikasi produk lambat bergerak secara real-time. |
| **F&B** | Pengguna | Kelola bahan baku, pembelian, biaya produksi, dan margin menu dalam satu tempat. |
| **Manufaktur Kecil** | Paket | Pantau bahan baku, proses produksi, hasil, dan biaya dasar produksi. |
| **Startup** | Tren | Transparansi arus kas dan laporan kredibel untuk investor dan dewan direksi. |

## 1.10 Seksi Pricing (`#harga`)

3 kartu paket; kartu Premium ditandai badge **"POPULER"** dan efek bayangan:

| Paket | Harga | Fitur | CTA |
|---|---|---|---|
| **Basic** | Rp199.000/bulan | Akuntansi dasar; 50 transaksi/bulan; 1 pengguna; 1 cabang; laporan laba rugi & neraca; dukungan email | **"Mulai Trial Gratis"** → `/auth/register` |
| **Premium** (POPULER) | Rp499.000/bulan | Semua fitur Basic; transaksi tak terbatas; 5 pengguna; 3 cabang; manajemen stok & produk; invoice & pelanggan; prediksi AI dasar; dukungan prioritas | **"Mulai Trial Gratis"** → `/auth/register?plan=premium` |
| **Platinum** | Rp999.000/bulan | Semua fitur Premium; pengguna tak terbatas; cabang tak terbatas; laporan investor kustom; audit trail lengkap; AI insight lanjutan; rekonsiliasi bank; dukungan dedicated | **"Jadwalkan Demo"** → `/auth/register` |

- Setiap fitur ditandai ikon centang hijau.
- Kartu Premium juga menampilkan catatan: *"Promo Early Adopter: 50% untuk tahun pertama"*.
- ⚠️ **Temuan**: parameter `?plan=premium` dikirim ke `/auth/register`, tetapi halaman register **tidak membaca** query parameter tersebut (param mati — lihat Lampiran).

## 1.11 Early Adopter

Banner merah penuh dengan CTA putih:

- Judul: "Program Early Adopter".
- Deskripsi: diskon 50% tahun pertama, kuota 50 klien pertama, imbalan testimoni & feedback.
- **CTA "Ambil Diskon Early Adopter"** → `/auth/register`.

## 1.12 Seksi FAQ (`#faq`)

6 pertanyaan dalam bentuk **accordion single-open** (membuka satu item otomatis menutup item lain):

| ID | Pertanyaan |
|---|---|
| `cocok` | Apakah KePin cocok untuk bisnis tanpa staf akuntansi? |
| `pemisahan` | Bagaimana pemisahan data antar perusahaan? |
| `cabang` | Apakah dapat mengelola banyak cabang? |
| `trial` | Apa yang terjadi setelah masa trial? |
| `ekspor` | Bagaimana cara ekspor data? |
| `prediksi` | Bagaimana prediksi AI bekerja? |

Perilaku interaktif:

- Klik header pertanyaan → jawaban muncul di bawah (dengan garis pemisah atas) dan **chevron berputar 180°** (via class `rotate-180`).
- Klik pertanyaan yang sama lagi → accordion tertutup (toggle).
- Jawaban menyebutkan dukungan ekspor PDF/CSV/XLSX dan cara kerja AI (rentang kepercayaan, faktor utama, periode).

## 1.13 Final CTA

Seksi penutup (putih / gelap sesuai tema):

- Headline: "Siap Mengelola Bisnis dengan Lebih Percaya Diri?"
- Sub-copy: ajakan bergabung dengan ribuan UMKM.
- Dua tombol:
  - **"Coba Gratis 14 Hari"** → `/auth/register`.
  - **"Jadwalkan Demo"** → `/auth/register?plan=platinum` (⚠️ param `plan=platinum` juga tidak dibaca register).
- Microcopy: "Tanpa kartu kredit. Dukungan setup gratis."

## 1.14 Footer

Footer gelap dengan grid 4 kolom:

| Kolom | Isi |
|---|---|
| **Brand** | Logo + tagline "Keuangan Pintar untuk UMKM Indonesia…" |
| **Produk** | Fitur → `/#fitur`; Harga → `/#harga`; Keamanan → `/security` |
| **Perusahaan** | Kebijakan Privasi → `/privacy`; Syarat & Ketentuan → `/terms` |
| **Bantuan** | `mailto:hello@kepin.id`; FAQ → `/#faq` |

Bar bawah: `© {tahun} KePin (Keuangan Pintar)` + menu tema.

## 1.15 Halaman Legal (Privacy / Terms / Security)

Ketiganya memakai header (PageHeader + breadcrumb) dan konten prosa statis:

### Privacy (`/privacy`)
5 bagian: Pengumpulan Data, Penggunaan Data, Keamanan Data, Hak Anda, Cookie.

### Terms (`/terms`)
5 bagian: Layanan, Akun & Tanggung Jawab, Pembayaran & Langganan, Batasan Tanggung Jawab, Penghentian Layanan.

### Security (`/security`)
- 6 kartu keamanan: **ISO 27001**, **Enkripsi End-to-End**, **Isolasi Tenant**, **Audit Trail Immutable**, **Multi-Factor Auth**, **Infrastruktur Aman**.
- Daftar "Praktik Keamanan".
- Link laporan kerentanan: `mailto:security@kepin.id`.

---

# 2. Halaman Autentikasi (Auth)

Semua halaman auth berada di grup `(auth)` dengan layout terpusat: header (logo → `/`, tombol tour `?`, theme menu) + kartu konten `max-w-md`. Tidak ada guard rute di level layout — halaman auth bisa diakses siapa saja.

Konvensi umum:

- Semua submit menggunakan `window.location.href` (reload penuh), bukan navigasi SvelteKit.
- Error ditampilkan dua kali: kotak error inline + toast.
- Session disimpan di **localStorage** dengan kunci: `kepin_session`, `kepin_token`, `kepin_tenants`, `kepin_mfa_token`.

## 2.1 Login (`/auth/login`)

| Fitur | Detail |
|---|---|
| Field | Email (`type=email`, required), Password (required) dengan **toggle tampil/sembunyi** (ikon mata). |
| Checkbox "Ingat saya" | ⚠️ Hanya visual — **tidak ada logika penyimpanan** (temuan, lihat Lampiran). |
| Link | "Lupa password?" → `/auth/forgot-password`; "Daftar gratis" → `/auth/register`. |
| Submit | `POST /auth/login` → |
| — MFA aktif | Redirect ke `/auth/mfa` (token MFA disimpan sementara). |
| — Sukses | Toast "Login berhasil"; **superadmin** → `/admin`; **punya tenant** → `/app/{slug}`; **tanpa tenant** → `/auth/onboarding`. |
| — Gagal | Pesan error inline + toast "Login gagal". |

## 2.2 Register (`/auth/register`)

| Fitur | Detail |
|---|---|
| Field | Nama Lengkap, Email, Password (`minlength=8`). Tanpa konfirmasi password / strength meter. |
| Submit | `POST /auth/register` → toast "Pendaftaran berhasil" → setelah ±1 detik redirect ke `/auth/login?onboarding=true` (harus login ulang; tidak auto-login). |
| Param URL | ⚠️ `?plan=` dari landing **tidak dibaca**; `?onboarding=true` di login juga **tidak dikonsumsi** (keduanya param mati — lihat Lampiran). |

## 2.3 Create Company (`/auth/create-company`)

Halaman untuk pengguna yang sudah login dan ingin membuat organisasi baru.

| Fitur | Detail |
|---|---|
| Field | **Nama Perusahaan** (auto-generate slug client-side: lowercase, spasi/karakter khusus → `-`), **Link Unik** (ditampilkan dengan prefix `/app/`), **Paket Langganan** (dropdown: Free Rp0 / Basic Rp99.000 / Premium Rp299.000 / Platinum Rp799.000 — default `free`). |
| Submit | `POST /auth/create-organization` `{name, slug, plan}` → toast sukses. |
| Setelah sukses | Form diganti layar **join code** ("Kode Bergabung Perusahaan" + kode mono). Slug & role disimpan ke `kepin_tenants`. Tombol **"Masuk ke Workspace"** → `/app/{slug}` atau **"Kembali"** → `/auth/onboarding`. |
| Gagal | Pesan `data.detail` inline + toast. |

> **Catatan**: paket pada halaman ini tidak terhubung dengan `?plan=` dari landing.

## 2.4 Join Company (`/auth/join-company`)

Halaman untuk bergabung ke organisasi lewat kode.

| Fitur | Detail |
|---|---|
| Field | **Kode Bergabung** (petunjuk 16 karakter, monospace, tengah). |
| Live lookup | Setiap input → `GET /auth/join-info?code=...` (tanpa auth). Jika valid, tampil kartu perusahaan (nama + `/app/{slug}`). Tombol submit hanya aktif saat info ditemukan. |
| Guard 1-tenant | Jika akun sudah punya tenant → form diganti peringatan "Satu akun hanya dapat bergabung ke satu perusahaan… keluar terlebih dahulu via menu *Keluar dari Perusahaan Ini*" + tombol ke `/app/{slug}` dan `/auth/onboarding`. |
| Submit | `POST /auth/join-by-code` `{join_code}` → simpan `{slug, role}` ke `kepin_tenants` → redirect `/app/{slug}`. |
| Gagal | Pesan `data.detail` inline + toast. |

## 2.5 Forgot Password (`/auth/forgot-password`)

| Fitur | Detail |
|---|---|
| Field | Email. |
| Submit | `POST /auth/forgot-password` → layar sukses "Jika email terdaftar, tautan reset akan dikirim…". |
| Dev mode | Karena layanan email belum terhubung, backend mengembalikan `dev_reset_token` → kotak "Mode pengembangan — layanan email belum terhubung" dengan tombol **"Salin Token"** (clipboard + toast) dan **"Lanjutkan Reset"** → `/auth/reset-password?token=...`. |
| Link | "Kembali ke Login" (bawah + layar sukses). |

## 2.6 Reset Password (`/auth/reset-password`)

| Fitur | Detail |
|---|---|
| Sumber token | Dibaca dari URL `?token=`; jika tidak ada, tampil field manual "Token Reset". |
| Field | Token (kondisional), Password Baru (`minlength=8`), Konfirmasi Password. |
| Validasi client | Password ≠ konfirmasi → "Konfirmasi password tidak sama."; token kosong → "Token reset tidak ditemukan." |
| Submit | `POST /auth/reset-password` `{token, new_password}` → layar sukses (ikon kunci) + tombol "Kembali ke Login" + toast. |

## 2.7 MFA (`/auth/mfa`)

Halaman verifikasi dua faktor setelah login (jika MFA aktif di akun).

| Fitur | Detail |
|---|---|
| Guard | Butuh `kepin_mfa_token` di localStorage; jika tidak ada → "Sesi verifikasi MFA tidak ditemukan atau telah kedaluwarsa." + "Kembali ke Login". |
| Tab Kode | 6 input digit (`maxlength=1`), **auto-advance** fokus ke input berikutnya, dukung **paste** string 6 karakter. |
| Tab Recovery | Input teks tunggal placeholder `XXXX-XXXX` (kode cadangan). |
| Submit | `POST /auth/mfa/verify` dengan token tersimpan → superadmin `/admin`; tenant `/app/{slug}`; tanpa tenant `/auth/onboarding`. |
| Gagal | Pesan inline + toast. |

## 2.8 Onboarding (`/auth/onboarding`)

| Fitur | Detail |
|---|---|
| Auto-redirect | Saat mount: superadmin → `/admin`; punya tenant → `/app/{slug tenant pertama}`; tanpa tenant → tampil layar pilihan. |
| Pilihan | **"Buat Perusahaan Baru"** → `/auth/create-company`; **"Gabung Perusahaan"** → `/auth/join-company`. |
| Logout | Tombol Logout → `logout()` lalu redirect ke `/`. |

---

# 3. Workspace Tenant (`/app/{tenantSlug}`)

Workspace adalah area utama aplikasi setelah login, di-scope per tenant (organisasi). Terdapat 28+ halaman dengan dua peran: `tenant_owner` dan `employee`.

## 3.0 Layout & Shell Workspace

### Guard & Preload (`(workspace)/+layout.svelte`)
- Pada setiap load memanggil `GET /tenants/{slug}/context`:
  - `401` → logout + redirect `/auth/login`.
  - `403` → layar "Akses Ditolak" (bukan anggota organisasi).
  - `404` → "Tenant Tidak Ditemukan".
  - Error lain → "Gagal Memuat Workspace" + tombol "Coba lagi".
  - Loading → skeleton "Memverifikasi akses workspace…".
- **Preload data** seluruh modul secara paralel (toleran gagal): sidebar settings, customers, suppliers, products, purchase orders, transactions, accounts, journals, invoices, branches, members, notifications, stock movements, audit events, inventory locations, supplier payments.
- Menentukan `currentRole` → menggerakkan UI owner vs employee.

### WorkspaceShell
- **Sidebar desktop** (collapsible `w-64 ⇄ w-16` dengan transisi), **drawer mobile** (overlay), **TopBar**, dan area konten `max-w-7xl`.
- **Branch banner**: "Cabang: Toko Pusat" + tombol "Ganti" — ⚠️ **stub**: tombol hanya menutup banner, belum ada switcher cabang (temuan, lihat Lampiran).

### WorkspaceSidebar
- Menu navigasi berbahasa Indonesia (dari `config/navigation.ts`), dikelompokkan dan bisa di-expand/collapse.
- **Filter visibilitas** via `isNavEnabled` (dari `TenantSidebarSetting`) — owner bisa menyembunyikan menu; item **pinned** (Dashboard, Pengaturan, Keamanan Akun, Tutorial) selalu tampil.
- Link **"Kustomisasi Sidebar"** hanya untuk owner.
- Deteksi halaman aktif (termasuk sub-halaman `/notifications`).

### TopBar
- **Kiri**: tombol hamburger (toggle drawer/collapse) + judul tenant.
- **Kanan**:
  - Tombol **Tutorial** (`?`) → `/app/{slug}/tutorial`.
  - **ThemeMenu** — light/dark/system, persist cookie `kepin_theme`.
  - **Bell Notifikasi** — badge jumlah belum dibaca (cap "9+"); dropdown 5 notifikasi teratas (titik unread, waktu relatif); klik → halaman detail; footer "Lihat Semua Notifikasi".
  - **Menu Profil** (nama + email):
    - **Edit Profil** → modal (nama/email/telepon) → simpan ke localStorage.
    - **Kembali ke Beranda** → `/`.
    - **Gabung Perusahaan** (hanya jika tanpa tenant) → `/auth/join-company`.
    - **Keluar dari Perusahaan Ini** (khusus employee) → konfirmasi → `leaveTenant` → `/auth/onboarding`.
    - **Logout** → konfirmasi → `/`.

## 3.1 Dashboard

Halaman utama workspace (`/app/{tenantSlug}/`).

| Fitur | Detail |
|---|---|
| Refresh | Muat ulang seluruh data (spinner). |
| Filter tanggal | Preset: 1 minggu / 2 minggu / 3 minggu / 1 bulan / custom (input tanggal + Terapkan). Default 7 hari terakhir. |
| Compare mode | Checkbox "Bandingkan dengan periode sebelumnya" → otomatis hitung periode sebelumnya (bisa diedit) → MetricCard menampilkan selisih +/- %. |
| Metrik (4) | **Pendapatan**, **Pengeluaran**, **Laba Bersih**, **Kas & Bank** (format IDR, delta di compare mode). |
| Aging AR/AP | Dua kartu: **Piutang Usaha** & **Hutang Usaha** — total + 5 bucket (Lancar, 1-30, 31-60, 61-90, >90); link → `/reports?tab=aging`. |
| Charts | **BarChart** arus kas harian (pemasukan hijau / pengeluaran merah); **PieChart** (donut) komposisi pengeluaran. |
| Alerts | Kartu "Perhatian" berisi daftar `dashboard.alerts` (mis. invoice jatuh tempo, stok rendah). |
| Tabel | Transaksi terbaru: Tanggal/Deskripsi/Tipe/Jumlah/Status, searchable. |

**API**: `GET /tenants/{slug}/dashboard?startDate&endDate`, `.../reports/receivable-aging`, `.../reports/payable-aging`.

## 3.2 POS (Point of Sale)

Layar kasir (`/app/{tenantSlug}/pos`).

| Fitur | Detail |
|---|---|
| Katalog produk (kiri) | Search debounce 250ms (nama/SKU/kategori); grid kartu (nama, SKU, harga, **badge stok live**: "Habis" / "Stok N" berwarna vs minStock); tombol "+ Keranjang" dan "Stok"; pagination 24/halaman (server-side). |
| Keranjang (kanan, sticky) | Line item dengan stepper qty (+/-), hapus (Trash), jumlah item & total live. |
| Pembayaran | `CurrencyInput` jumlah dibayar; shortcut **"Uang Pas"**; kembalian dihitung real-time (hijau cukup / merah "kurang Rp X"); tombol **Bayar** nonaktif jika keranjang kosong atau (jika jumlah > 0) jumlah < total. |
| Modal Stok | Per produk: toggle "Tambah stok / Kurangi stok", qty (min 1), alasan opsional, preview sebelum→sesudah. Membutuhkan lokasi inventory aktif. |
| Checkout | `POST /tenants/{slug}/pos/checkout` `{items, amount_paid}` → toast nomor checkout, keranjang dikosongkan, stok & stock movements di-refresh. |

## 3.3 Sales

### Customers (`/sales/customers`)
- **Search server-side** (debounce) + tabel: Kode/Nama/Email/Telepon/Bergabung (sortable).
- **CRUD**: "+ Pelanggan Baru" / Edit / Hapus (ConfirmDialog). Modal: kode, nama, email, telepon, alamat.
- **Statement** (aksi per baris) → `StatementModal` **"Kartu Piutang"**: range tanggal + Terapkan, saldo awal/akhir, tabel debet/kredit/saldo (sticky header, scroll), **export PDF/Excel**.
- **Export** 6 kolom, nama file `pelanggan`.

### Invoices (`/sales/invoices`)
- **Metrik**: Total Piutang (non-paid/cancelled), Outstanding (sent/partial/posted), Invoice Bulan Ini, Rata-rata.
- Tabel: No./Pelanggan/Tanggal/Jatuh Tempo/Total/Status (badge: Konsep/Terkirim/Sebagian/Dibayar/Lewat Jatuh Tempo/Dibatalkan), sortable, searchable.
- **Owner-only**: draft → **Post** (idempotent) / **Hapus**; posted → **Reverse** (konfirmasi native).
- **Modal buat invoice**: pelanggan, tanggal, catatan, **baris dinamis** (nama item, qty, harga satuan, PPN %, diskon), estimasi total live (termasuk pajak dikurangi diskon); tombol "Simpan Draft".
- **Export** 7 kolom, nama file `invoice`.

## 3.4 Purchasing

### Suppliers (`/purchasing/suppliers`)
- Tabel: Kode/Nama/Email/Telepon/Kota/Bergabung (sortable, searchable).
- **CRUD** penuh (modal: kode, nama, email `type=email`, telepon, kota).
- **Statement** → `StatementModal` **"Kartu Hutang"** (export PDF/Excel).
- **Export** 6 kolom, nama file `pemasok`. Tanpa gating role.

### Purchase Orders (`/purchasing/orders`)
- **Metrik**: Total PO Terbuka (draft/sent/partial), PO Bulan Ini, PO Diterima, Rata-rata Nilai PO.
- Tabel: No. PO/Pemasok/Tanggal/Jatuh Tempo/Item/Total/Status (Konsep/Terkirim/Sebagian/Diterima/Dibatalkan), sortable, searchable.
- **Owner-only per status**:
  - `draft` → **Kirim**, **Edit**, **Hapus**.
  - `sent` / `partial` → **Terima** (modal Receive).
  - `draft` / `sent` / `partial` → **Batal** (modal khusus).
- **Modal buat/edit PO**: pemasok, tanggal, catatan, baris dinamis (produk auto-isi nama + harga modal, qty, harga satuan, hapus), total berjalan live.
- **Modal Receive**: butuh lokasi inventory aktif (blokir jika tidak ada); qty per baris di-prefill dengan sisa belum diterima; catatan.
- **Export** 6 kolom, nama file `purchase-order`.

### Supplier Payments (`/purchasing/payments`)
- **Metrik**: Total Terbayar (posted), Dibayar Bulan Ini, Draft Menunggu Posting, Rata-rata.
- Tabel: No./Pemasok/Tanggal/Metode (Kas/Transfer Bank)/Jumlah/Status.
- **Owner-only**: draft → **Post**; posted → **Void** (membalik GL).
- **Modal buat**: pemasok, tanggal, metode (kas → akun Kas; bank → catatan akun bank), jumlah, referensi. Validasi client: pemasok + jumlah wajib.
- **Export** 6 kolom, nama file `supplier-payments`.

## 3.5 Inventory

### Products (`/inventory/products`)
- **Metrik**: Total Produk, Stok Kritis (0 < stok ≤ min), Nilai Stok (stok × harga modal), Dead Stock (stok ≤ min/2).
- **Search server-side** (debounce) + tabel: SKU/Nama/Kategori/Stok/Min/Harga Jual/Harga Modal/Status; pagination 20/halaman; kolom stok dari stock balances.
- **CRUD**: modal (SKU, kategori, nama, satuan, min stok, harga jual `CurrencyInput`, harga modal; status hanya saat edit).
- **Export** 8 kolom, nama file `produk`.

### Movements (`/inventory/movements`)
- Tabel **read-only**: Tanggal/Produk/Tipe (badge in/out/adjustment/transfer)/Qty/Stok Awal/Stok Akhir/Alasan; sortable, searchable, pageSize 5.
- **Export** 7 kolom, nama file `pergerakan-stok`.
- Reload otomatis saat mount; data diperbarui oleh POS/operasi stok lain.

### Transactions (`/inventory/transactions`)
- **Metrik**: Total Transaksi, Total Penjualan (halaman ini), Total Kembalian (halaman ini).
- **Search server-side** + tabel: No. Checkout/Tanggal/Ringkasan Produk (2 pertama + "+N lagi")/Qty/Total/Dibayar/Kembalian; pagination 20.
- **Detail modal**: ringkasan + tabel line-item (Produk/Qty/Harga Satuan/Subtotal + baris total).
- **Export** 7 kolom, nama file `transaksi-produk`. Read-only.

## 3.6 Accounting

### Chart of Accounts (`/accounting/chart-of-accounts`)
- Tabel: Kode/Nama Akun/Tipe (Asset/Liability/Equity/Income/Expense)/Saldo/Status; saldo diambil **per akun** (paralel); sortable (Kode/Nama), searchable.
- **CRUD**: modal (kode, tipe 5 pilihan, nama; status saat edit); `normalBalance` diturunkan otomatis (asset/expense → debit, lainnya kredit).
- **Export** 4 kolom, nama file `chart-of-accounts`.

### Fiscal Years (`/accounting/fiscal-years`)
- **Owner-only** (employee mendapat banner read-only; aksi tersembunyi).
- Kartu per tahun buku: nama, rentang tanggal, status (Terbuka/Ditutup/Soft Closed/Terkunci) + **tabel periode** (12 bulan) dengan aksi **Tutup / Buka** per periode (terkunci tidak bisa dibuka).
- Aksi: Refresh; owner **"+ Buat Tahun Buku"** (nama opsional + tanggal mulai/selesai); per tahun **"Tutup Tahun Buku" / "Buka Kembali"**.
- Pagination 10 tahun/halaman.

### Journals (`/accounting/journals`)
- **Filter akun** (select akun aktif) → reload jurnal (`?accountId=`); tombol "Reset".
- **Buku Besar**: checkbox "Lihat buku besar (saldo berjalan)" → kartu ledger dengan rentang tanggal + Terapkan, tabel (Tanggal/No. Jurnal/Deskripsi/Debit/Kredit/Saldo + baris saldo awal/akhir), pagination 25.
- Tabel jurnal: Tanggal/Referensi/Deskripsi/Status/Dibuat; sortable, searchable.
- **Owner-only**: draft → **Post** (idempotent); posted → **Reverse** (konfirmasi).
- **Modal buat jurnal**: tanggal, referensi, deskripsi, **editor baris dinamis** (akun, deskripsi, debet, kredit; min 2 baris), **indikator balance live** (debit = kredit dan ≥1 baris > 0 → "Simpan Draft" aktif).
- **Export** 5 kolom, nama file `jurnal`.

### Reconciliation (`/accounting/reconciliation`)
- **Kartu rekening bank**: nama bank, status (Aktif/Nonaktif), nomor ter-mask, saldo GL, jumlah & total statement, jumlah & total unmatched (amber). Owner: tombol edit & hapus.
- **Tabel transaksi bank**: filter per bank account; Tanggal/External ID/Deskripsi/Jumlah/Status (pill "Terkait" / "Belum dicocokkan"); aksi baris "Saran" (unmatched) + hapus (owner).
- **Tabel kandidat match**: ID/Bank Txn/Transaksi/Confidence/Status/Matched At/Catatan; owner **"Konfirmasi"**.
- **Owner-only (top bar)**: "+ Rekening Bank", "+ Impor Bank Txn", "+ Impor CSV", "Cocokkan Semua Saran" (bulk), "+ Buat Match".
- **6 modal**:
  1. Rekening bank — akun GL aset (saat buat), nama bank, nomor ter-mask, status (edit).
  2. Impor transaksi bank manual — akun, externalId, tanggal, jumlah, deskripsi.
  3. **Impor CSV** — akun + textarea (format `tanggal;deskripsi;jumlah`, negatif diperbolehkan, dedupe) → ringkasan dibuat/dilewati/error.
  4. Buat match manual — transaksi bank + transaksi internal posted + catatan.
  5. Saran — per transaksi bank: kandidat dengan skor + "Cocokkan".
  6. Hasil bulk — jumlah match + daftar dilewati + alasan.
- Employee: banner read-only, tanpa tombol (tetap bisa lihat saran).

## 3.7 Reports

Halaman terbesar dengan **7 tab** (didukung parameter URL `?tab=`): Ringkasan, Neraca Saldo, Laba Rugi, Neraca, Arus Kas, Aging, Valuasi Stok.

| Fitur global | Detail |
|---|---|
| Export | Pilih jenis export (`<select>`) + tombol **Ekspor** → `ExportModal` (PDF/Excel). |
| Refresh | Muat ulang. |
| Filter tanggal | `DateRangeFilter` (default 30 hari). |
| Kartu periode akuntansi | Nama periode + status (open/closed/locked) diturunkan dari fiscal years; **owner-only** tombol **"Tutup Periode" / "Buka Kembali"** (konfirmasi native); employee melihat "Read-only". |
| Compare mode | Checkbox + tanggal periode sebelumnya (mempengaruhi metrik ringkasan). |
| Metrik | Pendapatan/Beban/Laba/Piutang Outstanding + Total Aset/Kewajiban+Ekuitas/Selisih Neraca/Delta Stok vs GL. |

**Per tab:**

| Tab | Isi |
|---|---|
| **Ringkasan** | BarChart pendapatan vs beban harian + daftar "Beban Terbesar" (top 8). |
| **Neraca Saldo** | Checkbox "Sertakan jurnal penutup CLS/REV-CLS" (reload); indikator balance Dr/Cr; tabel (Saldo Awal / Debit&Kredit Periode / Debit&Kredit Akhir), sortable, pageSize 12, searchable. |
| **Laba Rugi** | Tabel P/L bulanan (Pendapatan/Beban/Laba + Δ vs bulan sebelumnya dengan kode warna +/-) + tabel akun. |
| **Neraca** | Tabel bulanan (Aset/Kewajiban/Ekuitas/Total + Δ Aset) + tabel akun. |
| **Arus Kas** | 4 metrik (Operasi/Investasi/Pendanaan/Net), legenda kategori, tabel bulanan dengan delta, tabel transaksi (Masuk/Keluar ditampilkan `-` bila nol). |
| **Aging** | Total AR/AP, per-bucket (jumlah invoice/GRN), ringkasan pemasok (Diterima/Dibayar/Outstanding/Bucket), tabel per pelanggan & pemasok dengan aksi **"Kartu piutang" / "Kartu hutang"** → `StatementModal`. |
| **Valuasi Stok** | SKU/Produk/Qty/Avg Cost/Nilai. |

**Export**: 8 jenis termasuk **Aging Detail** — yang menghasilkan **XLSX multi-sheet** (sheet "Piutang (Aging)" & "Hutang (Aging)") dengan total agregat. Nama file `laporan-{kind}`.

**Loading**: 12 request paralel (summary, P&L, balance sheet, trial balance ± closing, aging AR/AP asOf, stock valuation asOf, cash flow, versi bulanan ×3, fiscal years) dengan guard urutan request.

### Investor Report (`/reports/investor`)
- **Executive summary** naratif: pendapatan 6 bulan, gross margin %, posisi kas, runway (bulan).
- **5 MetricCard**: Pendapatan 6B, Gross Margin, Margin %, Cash Position, Runway (unit "bulan").
- **Charts**: BarChart pendapatan vs beban bulanan + donut komposisi pengeluaran.
- **Aksi**: **Bagikan** (`navigator.share`, fallback clipboard + toast), **Refresh**, **Ekspor** (baris label/nilai termasuk rincian per kategori beban).
- Banner error API. Tanpa tabel/CRUD.

## 3.8 Insights

- Filter rentang tanggal (default 30 hari) + compare mode + 4 metrik + BarChart (serupa dashboard).
- **Feed insight**: kartu `{judul, deskripsi, dampak (positif/negatif/netral), horizon, faktor[]}` dengan ikon hijau/kuning; tampil 6 pertama + toggle "Tampilkan semua (N)".
- Data insight berasal dari payload `GET /tenants/{slug}/dashboard` (tidak ada endpoint khusus).

## 3.9 Audit

- **Filter pill tipe objek**: dari `GET /tenants/{slug}/audit-events/types`; pill "Semua" + satu per tipe; reload saat dipilih.
- Tabel: Waktu/Pelaku/Aksi/Modul/Tipe/Objek; sortable (Waktu, Pelaku), searchable, pageSize 20.
- Aksi baris **"Detail"** → modal: grid metadata + JSON `before`/`after` yang di-format rapi (pretty-print).
- **Export** 7 kolom, nama file `audit-trail`.

## 3.10 Notifications

### List (`/notifications`)
- Aksi **"Tandai Dibaca"** (muncul hanya jika ada unread) → `markAllNotifRead` + toast sukses.
- List custom (bukan DataTable): titik unread, judul + pesan, waktu relatif; klik baris → halaman detail.
- **Pagination** 20/halaman: "Sebelumnya/Berikutnya" + "Halaman X / Y".
- Empty state (ikon Inbox). Data dari store (preload layout).

### Detail (`/notifications/[id]`)
- Load via `GET /tenants/{slug}/notifications/{id}`; **auto-mark-read** jika belum dibaca.
- Menampilkan: judul/pesan, waktu absolut, status baca, tautan terkait (jika ada) — "Buka tautan terkait".
- Aksi: **Kembali**, **Hapus** (confirm native) → kembali ke list.

## 3.11 Tutorial

- Kartu hero: statistik tour (N langkah, N halaman, N bab) + tombol **"Mulai Tur dari Awal"**.
- **Daftar langkah per fase** (dari `config/tour.ts`): nomor, judul, badge halaman, badge "menyorot elemen" (jika menarget elemen), deskripsi, tombol **"Mulai dari sini"** → `startTourFrom(index)` + navigasi ke halaman tujuan.
- CTA card di bagian bawah. Murni client-side, tanpa API.

## 3.12 Transactions

- **Metrik**: Total Pemasukan, Total Pengeluaran, Rata-rata Harian, Transaksi Bulan Ini (dihitung client-side).
- Tabel: Tanggal/Deskripsi/Akun (nama dari store)/Tipe/Jumlah (negatif dalam kurung)/Status (badge); sortable, searchable, pageSize 5.
- **Owner-only**: draft → **Edit** (modal), **Post** (`/transactions/{id}/post`), **Hapus**; posted → **Void** (konfirmasi native).
- **Modal buat/edit**: tanggal, deskripsi, akun (income/expense sesuai tipe), akun lawan (asset/cash), tipe, `CurrencyInput` jumlah. Validasi HTML `required`.
- Tanpa export.

## 3.13 Settings

### Organization (`/settings/organization`)
- Kartu profil **read-only**: Nama Tampilan, Nama Legal, NPWP, Telepon, Email, Website, Alamat, Zona Waktu, Currency.
- **Edit Profil modal**: semua field; timezone (WIB/WITA/WIT); currency (hanya IDR); `email`/`url` input type.
- **API**: `GET /tenants/{slug}/organization`, `PATCH .../organization`. Tombol Refresh + Edit. Tanpa gating role.

### Members (`/settings/members`)
- **Owner-gated** (employee: tabel read-only + banner, tanpa tombol).
- **Kartu join code**: tampilkan kode; **Salin** (clipboard → "Tersalin"); **"Perbarui Kode"** (`regenerateJoinCode`); link ke `/auth/join-company`; catatan batasan satu perusahaan per akun.
- Tabel: Nama/Email/Peran/Status (sortable, searchable).
- **Owner**: "+ Undang Anggota" (auto-create user bila email belum terdaftar), **Edit**, **Hapus**. Modal: nama, email, role (`tenant_owner`/`employee`), status.

### Branches (`/settings/branches`)
- **CRUD**: "+ Cabang Baru" / Edit / Hapus (ConfirmDialog). Modal: nama, kode, alamat, status (edit); kolom Pusat (isMain Ya/Tidak).
- Tabel: Nama Cabang/Kode/Alamat/Pusat/Status (sortable, searchable). Tanpa export, tanpa gating role.

### Roles (`/settings/roles`)
- **Read-only**: kartu per role — `tenant_owner` (ikon UserCog) & `employee` (ikon Shield) + deskripsi statis. Tanpa aksi/CRUD/export. Skeleton loading + empty fallback.

### Security (`/settings/security`)
- **MFA (TOTP)** — level akun:
  - Status check → `GET /auth/mfa/status`.
  - Jika **nonaktif**: "Aktifkan MFA" → `POST /auth/mfa/setup` → modal menampilkan **base32 secret** (tombol salin), URI otpauth collapsible, input **6 digit** (auto-advance + paste) → `POST /auth/mfa/enable` → **modal recovery codes** (salin semua, konfirmasi tersimpan).
  - Jika **aktif**: "Nonaktifkan MFA" → konfirmasi 6 digit → `POST /auth/mfa/disable`.
- **Ganti password**: password lama, baru (min 8), konfirmasi; validasi client "konfirmasi tidak sama" dengan error inline; `changePassword`.

### Sidebar (`/settings/sidebar`) — owner-only
- **Guard**: non-owner di-redirect ke `/app/{slug}` (via `$effect`) + kartu fallback "Hanya tenant_owner".
- **Toggle per grup**: header grup dengan hitungan X/Y aktif; per item ikon + label + badge gembok (pinned); switch untuk non-pinned.
- **Bar simpan sticky**: "Aktifkan Semua" / "Nonaktifkan Semua" / **"Simpan Perubahan"** → `PUT /tenants/{slug}/sidebar-settings`; indikator "✓ Tersimpan"; penghitung "N/M menu aktif".
- Banner info: perubahan berlaku real-time untuk semua anggota; item pinned selalu tampil.

### Billing (`/settings/billing`)
- **Read-only**: 3 MetricCard — **Paket** (⚠️ value hardcoded `0` — lihat Lampiran), **Fitur Aktif**, **Status**; kartu paket aktif (nama, planCode, status, periode, daftar fitur); **tabel riwayat langganan** (Paket/Status/Periode/Biaya format IDR/Mulai). Hanya tombol Refresh.

### Integrations (`/settings/integrations`)
- List kartu integrasi: provider/displayName, "Sinkron terakhir", baris error sinkron, status pill; **owner-only toggle Aktifkan/Putuskan** (`updateIntegration`).
- Owner **"+ Tambah Integrasi"** modal: provider + displayName (secret sengaja TIDAK diisi di browser).
- Jika backend kosong → pesan "Backend belum mengembalikan integrasi aktif. Tidak menampilkan daftar integrasi dummy."

---

# 4. Ringkasan Peran (Owner vs Employee)

| Area | tenant_owner | employee |
|---|---|---|
| Semua halaman view | ✅ | ✅ (baca) |
| Dashboard, POS, Reports, Insights, Audit, Notifications, Tutorial | ✅ penuh | ✅ penuh (POS: bisa tambah stok + checkout) |
| Transactions, Journals, Fiscal Years, Reconciliation, PO, Supplier Payments, Invoices | Post / Edit / Hapus / Void / Reverse / Tutup Periode | Read-only (banner) |
| Members, Sidebar Settings | ✅ kelola | Read-only / redirect |
| Integrations | ✅ tambah + toggle | Lihat saja |
| Profile menu | Tanpa "Keluar dari Perusahaan Ini" | "Keluar dari Perusahaan Ini" (tanpa "Gabung Perusahaan" bila sudah 1 tenant) |
| Settings Security / Organization / Billing / Roles / Branches | ✅ | ✅ (security = level akun) |
| Customers, Suppliers, Branches, COA, Organization | CRUD | CRUD juga di UI (tanpa gating UI) |

---

# 5. Lampiran: Temuan Analisis

Temuan berikut hasil analisis statis kode (belum diverifikasi lewat testing interaktif):

| # | Temuan | Lokasi | Keterangan |
|---|---|---|---|
| 1 | Parameter `?plan=premium` & `?plan=platinum` dikirim tapi **tidak dibaca** oleh halaman register | Landing pricing & final CTA → `/auth/register` | Flow "register dengan paket terpilih" tidak terhubung; param mati. |
| 2 | `?onboarding=true` di URL login **tidak dikonsumsi** | Register → `/auth/login?onboarding=true` | Param mati. |
| 3 | Checkbox "Ingat saya" **non-fungsional** | `/auth/login` | Hanya visual, tanpa logika persistensi. |
| 4 | Branch banner "Ganti" hanya **menutup banner** (stub) | `WorkspaceShell.svelte` | Belum ada switcher cabang sungguhan. |
| 5 | MetricCard "Paket" di Billing **hardcoded 0** | `/settings/billing` | Nama paket tampil di kartu bawah, tapi metrik atas selalu 0. |
| 6 | `logout()` **tidak membersihkan** `kepin_tenants` & `kepin_mfa_token` | `stores/auth.ts` | Berpotensi menyisakan state basi. |
| 7 | `lib/api/auth.ts` adalah **kode legacy mati** (endpoint `/dev-auth/*`) | `frontend/src/lib/api/auth.ts` | Tidak dipakai oleh alur auth mana pun. |
| 8 | Halaman tanpa export | Dashboard, Insights, Transactions, Notifications, Tutorial, Fiscal Years, Reconciliation, Roles, Security, Sidebar, Organization, Branches, Members, Billing, Integrations | Export terbatas pada halaman dengan data tabel utama. |
| 9 | Tanpa gating role di UI | Customers, Suppliers, Branches, COA, Organization | CRUD tampak terbuka untuk employee di UI (backend tetap menerapkan otorisasi). |
| 10 | `GET /invoices/{id}/pdf` masih **stub "not_available"** | Backend sales | Fitur PDF invoice belum diimplementasikan. |
| 11 | Header marketing membaca status auth **sekali saat mount** | `MarketingHeader.svelte` | Tidak reaktif terhadap login/logout di tab yang sama. |
| 12 | Halaman admin tanpa UI lengkap | `/admin/users`, `/admin/incidents` | Backend punya create/update, UI hanya list (di luar scope utama dokumen ini). |

---

## Catatan

- Seluruh jalur URL mengikuti pola: `/` (landing), `/auth/*` (autentikasi), `/app/{tenantSlug}/*` (workspace tenant), `/admin/*` (platform admin — di luar cakupan dokumen ini).
- Akun demo yang disediakan seed:
  - `budi@tokomaju.com` / `budi123` — owner `toko-maju`
  - `ani@tokomaju.com` / `ani12345` — employee `toko-maju`
  - `siti@warungsegar.com` / `siti123` — employee `warung-segar`
  - `admin@kepin.io` / `admin123` — superadmin platform
