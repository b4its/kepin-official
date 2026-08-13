import type { TourConfig, TourStep } from '$lib/stores/tour';

export const mainTour: TourConfig = {
  name: 'Tur KePin',
  phases: [
    { key: 'welcome', label: 'Halaman Awal', description: 'Pengenalan KePin dari halaman utama.' },
    { key: 'auth', label: 'Akun & Perusahaan', description: 'Masuk, daftar, dan siapkan workspace Anda.' },
    { key: 'dashboard', label: 'Dashboard', description: 'Ringkasan kondisi bisnis Anda secara real-time.' },
    { key: 'inventory', label: 'Inventaris & POS', description: 'Produk, stok, pergerakan, dan kasir.' },
    { key: 'sales', label: 'Penjualan', description: 'Invoice dan data pelanggan.' },
    { key: 'purchasing', label: 'Pembelian', description: 'Purchase order, pemasok, dan pembayaran.' },
    { key: 'accounting', label: 'Akuntansi', description: 'Transaksi, jurnal, COA, tahun buku, rekonsiliasi.' },
    { key: 'reports', label: 'Laporan & Insight', description: 'Laporan keuangan, analitik, audit, notifikasi.' },
    { key: 'settings', label: 'Pengaturan', description: 'Organisasi, tim, keamanan, dan billing.' },
    { key: 'finish', label: 'Selesai', description: 'Tur selesai — saatnya mengelola bisnis Anda.' },
  ],
  steps: [
    // ═══════════════════ Halaman Awal (Landing) ═══════════════════
    {
      page: '/',
      phase: 'welcome',
      title: 'Selamat Datang di KePin! 👋',
      description:
        'KePin adalah aplikasi manajemen keuangan dan operasional untuk bisnis kecil-menengah. Tur ini akan memandu Anda langkah demi langkah — dari halaman awal hingga seluruh fitur workspace — sambil menyorot elemen asli di layar.',
      side: 'bottom',
    },
    {
      page: '/',
      phase: 'welcome',
      element: '[data-tour="landing-header"]',
      title: 'Navigasi Halaman Utama',
      description:
        'Di bagian atas terdapat navigasi utama: logo KePin, menu Solusi, Fitur, Keamanan, Cara Kerja, Harga, dan FAQ. Gunakan menu ini untuk menjelajah informasi tentang KePin.',
      side: 'bottom',
    },
    {
      page: '/',
      phase: 'welcome',
      element: '[data-tour="cta-register"]',
      title: 'Mulai Coba Gratis',
      description:
        'Klik tombol "Coba Gratis" untuk mendaftarkan akun baru. Pendaftaran hanya membutuhkan nama, email, dan kata sandi.',
      side: 'left',
    },
    {
      page: '/',
      phase: 'welcome',
      element: '[data-tour="cta-login"]',
      title: 'Masuk ke Akun Anda',
      description:
        'Jika sudah memiliki akun, klik "Masuk" untuk menuju halaman login. Setelah login, Anda akan diarahkan ke workspace perusahaan Anda.',
      side: 'left',
    },

    // ═══════════════════ Akun & Perusahaan ═══════════════════
    {
      page: '/auth/login',
      phase: 'auth',
      element: '[data-tour="auth-form"]',
      title: 'Halaman Masuk (Login)',
      description:
        'Masukkan email dan kata sandi Anda. Centang "Ingat saya" agar sesi tetap aktif, atau gunakan "Lupa password?" untuk reset. Jika MFA aktif, Anda akan diminta kode verifikasi di langkah berikutnya.',
      side: 'top',
    },
    {
      page: '/auth/mfa',
      phase: 'auth',
      title: 'Verifikasi Dua Langkah (MFA)',
      description:
        'Apabila organisasi Anda mengaktifkan MFA, kode 6 digit dari aplikasi autentikator (Google Authenticator, dll.) diperlukan di sini. Ini melindungi akun dari akses tidak sah.',
      side: 'top',
    },
    {
      page: '/auth/register',
      phase: 'auth',
      element: '[data-tour="auth-form"]',
      title: 'Daftar Akun Gratis',
      description:
        'Isi nama lengkap, email, dan kata sandi (min. 8 karakter) untuk membuat akun. Setelah mendaftar, Anda masuk ke halaman onboarding untuk menyiapkan perusahaan.',
      side: 'top',
    },
    {
      page: '/auth/onboarding',
      phase: 'auth',
      title: 'Onboarding — Pilih Langkah Berikutnya',
      description:
        'Halaman ini muncul untuk akun baru. Pilih "Buat Perusahaan Baru" untuk mendirikan perusahaan sendiri, atau "Gabung Perusahaan" untuk masuk ke perusahaan yang sudah ada menggunakan kode undangan.',
    },
    {
      page: '/auth/create-company',
      phase: 'auth',
      element: '[data-tour="auth-form"]',
      title: 'Buat Perusahaan Baru',
      description:
        'Lengkapi profil perusahaan: nama, sektor industri, alamat, mata uang, dan kode pajak (NPWP). Anda otomatis menjadi pemilik (owner) dan workspace langsung dibuat.',
      side: 'top',
    },
    {
      page: '/auth/join-company',
      phase: 'auth',
      element: '[data-tour="auth-form"]',
      title: 'Gabung ke Perusahaan',
      description:
        'Masukkan kode undangan dari pemilik perusahaan untuk bergabung. Setelah diterima, Anda bisa mengakses workspace sesuai peran yang diberikan.',
      side: 'top',
    },

    // ═══════════════════ Dashboard ═══════════════════
    {
      page: '',
      phase: 'dashboard',
      title: 'Dashboard — Pusat Kendali Bisnis Anda',
      description:
        'Selamat datang di workspace Anda! Dashboard menampilkan kondisi bisnis secara real-time: pendapatan, pengeluaran, laba bersih, dan kas & bank dalam periode terpilih.',
    },
    {
      page: '',
      phase: 'dashboard',
      element: '[data-tour="metric-cards"]',
      title: 'Kartu Metrik Utama',
      description:
        'Empat kartu utama: Pendapatan, Pengeluaran, Laba Bersih, dan Kas & Bank. Centang "Bandingkan dengan periode sebelumnya" untuk melihat perbandingan antar periode.',
      side: 'top',
    },
    {
      page: '',
      phase: 'dashboard',
      element: '[data-tour="dashboard-charts"]',
      title: 'Grafik Arus Kas & Komposisi Beban',
      description:
        'Grafik batang menampilkan arus kas harian (pemasukan vs pengeluaran), dan diagram lingkaran menunjukkan komposisi beban berdasarkan akun pengeluaran.',
      side: 'top',
    },
    {
      page: '',
      phase: 'dashboard',
      element: '[data-tour="workspace-sidebar"]',
      title: 'Sidebar Navigasi',
      description:
        'Sidebar memuat seluruh modul: Penjualan, Pembelian, Inventaris, Akuntansi, Laporan & Insight, serta Kontrol. Klik ikon menu di kiri atas untuk menciutkan/memperluasnya.',
      side: 'right',
    },

    // ═══════════════════ Laporan & Insight ═══════════════════
    {
      page: 'insights',
      phase: 'reports',
      title: 'Analitik Bisnis (AI Insight)',
      description:
        'Halaman ini menyajikan insight deterministik dari data transaksi Anda: tren penjualan, produk terlaris, peringatan stok, dan rekomendasi berbasis data.',
    },
    {
      page: 'reports',
      phase: 'reports',
      title: 'Laporan Keuangan',
      description:
        'Hasilkan trial balance, laporan laba rugi, neraca, arus kas, dan aging piutang/hutang. Atur periode, bandingkan dengan periode sebelumnya, lalu ekspor ke PDF atau Excel.',
    },

    // ═══════════════════ Inventaris & POS ═══════════════════
    {
      page: 'inventory/products',
      phase: 'inventory',
      title: 'Produk — Daftar Produk',
      description:
        'Kelola seluruh produk Anda: SKU, nama, kategori, satuan, harga jual, harga modal, stok minimal, dan status. Gunakan kolom pencarian untuk menemukan produk dengan cepat.',
    },
    {
      page: 'inventory/products',
      phase: 'inventory',
      element: '[data-tour="add-product"]',
      title: 'Tambah Produk Baru',
      description:
        'Klik "+ Produk Baru" lalu isi SKU, nama, kategori, harga jual, dan harga modal. Produk langsung tersedia di katalog Point of Sales. Gunakan "Ekspor" untuk mengunduh daftar produk ke PDF/Excel.',
      side: 'left',
    },
    {
      page: 'inventory/products',
      phase: 'inventory',
      element: '[data-tour="products-table"]',
      title: 'Edit, Hapus & Pantau Stok',
      description:
        'Setiap baris produk memiliki tombol Edit dan Hapus. Kolom Stok dan Min. Stok membantu Anda memantau produk kritis (dead stock dan stok menipis).',
      side: 'top',
    },
    {
      page: 'inventory/transactions',
      phase: 'inventory',
      element: '[data-tour="product-transactions-table"]',
      title: 'Transaksi Produk — Riwayat POS',
      description:
        'Seluruh transaksi penjualan dari Point of Sales tercatat di sini: nomor checkout, produk, jumlah dibayar, total, dan kembalian. Klik "Detail" untuk melihat rincian per produk.',
      side: 'top',
    },
    {
      page: 'inventory/movements',
      phase: 'inventory',
      element: '[data-tour="movements-table"]',
      title: 'Pergerakan Stok (Stock Movement)',
      description:
        'Setiap mutasi stok dicatat lengkap: penerimaan barang, pengeluaran, penyesuaian, dan penjualan POS — lengkap dengan jumlah sebelum/sesudah serta alasan.',
      side: 'top',
    },
    {
      page: 'pos',
      phase: 'inventory',
      title: 'Point of Sales — Kasir',
      description:
        'Ini halaman kasir. Cari produk berdasarkan nama/SKU/kategori, lalu klik "+ Keranjang" untuk menambahkan ke transaksi. Stok terpotong otomatis saat pembayaran.',
    },
    {
      page: 'pos',
      phase: 'inventory',
      element: '[data-tour="pos-catalog"]',
      title: 'Katalog Produk Real-time',
      description:
        'Katalog menampilkan stok real-time: hijau = cukup, kuning = kritis, merah = habis. Klik "Stok" untuk menambah/mengurangi stok manual tanpa transaksi penjualan.',
      side: 'top',
    },
    {
      page: 'pos',
      phase: 'inventory',
      element: '[data-tour="pos-cart"]',
      title: 'Keranjang & Pembayaran',
      description:
        'Panel keranjang di kanan: atur jumlah item (+/−), hapus item, dan lihat total. Masukkan jumlah dibayarkan — kembalian dihitung real-time — lalu klik "Bayar & Kurangi Stok".',
      side: 'left',
    },

    // ═══════════════════ Penjualan ═══════════════════
    {
      page: 'sales/invoices',
      phase: 'sales',
      title: 'Invoice Penjualan',
      description:
        'Kelola invoice: buat invoice baru, kirim ke pelanggan, catat pembayaran, dan pantau status piutang. Setiap invoice memiliki nomor unik dan tanggal jatuh tempo.',
    },
    {
      page: 'sales/invoices',
      phase: 'sales',
      element: '[data-tour="add-invoice"]',
      title: 'Buat Invoice Baru',
      description:
        'Klik "+ Invoice Baru", pilih pelanggan, tanggal, item, pajak, dan diskon. Invoice bisa dikirim otomatis ke email pelanggan dan dicatat ke akun piutang.',
      side: 'left',
    },
    {
      page: 'sales/customers',
      phase: 'sales',
      element: '[data-tour="customers-table"]',
      title: 'Data Pelanggan',
      description:
        'Daftar pelanggan bisnis Anda. Tambah, edit, atau hapus data pelanggan, serta lihat "Statement" untuk riwayat transaksi dan saldo piutang masing-masing pelanggan.',
      side: 'top',
    },

    // ═══════════════════ Pembelian ═══════════════════
    {
      page: 'purchasing/orders',
      phase: 'purchasing',
      element: '[data-tour="orders-table"]',
      title: 'Pesanan Pembelian (Purchase Order)',
      description:
        'Buat PO untuk memesan barang dari pemasok. Alurnya: draft → dikirim → diterima (goods receipt). Barang yang diterima otomatis menambah stok dan membentuk hutang usaha.',
      side: 'top',
    },
    {
      page: 'purchasing/suppliers',
      phase: 'purchasing',
      element: '[data-tour="suppliers-table"]',
      title: 'Data Pemasok',
      description:
        'Kelola data pemasok: nama, kontak, alamat, dan syarat pembayaran. Data pemasok dipakai saat membuat PO dan pembayaran.',
      side: 'top',
    },
    {
      page: 'purchasing/payments',
      phase: 'purchasing',
      element: '[data-tour="payments-table"]',
      title: 'Pembayaran Pemasok',
      description:
        'Catat pembayaran atas hutang ke pemasok: pilih pemasok, jumlah, akun kas/bank, dan tanggal bayar. Pembayaran otomatis mengurangi saldo hutang usaha.',
      side: 'top',
    },

    // ═══════════════════ Akuntansi ═══════════════════
    {
      page: 'transactions',
      phase: 'accounting',
      element: '[data-tour="transactions-table"]',
      title: 'Transaksi Keuangan',
      description:
        'Katalog seluruh transaksi keuangan: penjualan, pembelian, jurnal, dan penyesuaian — dengan status (draft/posted) dan jumlah masing-masing. Ini sumber data laporan keuangan.',
      side: 'top',
    },
    {
      page: 'accounting/journals',
      phase: 'accounting',
      element: '[data-tour="journals-table"]',
      title: 'Jurnal Akuntansi',
      description:
        'Buat draft jurnal, posting, atau reversal. Setiap jurnal harus balanced (debit = kredit). Jurnal yang ter-posting masuk buku besar dan memengaruhi saldo akun.',
      side: 'top',
    },
    {
      page: 'accounting/journals',
      phase: 'accounting',
      element: '[data-tour="add-journal"]',
      title: 'Buat Jurnal Baru',
      description:
        'Klik "Jurnal Baru" untuk entri manual: pilih akun debit dan kredit, deskripsi, serta nominal. Sistem menolak penyimpanan bila total debit ≠ total kredit.',
      side: 'left',
    },
    {
      page: 'accounting/chart-of-accounts',
      phase: 'accounting',
      element: '[data-tour="coa-table"]',
      title: 'Chart of Accounts (COA)',
      description:
        'Daftar akun akuntansi: Aset, Kewajiban, Ekuitas, Pendapatan, dan Beban. Setiap transaksi dicatat ke akun yang tepat agar laporan keuangan akurat.',
      side: 'top',
    },
    {
      page: 'accounting/fiscal-years',
      phase: 'accounting',
      element: '[data-tour="fiscal-years-table"]',
      title: 'Tahun Buku & Periode',
      description:
        'Kelola tahun buku dan periode akuntansi. Periode dibuka/ditutup sesuai alur pelaporan, dan penutupan tahun buku menghasilkan jurnal penutup otomatis.',
      side: 'top',
    },
    {
      page: 'accounting/reconciliation',
      phase: 'accounting',
      element: '[data-tour="reconciliation-table"]',
      title: 'Rekonsiliasi Bank',
      description:
        'Impor transaksi bank, cocokkan dengan transaksi di sistem, dan tandai item yang sudah direkonsiliasi untuk memastikan kas & bank akurat.',
      side: 'top',
    },

    // ═══════════════════ Laporan & Kontrol ═══════════════════
    {
      page: 'notifications',
      phase: 'reports',
      title: 'Notifikasi',
      description:
        'Semua pemberitahuan sistem muncul di sini: invoice baru, pembayaran masuk, peringatan stok kritis, dan aktivitas tim. Klik notifikasi untuk melihat detailnya.',
    },
    {
      page: 'audit',
      phase: 'reports',
      element: '[data-tour="audit-table"]',
      title: 'Audit Trail',
      description:
        'Riwayat lengkap setiap perubahan data: siapa, kapan, aksi apa, dan modul mana. Berguna untuk kepatuhan dan menelusuri kesalahan pencatatan.',
      side: 'top',
    },

    // ═══════════════════ Pengaturan ═══════════════════
    {
      page: 'settings/organization',
      phase: 'settings',
      title: 'Pengaturan Organisasi',
      description:
        'Kelola profil organisasi: nama, sektor, alamat, dan informasi pajak. Hanya pemilik tenant (owner) yang dapat mengubah pengaturan ini.',
    },
    {
      page: 'settings/members',
      phase: 'settings',
      element: '[data-tour="members-table"]',
      title: 'Anggota Tim',
      description:
        'Undang anggota tim ke workspace, atur peran mereka, dan kelola status keanggotaan. Setiap anggota mengikuti izin sesuai perannya.',
      side: 'top',
    },
    {
      page: 'settings/roles',
      phase: 'settings',
      element: '[data-tour="roles-list"]',
      title: 'Peran & Izin (Role)',
      description:
        'Lihat peran aktif: pemilik, admin, dan karyawan — beserta izin yang dimilikinya (membaca/menulis akuntansi, posting jurnal, dll.).',
      side: 'top',
    },
    {
      page: 'settings/branches',
      phase: 'settings',
      element: '[data-tour="branches-table"]',
      title: 'Cabang Bisnis',
      description:
        'Kelola cabang atau lokasi bisnis Anda. Setiap cabang dapat memisahkan data inventaris dan transaksi.',
      side: 'top',
    },
    {
      page: 'settings/security',
      phase: 'settings',
      element: '[data-tour="security-settings"]',
      title: 'Keamanan Akun',
      description:
        'Aktifkan verifikasi dua langkah (MFA) dengan aplikasi autentikator, ubah kata sandi, dan pantau sesi login untuk melindungi akun Anda.',
      side: 'top',
    },
    {
      page: 'settings/billing',
      phase: 'settings',
      element: '[data-tour="billing-table"]',
      title: 'Billing & Langganan',
      description:
        'Pantau paket langganan, status pembayaran, dan riwayat tagihan workspace Anda.',
      side: 'top',
    },
    {
      page: 'settings/integrations',
      phase: 'settings',
      element: '[data-tour="integrations-list"]',
      title: 'Integrasi',
      description:
        'Lihat status integrasi dengan layanan eksternal (email, SMS, penyimpanan, dll.) yang terhubung ke workspace.',
      side: 'top',
    },
    {
      page: 'settings/sidebar',
      phase: 'settings',
      element: '[data-tour="sidebar-settings"]',
      title: 'Kustomisasi Sidebar',
      description:
        'Sebagai pemilik, Anda dapat menyembunyikan/menampilkan menu tertentu di sidebar untuk menyederhanakan tampilan bagi tim. Item yang disematkan (pinned) selalu tampil.',
      side: 'top',
    },

    // ═══════════════════ Selesai ═══════════════════
    {
      page: '',
      phase: 'finish',
      title: 'Tur Selesai — Selamat! 🎉',
      description:
        'Anda telah menyelesaikan seluruh tur KePin dari awal hingga akhir. Mulai kelola bisnis Anda sekarang! Kapan saja, buka halaman Tutorial (menu Bantuan di sidebar atau ikon ? di pojok kanan atas) untuk mengulang tur dari langkah mana pun.',
      side: 'bottom',
    },
  ],
};

