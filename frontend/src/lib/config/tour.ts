import type { TourConfig } from '$lib/stores/tour';

export const mainTour: TourConfig = {
  name: 'Panduan KePin',
  steps: [
    // ═══════════════════ DASHBOARD ═══════════════════
    {
      page: '',
      title: 'Selamat Datang di KePin!',
      description:
        'KePin adalah aplikasi manajemen keuangan dan operasional untuk bisnis kecil-menengah. Panduan ini akan mengajak Anda mengenal semua fitur utama, langkah demi langkah.',
      side: 'bottom',
    },
    {
      page: '',
      element: '[class*="grid"]',
      title: 'Ringkasan Dashboard',
      description:
        'Dashboard menampilkan metrik ringkas: total penjualan, piutang, beban, kas & bank — dan grafik pendapatan & beban harian.',
      side: 'top',
    },
    {
      page: '',
      element: 'nav, [class*="Sidebar"]',
      title: 'Navigasi Sidebar',
      description:
        'Gunakan menu samping untuk berpindah antar modul: Penjualan, Pembelian, Inventaris, Akuntansi, Laporan, dan Pengaturan. Klik ikon menu di kiri atas untuk menyembunyikan/memperluas sidebar.',
      side: 'right',
    },

    // ═══════════════════ PRODUK ═══════════════════
    {
      page: 'inventory/products',
      title: 'Produk — Daftar Produk',
      description:
        'Halaman ini menampilkan semua produk Anda. Anda bisa mencari, menambah, mengedit, atau menghapus produk. Setiap produk memiliki SKU, nama, kategori, harga jual, harga modal, dan stok.',
    },
    {
      page: 'inventory/products',
      element: 'button:has-text("+ Produk Baru")',
      title: 'Tambah Produk Baru',
      description:
        'Klik tombol "+ Produk Baru" untuk menambahkan produk. Isi SKU, nama, kategori, harga, dan stok minimal. Produk baru langsung tersedia di Point of Sales.',
      side: 'left',
    },
    {
      page: 'inventory/products',
      element: '[class*="DataTable"] table tbody tr:first-child [class*="hover:underline"]:first-child',
      title: 'Edit & Hapus Produk',
      description:
        'Setiap baris produk memiliki tombol Edit (ubah data) dan Hapus. Gunakan fitur ekspor untuk mengunduh daftar produk ke PDF/Excel.',
      side: 'left',
    },

    // ═══════════════════ TRANSAKSI PRODUK ═══════════════════
    {
      page: 'inventory/transactions',
      title: 'Transaksi Produk — Riwayat Penjualan POS',
      description:
        'Semua transaksi penjualan dari Point of Sales tercatat di sini. Lihat nomor checkout, produk yang dibeli, jumlah dibayarkan, total harga, dan kembalian secara lengkap.',
    },
    {
      page: 'inventory/transactions',
      element: '[class*="DataTable"] table tbody tr:first-child button',
      title: 'Detail Transaksi',
      description:
        'Klik tombol "Detail" untuk melihat rincian produk dalam transaksi: nama produk, kuantitas, harga satuan, dan subtotal. Juga ringkasan total, dibayar, dan kembalian.',
      side: 'left',
    },

    // ═══════════════════ PERGERAKAN STOK ═══════════════════
    {
      page: 'inventory/movements',
      title: 'Pergerakan Stok — Riwayat Mutasi',
      description:
        'Halaman ini mencatat setiap perubahan stok: penerimaan barang, pengeluaran, penyesuaian, dan penjualan POS. Setiap baris menunjukkan produk, lokasi, jumlah sebelum/sesudah, dan alasan.',
    },

    // ═══════════════════ POINT OF SALES ═══════════════════
    {
      page: 'pos',
      title: 'Point of Sales — Kasir',
      description:
        'Ini adalah halaman kasir POS. Cari produk berdasarkan nama/SKU/kategori, lalu klik "+ Keranjang" untuk menambahkan ke daftar belanja. Stok terkelola otomatis.',
    },
    {
      page: 'pos',
      element: '.lg\\\\:col-span-2 [class*="grid"] div.card:first-child',
      title: 'Katalog Produk',
      description:
        'Katalog produk dengan stok real-time (hijau = cukup, kuning = kritis, merah = habis). Klik "Stok" untuk menambah/mengurangi stok manual tanpa transaksi penjualan.',
      side: 'top',
    },
    {
      page: 'pos',
      element: '.lg\\\\:sticky [class*="card"]',
      title: 'Keranjang & Pembayaran',
      description:
        'Panel keranjang: atur jumlah item (+ / -), hapus item, lihat total. Masukkan jumlah dibayarkan — kembalian otomatis terhitung real-time. Klik "Bayar & Kurangi Stok" untuk menyelesaikan transaksi.',
      side: 'left',
    },

    // ═══════════════════ INVOICE ═══════════════════
    {
      page: 'sales/invoices',
      title: 'Invoice — Penjualan',
      description:
        'Kelola invoice penjualan di sini. Buat invoice baru, kirim ke pelanggan, catat pembayaran, dan pantau status piutang. Setiap invoice memiliki nomor unik dan jatuh tempo.',
    },
    {
      page: 'sales/invoices',
      element: 'button:has-text("+ Invoice Baru")',
      title: 'Buat Invoice',
      description:
        'Klik "+ Invoice Baru" untuk membuat invoice. Pilih pelanggan, tanggal, item, pajak, dan diskon. Invoice bisa dikirim otomatis ke email pelanggan.',
      side: 'left',
    },

    // ═══════════════════ PELANGGAN ═══════════════════
    {
      page: 'sales/customers',
      title: 'Pelanggan — Manajemen Data',
      description:
        'Daftar pelanggan bisnis Anda. Tambah, edit, atau hapus data pelanggan. Kolom pencarian memudahkan menemukan pelanggan tertentu. Klik "Statement" untuk melihat riwayat transaksi.',
    },

    // ═══════════════════ PURCHASE ORDER ═══════════════════
    {
      page: 'purchasing/orders',
      title: 'Pesanan Pembelian (PO)',
      description:
        'Buat purchase order untuk memesan barang dari supplier. Setiap PO melalui alur: draft → dikirim → diterima (goods receipt). Barang yang diterima otomatis menambah stok.',
    },

    // ═══════════════════ CHART OF ACCOUNTS ═══════════════════
    {
      page: 'accounting/chart-of-accounts',
      title: 'Chart of Accounts',
      description:
        'Daftar akun akuntansi (COA). Terdiri dari Aset, Kewajiban, Ekuitas, Pendapatan, dan Beban. Setiap transaksi dicatat ke akun yang sesuai untuk laporan keuangan yang akurat.',
    },

    // ═══════════════════ JURNAL ═══════════════════
    {
      page: 'accounting/journals',
      title: 'Jurnal Akuntansi',
      description:
        'Draft, posting, dan reversal jurnal akuntansi. Setiap jurnal harus balanced (debit = kredit). Jurnal yang sudah diposting masuk ke buku besar dan memengaruhi saldo akun.',
    },
    {
      page: 'accounting/journals',
      element: 'button:has-text("Jurnal Baru")',
      title: 'Buat Jurnal Baru',
      description:
        'Klik "Jurnal Baru" untuk membuat entri jurnal manual. Pilih akun debit/kredit, deskripsi, dan nominal. Pastikan total debit = total kredit sebelum menyimpan.',
      side: 'left',
    },

    // ═══════════════════ LAPORAN ═══════════════════
    {
      page: 'reports',
      title: 'Laporan Keuangan',
      description:
        'Hasilkan laporan laba rugi, neraca, arus kas, dan aging piutang/hutang. Filter berdasarkan periode, bandingkan dengan periode sebelumnya, dan ekspor ke PDF atau Excel.',
    },

    // ═══════════════════ NOTIFIKASI ═══════════════════
    {
      page: 'notifications',
      title: 'Notifikasi',
      description:
        'Semua pemberitahuan sistem muncul di sini: invoice baru, pembayaran masuk, peringatan stok kritis, dan aktivitas tim. Klik notifikasi untuk melihat detail.',
      navigateTo: 'notifications',
    },

    // ═══════════════════ SETTINGS ═══════════════════
    {
      page: 'settings/organization',
      title: 'Pengaturan Organisasi',
      description:
        'Kelola profil organisasi: nama, sektor, alamat, dan informasi pajak. Hanya pemilik tenant (owner) yang dapat mengubah pengaturan ini.',
    },

    // ═══════════════════ SELESAI ═══════════════════
    {
      page: '',
      title: 'Selesai! 🎉',
      description:
        'Anda telah menyelesaikan tur KePin. Mulai kelola bisnis Anda sekarang! Kapan saja, klik ikon ? di pojok kanan atas untuk memulai tur ulang.',
      side: 'bottom',
    },
  ],
};