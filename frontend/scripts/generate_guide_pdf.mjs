import { chromium } from '@playwright/test';
import fs from 'fs';
import path from 'path';
import { execSync } from 'child_process';

const ROOT_DOCS = path.resolve(import.meta.dirname, '../../documentation/dokumen');
const IMG_DIR = path.join(ROOT_DOCS, 'images');
const OUT_PDF = path.join(ROOT_DOCS, 'Buku_Panduan_Pengguna_KePin.pdf');
const OUT_HTML = path.join(ROOT_DOCS, 'scratch_guide.html');
const OUT_DOCX = path.join(ROOT_DOCS, 'Buku_Panduan_Pengguna_KePin.docx');

function getBase64Image(filename) {
  const filePath = path.join(IMG_DIR, filename);
  if (!fs.existsSync(filePath)) {
    console.warn(`[WARN] Image not found: ${filePath}`);
    return '';
  }
  const buffer = fs.readFileSync(filePath);
  return `data:image/png;base64,${buffer.toString('base64')}`;
}

const html = `<!DOCTYPE html>
<html lang="id">
<head>
<meta charset="UTF-8">
<title>Buku Panduan Pengguna Resmi KePin</title>
<style>
  @page {
    size: A4 portrait;
    margin: 18mm 15mm 20mm 15mm;
  }

  * {
    box-sizing: border-box;
    margin: 0;
    padding: 0;
  }

  body {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
    color: #1e293b;
    background-color: #ffffff;
    line-height: 1.6;
    font-size: 10.5pt;
  }

  /* Cover Page */
  .cover-page {
    page-break-after: always;
    height: 100%;
    min-height: 250mm;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    padding: 20mm 10mm 10mm 10mm;
    border: 3px solid #0f172a;
    border-radius: 8px;
    background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
    position: relative;
  }

  .cover-header {
    border-bottom: 2px solid #059669;
    padding-bottom: 15px;
  }

  .cover-badge {
    display: inline-block;
    background-color: #059669;
    color: #ffffff;
    font-weight: 700;
    font-size: 10pt;
    padding: 6px 14px;
    border-radius: 20px;
    text-transform: uppercase;
    letter-spacing: 1px;
    margin-bottom: 15px;
  }

  .cover-title {
    font-size: 28pt;
    font-weight: 800;
    color: #0f172a;
    line-height: 1.2;
    margin-bottom: 10px;
  }

  .cover-subtitle {
    font-size: 14pt;
    color: #475569;
    font-weight: 500;
    line-height: 1.4;
  }

  .cover-hero-img {
    margin: 25px 0;
    text-align: center;
  }

  .cover-hero-img img {
    max-width: 90%;
    border-radius: 8px;
    box-shadow: 0 10px 25px rgba(0,0,0,0.12);
    border: 1px solid #cbd5e1;
  }

  .cover-meta-table {
    width: 100%;
    border-collapse: collapse;
    margin-top: 15px;
    font-size: 9.5pt;
  }

  .cover-meta-table td {
    padding: 8px 12px;
    border: 1px solid #e2e8f0;
  }

  .cover-meta-table td.label {
    background-color: #f1f5f9;
    font-weight: 700;
    width: 30%;
    color: #334155;
  }

  .cover-footer {
    border-top: 1px solid #cbd5e1;
    padding-top: 12px;
    font-size: 8.5pt;
    color: #64748b;
    text-align: center;
  }

  /* Chapter formatting */
  .chapter-break {
    page-break-before: always;
  }

  h1.chapter-title {
    font-size: 18pt;
    color: #0f172a;
    border-bottom: 2.5px solid #059669;
    padding-bottom: 8px;
    margin-top: 10px;
    margin-bottom: 16px;
    text-transform: uppercase;
    letter-spacing: 0.5px;
  }

  h2.section-title {
    font-size: 13pt;
    color: #1e3a8a;
    margin-top: 18px;
    margin-bottom: 10px;
    border-left: 4px solid #3b82f6;
    padding-left: 10px;
  }

  h3 {
    font-size: 11pt;
    color: #334155;
    margin-top: 12px;
    margin-bottom: 6px;
  }

  p {
    margin-bottom: 10px;
    text-align: justify;
  }

  ul, ol {
    margin-left: 20px;
    margin-bottom: 12px;
  }

  li {
    margin-bottom: 4px;
  }

  /* Screenshot Card styling */
  .screenshot-card {
    margin: 16px 0 20px 0;
    padding: 10px;
    background-color: #f8fafc;
    border: 1px solid #e2e8f0;
    border-radius: 8px;
    text-align: center;
    page-break-inside: avoid;
  }

  .screenshot-card img {
    max-width: 100%;
    height: auto;
    border-radius: 6px;
    border: 1px solid #cbd5e1;
    box-shadow: 0 4px 10px rgba(0,0,0,0.06);
  }

  .screenshot-caption {
    margin-top: 8px;
    font-size: 9pt;
    font-style: italic;
    color: #475569;
    font-weight: 500;
  }

  /* Callout Boxes */
  .callout-box {
    margin: 14px 0;
    padding: 12px 16px;
    border-radius: 6px;
    font-size: 9.5pt;
    page-break-inside: avoid;
  }

  .callout-info {
    background-color: #eff6ff;
    border-left: 4px solid #3b82f6;
    color: #1e40af;
  }

  .callout-success {
    background-color: #ecfdf5;
    border-left: 4px solid #10b981;
    color: #065f46;
  }

  .callout-warning {
    background-color: #fffbeb;
    border-left: 4px solid #f59e0b;
    color: #92400e;
  }

  .callout-box strong {
    display: block;
    margin-bottom: 4px;
    font-size: 10pt;
  }

  /* Tables */
  table.data-table {
    width: 100%;
    border-collapse: collapse;
    margin: 14px 0;
    font-size: 9pt;
    page-break-inside: avoid;
  }

  table.data-table th, table.data-table td {
    padding: 8px 10px;
    border: 1px solid #cbd5e1;
    text-align: left;
  }

  table.data-table th {
    background-color: #0f172a;
    color: #ffffff;
    font-weight: 600;
  }

  table.data-table tr:nth-child(even) {
    background-color: #f8fafc;
  }

  /* Code & tags */
  code {
    font-family: "SFMono-Regular", Consolas, "Liberation Mono", Menlo, Courier, monospace;
    background-color: #f1f5f9;
    color: #0f172a;
    padding: 2px 5px;
    border-radius: 4px;
    font-size: 8.5pt;
    border: 1px solid #e2e8f0;
  }

  .toc-container {
    page-break-after: always;
    padding: 10px 0;
  }

  .toc-item {
    display: flex;
    justify-content: space-between;
    padding: 5px 0;
    border-bottom: 1px dotted #cbd5e1;
    font-size: 9.5pt;
  }

  .toc-title {
    font-weight: 600;
    color: #0f172a;
  }
</style>
</head>
<body>

<!-- ================= COVER PAGE ================= -->
<div class="cover-page">
  <div class="cover-header">
    <div class="cover-badge">BUKU PANDUAN PENGGUNA RESMI</div>
    <div class="cover-title">KePin — Keuangan Pintar</div>
    <div class="cover-subtitle">Sistem ERP & SaaS Terpadu untuk Manajemen Keuangan, Kasir Digital (POS), Inventori, dan Operasional Bisnis UMKM</div>
  </div>

  <div class="cover-hero-img">
    <img src="${getBase64Image('08_workspace_dashboard.png')}" alt="Dashboard KePin Preview">
  </div>

  <div>
    <table class="cover-meta-table">
      <tr>
        <td class="label">Versi Dokumen</td>
        <td>v1.0.0 (Release Oktober 2026)</td>
      </tr>
      <tr>
        <td class="label">Target Pengguna</td>
        <td>Pemilik Usaha (Owner), Kasir/Staf Toko, Manajer Keuangan, Admin Platform</td>
      </tr>
      <tr>
        <td class="label">Domain Aplikasi</td>
        <td><code>https://kepin.oryphem.com</code> &amp; <code>http://72.61.213.112:3001</code></td>
      </tr>
      <tr>
        <td class="label">Dokumentasi</td>
        <td>Disimpan resmi pada <code>documentation/dokumen/</code></td>
      </tr>
    </table>
  </div>

  <div class="cover-footer">
    © 2026 KePin (Keuangan Pintar). Hak Cipta Dilindungi Undang-Undang.<br>
    Dokumen ini memuat panduan komprehensif seluruh modul dan fitur aplikasi beserta bukti visual antarmuka resmi.
  </div>
</div>

<!-- ================= DAFTAR ISI ================= -->
<div class="toc-container">
  <h1 class="chapter-title">DAFTAR ISI PANDUAN</h1>
  <div class="toc-item"><span class="toc-title">BAB 1: PENDAHULUAN & PROFIL APLIKASI</span><span>Hal. 3</span></div>
  <div class="toc-item"><span class="toc-title">BAB 2: HALAMAN PUBLIK & AUTENTIKASI PENGGUNA</span><span>Hal. 5</span></div>
  <div class="toc-item"><span class="toc-title">BAB 3: WORKSPACE PERUSAHAAN (TENANT DASHBOARD)</span><span>Hal. 9</span></div>
  <div class="toc-item"><span class="toc-title">BAB 4: MESIN KASIR DIGITAL (POINT OF SALE / POS)</span><span>Hal. 11</span></div>
  <div class="toc-item"><span class="toc-title">BAB 5: MODUL PENJUALAN (SALES MANAGEMENT)</span><span>Hal. 13</span></div>
  <div class="toc-item"><span class="toc-title">BAB 6: MODUL PEMBELIAN & PENGADAAN (PURCHASING)</span><span>Hal. 15</span></div>
  <div class="toc-item"><span class="toc-title">BAB 7: MODUL INVENTORI & MANAJEMEN GUDANG</span><span>Hal. 17</span></div>
  <div class="toc-item"><span class="toc-title">BAB 8: MODUL AKUNTANSI & PEMBUKUAN KEUANGAN</span><span>Hal. 19</span></div>
  <div class="toc-item"><span class="toc-title">BAB 9: MODUL LAPORAN KEUANGAN & EKSEKUTIF</span><span>Hal. 22</span></div>
  <div class="toc-item"><span class="toc-title">BAB 10: WAWASAN BISNIS OTOMATIS (AI INSIGHTS) & AUDIT KEAMANAN</span><span>Hal. 25</span></div>
  <div class="toc-item"><span class="toc-title">BAB 11: PENGATURAN PERUSAHAAN & KUSTOMISASI WORKSPACE</span><span>Hal. 27</span></div>
  <div class="toc-item"><span class="toc-title">BAB 12: STUDI KASUS OPERASIONAL & PERBANDINGAN PERAN (RBAC)</span><span>Hal. 33</span></div>
  <div class="toc-item"><span class="toc-title">BAB 13: PORTAL ADMINISTRATOR PLATFORM (SUPERADMIN)</span><span>Hal. 35</span></div>
  <div class="toc-item"><span class="toc-title">BAB 14: PANDUAN PEMECAHAN MASALAH, FAQ, & GLOSARIUM</span><span>Hal. 40</span></div>
</div>

<!-- ================= BAB 1 ================= -->
<div class="chapter-break">
  <h1 class="chapter-title">BAB 1: PENDAHULUAN & PROFIL APLIKASI</h1>
  
  <h2 class="section-title">1.1 Mengenal KePin — Solusi Pembukuan Terpadu UMKM</h2>
  <p>Usaha Mikro, Kecil, dan Menengah (UMKM) memegang peranan krusial dalam perekonomian nasional, namun kerap terkendala oleh sistem pembukuan manual yang terpecah-pecah. Seringkali kasir mencatat penjualan di buku nota, manajer inventori memeriksa stok fisik dengan menghitung manual, dan pemilik usaha tidak mengetahui secara pasti posisi laba atau rugi bersih perusahaannya.</p>
  
  <p><strong>KePin (Keuangan Pintar)</strong> hadir sebagai platform Enterprise Resource Planning (ERP) multi-tenant modern yang mentransformasikan pembukuan tradisional menjadi sistem digital otomatis semua-dalam-satu (all-in-one). Sekali transaksi terjadi di kasir, stok terpotong seketika, jurnal akuntansi debit-kredit tercatat secara otomatis, dan neraca keuangan langsung diperbarui tanpa intervensi manual akuntan.</p>

  <div class="callout-box callout-success">
    <strong>🎯 Keunggulan Kunci KePin:</strong>
    1. <strong>Otomatisasi Penuh:</strong> POS kasir langsung terhubung ke jurnal umum, HPP, persediaan barang, dan laba rugi.<br>
    2. <strong>Mesin Modal Awal:</strong> Inisialisasi modal usaha secara kanonik yang menjaga neraca keuangan selalu seimbang.<br>
    3. <strong>Isolasi Multi-Tenant:</strong> Setiap badan usaha memiliki ruang kerja mandiri yang terisolasi aman.<br>
    4. <strong>Fleksibilitas Akses:</strong> Dapat diakses dari komputer kasir, tablet Android/iPad, maupun peramban smartphone.
  </div>

  <h2 class="section-title">1.2 Matriks Hak Akses &amp; Pembagian Peran Pengguna (RBAC)</h2>
  <p>KePin menerapkan sistem keamanan terintegrasi berbasis peran (<em>Role-Based Access Control</em> / RBAC) untuk memastikan pemisahan kewenangan kerja (<em>segregation of duties</em>), menjaga kerahasiaan data finansial strategis, serta mencegah penyalahgunaan data operasional perusahaan:</p>

  <table class="data-table">
    <thead>
      <tr>
        <th style="width: 22%;">Tingkatan Peran</th>
        <th style="width: 28%;">Fungsi &amp; Tanggung Jawab</th>
        <th style="width: 30%;">Modul yang Dapat Diakses</th>
        <th style="width: 20%;">Batasan Akses</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td><strong>Pemilik Usaha (Owner)</strong></td>
        <td>Pengendali tertinggi dan penanggung jawab penuh badan usaha tenant.</td>
        <td>Akses penuh (<em>Full Control</em>): POS Kasir, Penjualan, Pembelian, Inventori, Akuntansi &amp; Jurnal Umum, Laporan Keuangan, Modal Awal, Anggota Tim, Cabang, dan Billing Langganan.</td>
        <td>Tidak ada pembatasan dalam lingkup tenant terkait.</td>
      </tr>
      <tr>
        <td><strong>Manajer Keuangan (Finance)</strong></td>
        <td>Pengelola pembukuan, rekonsiliasi arus kas, penagihan piutang, dan pelaporan perpajakan.</td>
        <td>Faktur Penjualan, Tagihan &amp; PO Pembelian, Inventori, Bagan Akun (CoA), Jurnal Umum, Rekonsiliasi Bank, dan Laporan Finansial.</td>
        <td>Dibatasi dari mutasi kepemilikan tenant, paket langganan SaaS, dan perubahan hak akses tim.</td>
      </tr>
      <tr>
        <td><strong>Karyawan / Kasir (Employee)</strong></td>
        <td>Pelaksana operasional pelayanan transaksi jual-beli langsung di gerai/toko.</td>
        <td>Terminal Kasir (POS), Pencarian Katalog &amp; Cek Stok Produk, serta Riwayat Transaksi Penjualan shift berjalan.</td>
        <td>Tertutup secara ketat dari modul Akuntansi, Jurnal Umum, Laba Rugi, Pengaturan Modal Awal, dan Pengaturan Organisasi.</td>
      </tr>
      <tr>
        <td><strong>Administrator Platform (Superadmin)</strong></td>
        <td>Pengelola operasional sistem cloud global KePin (multi-tenant infrastructure).</td>
        <td>Portal Admin Platform (<code>/admin</code>), Monitoring Tenant Global, Log Jejak Audit Keamanan, Manajemen Insiden, dan Pengaturan Paket Layanan.</td>
        <td>Tidak mengintervensi atau mengubah data transaksi pembukuan privat milik masing-masing tenant.</td>
      </tr>
    </tbody>
  </table>
</div>

<!-- ================= BAB 2 ================= -->
<div class="chapter-break">
  <h1 class="chapter-title">BAB 2: HALAMAN PUBLIK & AUTENTIKASI PENGGUNA</h1>

  <h2 class="section-title">2.1 Menjelajahi Landing Page Resmi</h2>
  <p>Halaman depan (Landing Page) memperkenalkan arsitektur KePin, solusi masalah UMKM, transparansi harga, dan gerbang pendaftaran.</p>

  <div class="screenshot-card">
    <img src="${getBase64Image('01_landing_hero.png')}" alt="Landing Page Hero">
    <div class="screenshot-caption">Gambar 2.1: Header Sticky, Value Proposition Hero, dan Tombol Navigasi Landing Page</div>
  </div>

  <p>Pada bagian Solusi dan Fitur, dijelaskan alur kerja berantai yang mengubah kekacauan nota kertas menjadi pencatatan digital rapi.</p>

  <div class="screenshot-card">
    <img src="${getBase64Image('02_landing_features.png')}" alt="Landing Page Features">
    <div class="screenshot-caption">Gambar 2.2: Rincian Fitur Unggulan &amp; Solusi Terintegrasi KePin</div>
  </div>

  <p>Bagian Harga dan FAQ menyajikan pilihan paket langganan (Starter, Pro, Platinum) yang fleksibel sesuai skala bisnis pengguna.</p>

  <div class="screenshot-card">
    <img src="${getBase64Image('03_landing_pricing.png')}" alt="Landing Page Pricing">
    <div class="screenshot-caption">Gambar 2.3: Matriks Harga Berlangganan &amp; Pusat Pertanyaan yang Sering Diajukan (FAQ)</div>
  </div>

  <h2 class="section-title">2.2 Alur Masuk Sistem (Login) &amp; Pendaftaran</h2>
  <p>Sistem autentikasi KePin dirancang aman dan intuitif dengan fitur pengalihan berbasis peran (Role-Aware Redirect).</p>

  <div class="screenshot-card">
    <img src="${getBase64Image('04_auth_login.png')}" alt="Login Form">
    <div class="screenshot-caption">Gambar 2.4: Formulir Masuk Sistem (Login) KePin</div>
  </div>

  <div class="screenshot-card">
    <img src="${getBase64Image('05_auth_register.png')}" alt="Register Form">
    <div class="screenshot-caption">Gambar 2.5: Formulir Registrasi Akun Pengguna Baru</div>
  </div>

  <h2 class="section-title">2.3 Pembuatan Perusahaan Baru &amp; Bergabung via Join Code</h2>
  <p>Setelah mendaftar, pemilik bisnis dapat mendirikan perusahaannya sendiri atau staf dapat bergabung menggunakan 16-karakter kode undangan (Join Code) resmi.</p>

  <div class="screenshot-card">
    <img src="${getBase64Image('06_auth_create_company.png')}" alt="Create Company">
    <div class="screenshot-caption">Gambar 2.6: Formulir Pendaftaran Badan Usaha / Perusahaan Baru (Create Tenant)</div>
  </div>

  <div class="screenshot-card">
    <img src="${getBase64Image('07_auth_join_company.png')}" alt="Join Company">
    <div class="screenshot-caption">Gambar 2.7: Formulir Penggabungan Karyawan Melalui Join Code Resmi</div>
  </div>
</div>

<!-- ================= BAB 3 ================= -->
<div class="chapter-break">
  <h1 class="chapter-title">BAB 3: WORKSPACE PERUSAHAAN (TENANT DASHBOARD)</h1>

  <h2 class="section-title">3.1 Antarmuka &amp; Indikator Kinerja Utama (KPI Metrics)</h2>
  <p>Dashboard utama merupakan pusat kendali pemilik bisnis (Owner). Di sini disajikan rangkuman kondisi finansial secara aktual tanpa perlu membuka laporan berlapis-lapis.</p>

  <div class="screenshot-card">
    <img src="${getBase64Image('08_workspace_dashboard.png')}" alt="Workspace Dashboard">
    <div class="screenshot-caption">Gambar 3.1: Dashboard Ruang Kerja Tenant Toko Maju Jaya (Budi Santoso)</div>
  </div>

  <div class="callout-box callout-info">
    <strong>📊 Komponen Penting Dashboard:</strong>
    <ul>
      <li><strong>Total Pendapatan:</strong> Akumulasi nilai bersih transaksi penjualan tunai dan faktur lunas pada rentang waktu terpilih.</li>
      <li><strong>Laba Kotor (Gross Profit):</strong> Total pendapatan dikurangi beban pokok pembelian barang dagang yang terjual.</li>
      <li><strong>Pengeluaran Operasional:</strong> Biaya operasional toko yang telah dibayarkan (sewa, listrik, utilitas, gaji).</li>
      <li><strong>Saldo Kas Tunai &amp; Rekening Bank:</strong> Posisi likuiditas uang nyata yang dapat segera digunakan untuk operasional.</li>
      <li><strong>Kartu Penuaan Piutang &amp; Utang:</strong> Peringatan visual mengenai tagihan yang mendekati atau telah melampaui tanggal jatuh tempo.</li>
    </ul>
  </div>
</div>

<!-- ================= BAB 4 ================= -->
<div class="chapter-break">
  <h1 class="chapter-title">BAB 4: MESIN KASIR DIGITAL (POINT OF SALE / POS)</h1>

  <h2 class="section-title">4.1 Antarmuka Kasir &amp; Keranjang Belanja</h2>
  <p>Modul kasir KePin didesain untuk transaksi cepat di meja kasir. Mendukung layar sentuh, pembaca barcode fisik, serta pemilihan kategori produk secara instan.</p>

  <div class="screenshot-card">
    <img src="${getBase64Image('09_pos_cashier.png')}" alt="POS Cashier">
    <div class="screenshot-caption">Gambar 4.1: Antarmuka Mesin Kasir Digital POS Toko Maju Jaya</div>
  </div>

  <h2 class="section-title">4.2 Panduan Operasional Kasir Step-by-Step</h2>
  <ol>
    <li><strong>Memilih Produk:</strong> Klik pada kartu produk atau tembak barcode kemasan menggunakan scanner. Produk otomatis bertambah ke keranjang belanja di sisi kanan.</li>
    <li><strong>Menyesuaikan Kuantitas:</strong> Klik tombol <code>+</code> atau <code>-</code> atau ketikkan angka kuantitas langsung pada item di keranjang.</li>
    <li><strong>Memberi Diskon:</strong> Masukkan diskon jika ada program promosi atau potongan harga nota.</li>
    <li><strong>Memilih Metode Pembayaran:</strong>
      <ul>
        <li><strong>Tunai:</strong> Masukkan jumlah uang tunai yang diserahkan konsumen. Sistem otomatis mengkalkulasi uang kembalian secara presisi.</li>
        <li><strong>QRIS / Transfer Bank:</strong> Konfirmasi pembayaran non-tunai langsung saat uang masuk ke mutasi bank.</li>
      </ul>
    </li>
    <li><strong>Selesaikan Transaksi:</strong> Klik tombol <strong>Bayar &amp; Cetak Struk</strong>. Transaksi otomatis membukukan kas masuk, memotong stok barang di gudang, dan memicu dialog cetak struk nota kasir termal (58mm/80mm).</li>
  </ol>
</div>

<!-- ================= BAB 5 ================= -->
<div class="chapter-break">
  <h1 class="chapter-title">BAB 5: MODUL PENJUALAN (SALES MANAGEMENT)</h1>

  <h2 class="section-title">5.1 Pengelolaan Faktur Penjualan (Invoicing)</h2>
  <p>Untuk transaksi penjualan grosir, pasokan ke warung mitra, atau penjualan bertempo (kredit), gunakan modul Faktur Penjualan.</p>

  <div class="screenshot-card">
    <img src="${getBase64Image('10_sales_invoices.png')}" alt="Sales Invoices">
    <div class="screenshot-caption">Gambar 5.1: Daftar Faktur Penjualan (Invoicing) &amp; Status Pelunasan Tagihan</div>
  </div>

  <h2 class="section-title">5.2 Manajemen Basis Data Pelanggan (CRM)</h2>
  <p>Modul direktori pelanggan menyimpan identitas pelanggan, nomor WhatsApp untuk penagihan, alamat pengiriman, dan riwayat akumulasi belanja.</p>

  <div class="screenshot-card">
    <img src="${getBase64Image('11_sales_customers.png')}" alt="Sales Customers">
    <div class="screenshot-caption">Gambar 5.2: Direktori Pelanggan &amp; Batas Piutang Toko Maju Jaya</div>
  </div>
</div>

<!-- ================= BAB 6 ================= -->
<div class="chapter-break">
  <h1 class="chapter-title">BAB 6: MODUL PEMBELIAN & PENGADAAN (PURCHASING)</h1>

  <h2 class="section-title">6.1 Pesanan Pembelian (Purchase Orders - PO)</h2>
  <p>Pengadaan stok dilakukan secara tertib melalui Purchase Order. Menghindari pembelian ganda atau selisih harga saat barang dikirim oleh vendor.</p>

  <div class="screenshot-card">
    <img src="${getBase64Image('12_purchasing_orders.png')}" alt="Purchase Orders">
    <div class="screenshot-caption">Gambar 6.1: Daftar Pesanan Pembelian (PO) ke Supplier</div>
  </div>

  <h2 class="section-title">6.2 Pembayaran Pemasok &amp; Manajemen Vendor</h2>
  <p>Mencatat setiap pelunasan utang dagang kepada pemasok serta mengelola direktori supplier beserta termin pembayaran (Net 30, COD, dll.).</p>

  <div class="screenshot-card">
    <img src="${getBase64Image('13_purchasing_payments.png')}" alt="Purchasing Payments">
    <div class="screenshot-caption">Gambar 6.2: Pengelolaan Pembayaran Tagihan Pemasok (Bills &amp; Payments)</div>
  </div>

  <div class="screenshot-card">
    <img src="${getBase64Image('14_purchasing_suppliers.png')}" alt="Purchasing Suppliers">
    <div class="screenshot-caption">Gambar 6.3: Direktori Data Pemasok &amp; Rekening Tujuan Pembayaran</div>
  </div>
</div>

<!-- ================= BAB 7 ================= -->
<div class="chapter-break">
  <h1 class="chapter-title">BAB 7: MODUL INVENTORI & MANAJEMEN GUDANG</h1>

  <h2 class="section-title">7.1 Katalog Produk &amp; Ambang Batas Stok Minimum</h2>
  <p>Semua komoditas barang dagangan dikelola secara rapi dengan kode SKU, barcode, kategori, satuan hitung, harga beli, dan harga jual rekomendasi.</p>

  <div class="screenshot-card">
    <img src="${getBase64Image('15_inventory_products.png')}" alt="Inventory Products">
    <div class="screenshot-caption">Gambar 7.1: Katalog Produk, Harga Pokok/Jual, dan Pemantauan Stok Tersedia</div>
  </div>

  <h2 class="section-title">7.2 Log Mutasi Stok (Stock Movements)</h2>
  <p>Setiap perubahan stok tercatat secara permanen dengan jenis mutasi (Masuk, Keluar, Koreksi Opname) dan referensi dokumen asalnya.</p>

  <div class="screenshot-card">
    <img src="${getBase64Image('16_inventory_movements.png')}" alt="Stock Movements">
    <div class="screenshot-caption">Gambar 7.2: Log Riwayat Mutasi Keluar-Masuk Stok Barang</div>
  </div>
</div>

<!-- ================= BAB 8 ================= -->
<div class="chapter-break">
  <h1 class="chapter-title">BAB 8: MODUL AKUNTANSI & PEMBUKUAN KEUANGAN</h1>

  <h2 class="section-title">8.1 Bagan Akun Standar (Chart of Accounts / CoA)</h2>
  <p>Bagan Akun KePin mengikuti kaidah akuntansi baku (PSAK): 1000 (Aset), 2000 (Kewajiban), 3000 (Ekuitas), 4000 (Pendapatan), 5000 (HPP), dan 6000 (Beban).</p>

  <div class="screenshot-card">
    <img src="${getBase64Image('17_accounting_chart_of_accounts.png')}" alt="Chart of Accounts">
    <div class="screenshot-caption">Gambar 8.1: Daftar Bagan Akun (CoA) Toko Maju Jaya</div>
  </div>

  <h2 class="section-title">8.2 Mesin Modal Awal &amp; Jurnal Umum Transaksi</h2>
  <p>KePin memiliki mesin modal awal terpadu yang otomatis menerbitkan jurnal pembuka kanonik: <code>Debit: Kas (1000) / Kredit: Modal Pemilik (3000)</code>, memastikan neraca tidak pernah berselisih sejak hari pertama.</p>

  <div class="screenshot-card">
    <img src="${getBase64Image('18_accounting_journals.png')}" alt="Accounting Journals">
    <div class="screenshot-caption">Gambar 8.2: Buku Jurnal Umum &amp; Verifikasi Keseimbangan Debit-Kredit</div>
  </div>

  <h2 class="section-title">8.3 Rekonsiliasi Bank</h2>
  <p>Membandingkan mutasi rekening koran bank dengan catatan buku kas di KePin untuk memastikan tidak ada transfer atau biaya admin yang terlewat.</p>

  <div class="screenshot-card">
    <img src="${getBase64Image('19_accounting_reconciliation.png')}" alt="Bank Reconciliation">
    <div class="screenshot-caption">Gambar 8.3: Antarmuka Pencocokan &amp; Rekonsiliasi Rekening Bank</div>
  </div>
</div>

<!-- ================= BAB 9 ================= -->
<div class="chapter-break">
  <h1 class="chapter-title">BAB 9: MODUL LAPORAN KEUANGAN & EKSEKUTIF</h1>

  <h2 class="section-title">9.1 Laporan Laba Rugi, Neraca, &amp; Arus Kas</h2>
  <p>Semua transaksi menghasilkan laporan keuangan terpadu secara real-time:</p>
  <ul>
    <li><strong>Laba Rugi:</strong> Mengukur profitabilitas bersih usaha setelah dipotong seluruh beban pokok dan operasional.</li>
    <li><strong>Neraca Keuangan:</strong> Memotret posisi solvabilitas: Total Aset = Total Kewajiban + Total Ekuitas.</li>
    <li><strong>Arus Kas:</strong> Memantau perputaran uang kas riil masuk dan keluar.</li>
  </ul>

  <div class="screenshot-card">
    <img src="${getBase64Image('20_reports_financial.png')}" alt="Financial Reports">
    <div class="screenshot-caption">Gambar 9.1: Pusat Laporan Finansial Komprehensif Toko Maju Jaya</div>
  </div>

  <h2 class="section-title">9.2 Laporan Khusus Investor &amp; Eksekutif</h2>
  <p>Disiapkan khusus untuk presentasi kepada pemodal atau pengajuan kredit perbankan, menyajikan metrik pertumbuhan dan margin laba bersih.</p>

  <div class="screenshot-card">
    <img src="${getBase64Image('21_reports_investor.png')}" alt="Investor Reports">
    <div class="screenshot-caption">Gambar 9.2: Laporan Ringkasan Eksekutif &amp; Investor Toko Maju Jaya</div>
  </div>
</div>

<!-- ================= BAB 10 ================= -->
<div class="chapter-break">
  <h1 class="chapter-title">BAB 10: WAWASAN BISNIS OTOMATIS & AUDIT KEAMANAN</h1>

  <h2 class="section-title">10.1 Analisis Wawasan Bisnis Otomatis (Insights)</h2>
  <p>Mesin analitik KePin memberikan rekomendasi otomatis terkait tren omzet, produk terlaris, dan prediksi kehabisan stok.</p>

  <div class="screenshot-card">
    <img src="${getBase64Image('22_insights_analytics.png')}" alt="Insights Analytics">
    <div class="screenshot-caption">Gambar 10.1: Dasbor Analisis Wawasan Bisnis Otomatis (Insights)</div>
  </div>

  <h2 class="section-title">10.2 Log Jejak Audit (Audit Trail) &amp; Notifikasi</h2>
  <p>Menjamin transparansi penuh dan mencegah fraud internal dengan mencatat aktor, waktu, IP, dan detail aksi secara permanen.</p>

  <div class="screenshot-card">
    <img src="${getBase64Image('23_audit_trail.png')}" alt="Audit Trail">
    <div class="screenshot-caption">Gambar 10.2: Buku Catatan Jejak Audit Keamanan Sistem</div>
  </div>

  <div class="screenshot-card">
    <img src="${getBase64Image('24_notifications.png')}" alt="Notifications">
    <div class="screenshot-caption">Gambar 10.3: Pusat Notifikasi, Peringatan Jatuh Tempo, dan Stok Habis</div>
  </div>
</div>

<!-- ================= BAB 11 ================= -->
<div class="chapter-break">
  <h1 class="chapter-title">BAB 11: PENGATURAN PERUSAHAAN & KUSTOMISASI WORKSPACE</h1>

  <h2 class="section-title">11.1 Pengaturan Organisasi, Legalitas, &amp; Modal Awal</h2>
  <p>Konfigurasi data legal badan usaha, NPWP, alamat fisik, mata uang operasional, serta pengaturan input nilai modal awal usaha.</p>

  <div class="screenshot-card">
    <img src="${getBase64Image('27_settings_organization.png')}" alt="Organization Settings">
    <div class="screenshot-caption">Gambar 11.1: Pengaturan Profil Organisasi &amp; Modal Awal Usaha</div>
  </div>

  <h2 class="section-title">11.2 Manajemen Anggota Tim &amp; Peran (RBAC)</h2>
  <p>Menambahkan staf kasir, menentukan hak akses menu, dan membatasi staf agar tidak dapat melihat laporan keuntungan atau jurnal akuntansi.</p>

  <div class="screenshot-card">
    <img src="${getBase64Image('28_settings_members.png')}" alt="Members Settings">
    <div class="screenshot-caption">Gambar 11.2: Manajemen Anggota Tim &amp; Staf Karyawan</div>
  </div>

  <div class="screenshot-card">
    <img src="${getBase64Image('29_settings_roles.png')}" alt="Roles Settings">
    <div class="screenshot-caption">Gambar 11.3: Konfigurasi Matriks Peran &amp; Hak Akses Pengguna</div>
  </div>

  <h2 class="section-title">11.3 Pengelolaan Cabang Toko &amp; Kustomisasi Sidebar</h2>
  <p>Pengguna dapat mengelola toko multi-cabang serta menyesuaikan urutan dan visibilitas menu sidebar sesuai kebutuhan peran harian.</p>

  <div class="screenshot-card">
    <img src="${getBase64Image('30_settings_branches.png')}" alt="Branches Settings">
    <div class="screenshot-caption">Gambar 11.4: Pengelolaan Cabang Toko &amp; Outlet Ritel</div>
  </div>

  <div class="screenshot-card">
    <img src="${getBase64Image('31_settings_sidebar.png')}" alt="Sidebar Settings">
    <div class="screenshot-caption">Gambar 11.5: Pengaturan Visibilitas &amp; Kustomisasi Tata Letak Menu Sidebar</div>
  </div>

  <h2 class="section-title">11.4 Keamanan, Billing Langganan, &amp; Tutorial Interaktif</h2>
  <p>Fitur keamanan akun pengguna, pemantauan status kuota paket berlangganan, serta panduan interaktif langsung di layar.</p>

  <div class="screenshot-card">
    <img src="${getBase64Image('32_settings_security.png')}" alt="Security Settings">
    <div class="screenshot-caption">Gambar 11.6: Pengaturan Keamanan Sandi &amp; Verifikasi Dua Langkah (MFA)</div>
  </div>

  <div class="screenshot-card">
    <img src="${getBase64Image('33_settings_billing.png')}" alt="Billing Settings">
    <div class="screenshot-caption">Gambar 11.7: Status Paket Berlangganan &amp; Informasi Billing</div>
  </div>

  <div class="screenshot-card">
    <img src="${getBase64Image('25_tutorial.png')}" alt="Tutorial System">
    <div class="screenshot-caption">Gambar 11.8: Panduan Interaktif (Interactive Tour) Bagi Pengguna Pemula</div>
  </div>
</div>

<!-- ================= BAB 12 ================= -->
<div class="chapter-break">
  <h1 class="chapter-title">BAB 12: STUDI KASUS OPERASIONAL & PERBANDINGAN PERAN</h1>

  <h2 class="section-title">12.1 Perbandingan Tampilan: Pemilik vs Karyawan</h2>
  <p>Ketika staf kasir masuk ke sistem dengan peran Karyawan (<em>Employee</em>), sistem secara otomatis menyaring menu navigasi:</p>
  <ul>
    <li>Hanya menu operasional kasir dan penjualan yang ditampilkan.</li>
    <li>Menu Akuntansi, Laporan Keuangan, Pengaturan Anggota, dan Modal Awal otomatis terproteksi dan disembunyikan.</li>
  </ul>

  <div class="screenshot-card">
    <img src="${getBase64Image('34_employee_dashboard.png')}" alt="Employee Dashboard">
    <div class="screenshot-caption">Gambar 12.1: Tampilan Dashboard Terbatas untuk Peran Karyawan / Kasir</div>
  </div>

  <h2 class="section-title">12.2 Isolasi Data Multi-Tenant: Warung Segar</h2>
  <p>Tenant Warung Segar menggambarkan independensi total data antar-badan usaha. Seluruh katalog produk sayur-buah, transaksi penjualan kasir, dan pelanggan tersimpan secara terisolasi tanpa risiko kebocoran data ke tenant lain seperti Toko Maju Jaya.</p>

  <div class="screenshot-card">
    <img src="${getBase64Image('35_warung_segar_dashboard.png')}" alt="Warung Segar Dashboard">
    <div class="screenshot-caption">Gambar 12.2: Workspace Terpisah Tenant Warung Segar</div>
  </div>

  <div class="screenshot-card">
    <img src="${getBase64Image('36_warung_segar_pos.png')}" alt="Warung Segar POS">
    <div class="screenshot-caption">Gambar 12.3: Antarmuka Mesin Kasir Ritel Bahan Segar di Warung Segar</div>
  </div>
</div>

<!-- ================= BAB 13 ================= -->
<div class="chapter-break">
  <h1 class="chapter-title">BAB 13: PORTAL ADMINISTRATOR PLATFORM (SUPERADMIN)</h1>

  <h2 class="section-title">13.1 Beranda Admin &amp; Metrik Kesehatan Global Platform</h2>
  <p>Bagi pengelola pusat sistem dengan peran Platform Superadmin, tersedia konsol manajemen pusat (<code>/admin</code>) untuk mengawasi seluruh ekosistem KePin secara menyeluruh.</p>

  <div class="screenshot-card">
    <img src="${getBase64Image('37_admin_dashboard.png')}" alt="Admin Dashboard">
    <div class="screenshot-caption">Gambar 13.1: Beranda Platform Administrator KePin</div>
  </div>

  <h2 class="section-title">13.2 Manajemen Tenant &amp; Pengguna Platform</h2>
  <p>Memantau pertumbuhan badan usaha terdaftar, status aktivasi tenant, dan basis data pengguna terdaftar dari seluruh tenant.</p>

  <div class="screenshot-card">
    <img src="${getBase64Image('38_admin_tenants.png')}" alt="Admin Tenants">
    <div class="screenshot-caption">Gambar 13.2: Daftar Seluruh Tenant Perusahaan Terdaftar di Platform</div>
  </div>

  <div class="screenshot-card">
    <img src="${getBase64Image('39_admin_users.png')}" alt="Admin Users">
    <div class="screenshot-caption">Gambar 13.3: Direktori Pengguna Global Platform KePin</div>
  </div>

  <h2 class="section-title">13.3 Pengelolaan Paket Langganan &amp; Insiden Sistem</h2>
  <p>Mengatur batasan kuota transaksi tiap paket langganan serta pusat penanganan insiden dan gangguan teknis platform.</p>

  <div class="screenshot-card">
    <img src="${getBase64Image('40_admin_subscriptions.png')}" alt="Admin Subscriptions">
    <div class="screenshot-caption">Gambar 13.4: Manajemen Paket Berlangganan SaaS</div>
  </div>

  <div class="screenshot-card">
    <img src="${getBase64Image('41_admin_incidents.png')}" alt="Admin Incidents">
    <div class="screenshot-caption">Gambar 13.5: Panel Manajemen Insiden &amp; Pemantauan Kestabilan Sistem</div>
  </div>

  <h2 class="section-title">13.4 Log Audit Global &amp; Pengawasan Keamanan Platform</h2>
  <p>Audit trail komprehensif tingkat infrastruktur untuk meninjau akses superadmin dan kepatuhan regulasi perlindungan data pribadi pengguna.</p>

  <div class="screenshot-card">
    <img src="${getBase64Image('42_admin_audit.png')}" alt="Admin Audit">
    <div class="screenshot-caption">Gambar 13.6: Buku Jejak Audit Global Platform Administrator</div>
  </div>

  <div class="screenshot-card">
    <img src="${getBase64Image('43_admin_security.png')}" alt="Admin Security">
    <div class="screenshot-caption">Gambar 13.7: Parameter Konfigurasi Keamanan &amp; Zero Trust Platform</div>
  </div>
</div>

<!-- ================= BAB 14 ================= -->
<div class="chapter-break">
  <h1 class="chapter-title">BAB 14: PANDUAN PEMECAHAN MASALAH, FAQ, & GLOSARIUM</h1>

  <h2 class="section-title">14.1 Pemecahan Masalah Umum (Troubleshooting)</h2>
  <table class="data-table">
    <thead>
      <tr>
        <th>Gejala Kendala</th>
        <th>Kemungkinan Penyebab</th>
        <th>Langkah Solusi Terbukti</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td>Gagal masuk dengan pesan "Email atau password salah"</td>
        <td>Salah ketik atau capslock aktif pada password.</td>
        <td>Periksa huruf kapital. Gunakan fitur Reset Password jika lupa.</td>
      </tr>
      <tr>
        <td>Jurnal Pembuka Modal Awal belum muncul</td>
        <td>Modal awal belum disimpan di Pengaturan Organisasi.</td>
        <td>Buka menu <code>Pengaturan &gt; Organisasi</code>, masukkan nominal modal awal, lalu klik Simpan.</td>
      </tr>
      <tr>
        <td>Struk POS tidak terhubung ke printer thermal</td>
        <td>Driver printer lokal belum terpasang atau izin pop-up browser terblokir.</td>
        <td>Izinkan pop-up cetak pada peramban Chrome/Firefox, dan pastikan printer telah aktif.</td>
      </tr>
    </tbody>
  </table>

  <h2 class="section-title">14.2 Tanya Jawab Populer (FAQ)</h2>
  <div class="callout-box callout-info">
    <strong>T: Apakah data keuangan tenant saya dapat dilihat oleh perusahaan lain?</strong><br>
    J: Sama sekali tidak. KePin menerapkan isolasi logis basis data yang sangat ketat melalui Tenant ID pada setiap query database. Pengguna Toko Maju Jaya tidak memiliki akses teknis ke data Warung Segar.
  </div>

  <div class="callout-box callout-info">
    <strong>T: Apakah laporan keuangan di KePin sah untuk keperluan pajak UMKM?</strong><br>
    J: Ya. Laporan laba rugi dan neraca keuangan di KePin disusun sesuai prinsip akuntansi berpasangan baku yang dapat langsung digunakan sebagai lampiran SPT Pajak Tahunan.
  </div>

  <h2 class="section-title">14.3 Glosarium Istilah</h2>
  <p><strong>Tenant:</strong> Ruang kerja entitas satu badan usaha atau toko mandiri.<br>
  <strong>Double-Entry Accounting:</strong> Sistem pencatatan berpasangan di mana Debit harus seimbang dengan Kredit.<br>
  <strong>Chart of Accounts (CoA):</strong> Klasifikasi nomor akun pembukuan baku perusahaan.<br>
  <strong>Point of Sale (POS):</strong> Terminal kasir digital tempat berlangsungnya transaksi jual-beli langsung.<br>
  <strong>Role-Based Access Control (RBAC):</strong> Sistem pembatasan wewenang modul berdasarkan jabatan akun pengguna.</p>

  <hr style="margin: 25px 0; border: none; border-top: 1px solid #cbd5e1;">
  <p style="text-align: center; font-size: 9pt; color: #64748b;">
    <strong>KePin — Keuangan Pintar</strong> &bull; Seluruh Hak Cipta Dilindungi Undang-Undang &bull; Oktober 2026
  </p>
</div>

</body>
</html>
`;