/** Label halaman yang ramah-tampil untuk halaman tutorial. */
export const tourPageLabels: Record<string, string> = {
  '/': 'Halaman Utama',
  '/auth/login': 'Login',
  '/auth/mfa': 'Verifikasi MFA',
  '/auth/register': 'Daftar Akun',
  '/auth/onboarding': 'Onboarding',
  '/auth/create-company': 'Buat Perusahaan',
  '/auth/join-company': 'Gabung Perusahaan',
  '': 'Dashboard',
  'insights': 'Analitik Bisnis',
  'reports': 'Laporan Keuangan',
  'inventory/products': 'Produk',
  'inventory/transactions': 'Transaksi Produk',
  'inventory/movements': 'Pergerakan Stok',
  'pos': 'Point of Sales',
  'sales/invoices': 'Invoice',
  'sales/customers': 'Pelanggan',
  'purchasing/orders': 'Pesanan Pembelian',
  'purchasing/payments': 'Pembayaran Pemasok',
  'purchasing/suppliers': 'Pemasok',
  'transactions': 'Transaksi Keuangan',
  'accounting/journals': 'Jurnal',
  'accounting/chart-of-accounts': 'Chart of Accounts',
  'accounting/fiscal-years': 'Tahun Buku',
  'accounting/reconciliation': 'Rekonsiliasi Bank',
  'notifications': 'Notifikasi',
  'audit': 'Audit Trail',
  'settings/organization': 'Organisasi',
  'settings/members': 'Anggota Tim',
  'settings/roles': 'Peran & Izin',
  'settings/branches': 'Cabang',
  'settings/security': 'Keamanan Akun',
  'settings/billing': 'Billing',
  'settings/integrations': 'Integrasi',
  'settings/sidebar': 'Kustomisasi Sidebar',
};

/** Kelompokkan langkah berdasarkan fase, tetap berurutan. */
export function groupStepsByPhase(config: TourConfig) {
  const groups = new Map<string, TourStep[]>();
  for (const phase of config.phases) groups.set(phase.key, []);
  for (const step of config.steps) {
    const list = groups.get(step.phase);
    if (list) list.push(step);
  }
  return groups;
}