async function main() {
  console.log('Writing scratch HTML guide...');
  fs.writeFileSync(OUT_HTML, html, 'utf8');

  console.log('Launching browser to generate PDF...');
  const browser = await chromium.launch({
    executablePath: '/usr/bin/chromium',
    args: ['--no-sandbox', '--disable-setuid-sandbox']
  });
  const page = await browser.newPage();
  
  await page.setContent(html, { waitUntil: 'load' });
  await page.waitForTimeout(2000); // Allow images to render completely

  console.log('Printing to PDF...');
  await page.pdf({
    path: OUT_PDF,
    format: 'A4',
    printBackground: true,
    displayHeaderFooter: true,
    headerTemplate: '<div style="font-size: 8px; color: #94a3b8; width: 100%; text-align: right; padding-right: 15mm;">KePin — Buku Panduan Pengguna Resmi</div>',
    footerTemplate: '<div style="font-size: 8px; color: #94a3b8; width: 100%; text-align: center;">Halaman <span class="pageNumber"></span> dari <span class="totalPages"></span></div>',
    margin: {
      top: '18mm',
      bottom: '20mm',
      left: '15mm',
      right: '15mm'
    }
  });

  await browser.close();
  console.log('✓ Successfully created PDF at:', OUT_PDF);

  console.log('Generating DOCX via LibreOffice...');
  try {
    execSync(`libreoffice --headless --convert-to "docx:MS Word 2007 XML" "${OUT_HTML}" --outdir "${path.dirname(OUT_DOCX)}"`, { stdio: 'inherit' });
    const generatedDocx = path.join(path.dirname(OUT_DOCX), 'scratch_guide.docx');
    if (fs.existsSync(generatedDocx)) {
      fs.renameSync(generatedDocx, OUT_DOCX);
      console.log('✓ Successfully created DOCX at:', OUT_DOCX);
    }
  } catch (err) {
    console.error('Error generating DOCX:', err.message);
  }

  // Clean up scratch HTML
  if (fs.existsSync(OUT_HTML)) {
    fs.unlinkSync(OUT_HTML);
  }

  console.log('\nALL DOCUMENTATION ASSETS READY IN documentation/dokumen/!');
}

main().catch(err => {
  console.error('Fatal error in PDF generation:', err);
  process.exit(1);
});
