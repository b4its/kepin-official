<script lang="ts">
  import { ArrowRight, Check, Shield, TrendingUp, BarChart3, Package, BookOpen, Users, Clock, Download, FileText, Layers, Lock, Target, ChevronDown, ShoppingCart } from '@lucide/svelte';
  import Button from '$lib/components/ui/Button.svelte';

  let activeFaq = $state<string | null>(null);

  function toggleFaq(id: string) {
    activeFaq = activeFaq === id ? null : id;
  }

  const securityItems = [
    { icon: Lock, text: 'Verifikasi identitas dan akses berdasarkan peran pengguna' },
    { icon: Layers, text: 'Isolasi data ketat antarorganisasi' },
    { icon: Shield, text: 'Otentikasi multi-faktor (MFA) dan manajemen session' },
    { icon: FileText, text: 'Audit trail append-only yang tidak dapat dimanipulasi' },
    { icon: Lock, text: 'Enkripsi data dalam transit (TLS 1.3) dan penyimpanan' },
  ];

  const caraKerjaSteps = [
    { num: '01', title: 'Buat Workspace', desc: 'Daftar dan buat workspace bisnis Anda. Isi profil, atur cabang, dan pilih template akun.' },
    { num: '02', title: 'Setup Bisnis', desc: 'Atur produk, pelanggan, pemasok, dan undang tim Anda. Semua dalam beberapa klik.' },
    { num: '03', title: 'Catat Transaksi', desc: 'Input penjualan, pembelian, dan pengeluaran. Stok dan jurnal terupdate otomatis.' },
    { num: '04', title: 'Pantau & Kembangkan', desc: 'Pantau dashboard, baca laporan, dapatkan insight AI, dan ambil keputusan lebih baik.' },
  ];

  const useCases = [
    { icon: ShoppingCart, title: 'Ritel', desc: 'Kontrol selisih stok dan identifikasi produk lambat bergerak secara real-time.' },
    { icon: Users, title: 'F&B', desc: 'Kelola bahan baku, pembelian, biaya produksi, dan margin menu dalam satu tempat.' },
    { icon: Package, title: 'Manufaktur Kecil', desc: 'Pantau bahan baku, proses produksi, hasil, dan biaya dasar produksi.' },
    { icon: TrendingUp, title: 'Startup', desc: 'Transparansi arus kas dan laporan kredibel untuk investor dan dewan direksi.' },
  ];

  const pricingPlans = [
    {
      name: 'Basic',
      price: '199.000',
      period: '/bulan',
      desc: 'Untuk pemilik usaha yang baru memulai pencatatan keuangan.',
      features: ['Akuntansi dasar', '50 transaksi/bulan', '1 pengguna', '1 cabang', 'Laporan laba rugi & neraca', 'Dukungan email'],
      cta: 'Mulai Trial Gratis',
      popular: false,
    },
    {
      name: 'Premium',
      price: '499.000',
      period: '/bulan',
      desc: 'Untuk usaha yang membutuhkan kontrol operasional dan stok.',
      features: ['Semua fitur Basic', 'Transaksi tak terbatas', '5 pengguna', '3 cabang', 'Manajemen stok & produk', 'Invoice & pelanggan', 'Prediksi AI dasar', 'Dukungan prioritas'],
      cta: 'Mulai Trial Gratis',
      popular: true,
    },
    {
      name: 'Platinum',
      price: '999.000',
      period: '/bulan',
      desc: 'Untuk perusahaan yang siap fundraising dan due diligence.',
      features: ['Semua fitur Premium', 'Pengguna tak terbatas', 'Cabang tak terbatas', 'Laporan investor kustom', 'Audit trail lengkap', 'AI insight lanjutan', 'Rekonsiliasi bank', 'Dukungan dedicated'],
      cta: 'Jadwalkan Demo',
      popular: false,
    },
  ];

  const faqs = [
    {
      id: 'cocok',
      q: 'Apakah KePin cocok untuk bisnis tanpa staf akuntansi?',
      a: 'Ya. KePin dirancang agar mudah digunakan oleh pemilik usaha tanpa latar belakang akuntansi. Sistem memandu Anda dari pencatatan transaksi hingga laporan keuangan yang siap digunakan.',
    },
    {
      id: 'pemisahan',
      q: 'Bagaimana pemisahan data antar perusahaan?',
      a: 'Setiap organisasi memiliki workspace terisolasi. Data Anda tidak dapat diakses oleh organisasi lain, dan setiap pengguna hanya melihat data sesuai izin aksesnya.',
    },
    {
      id: 'cabang',
      q: 'Apakah dapat mengelola banyak cabang?',
      a: 'Ya. Anda dapat menambahkan beberapa cabang dalam satu workspace. Setiap cabang dapat memiliki stok, transaksi, dan laporan sendiri yang tetap tergabung dalam laporan konsolidasi.',
    },
    {
      id: 'trial',
      q: 'Apa yang terjadi setelah masa trial?',
      a: 'Data Anda tetap aman. Anda dapat memilih paket yang sesuai atau mengekspor data kapan saja. Tidak ada lock-in dan tidak ada biaya tersembunyi.',
    },
    {
      id: 'ekspor',
      q: 'Bagaimana cara ekspor data?',
      a: 'Laporan dapat diekspor ke PDF, CSV, dan XLSX. Seluruh data dapat diekspor melalui menu pengaturan kapan saja selama akun aktif.',
    },
    {
      id: 'prediksi',
      q: 'Bagaimana prediksi AI bekerja?',
      a: 'AI menganalisis data historis penjualan, tren musiman, dan pola bisnis Anda untuk memberikan prediksi penjualan dan laba. Setiap prediksi menampilkan rentang kepercayaan, faktor utama, dan periode yang dianalisis.',
    },
  ];
</script>

<!-- Hero -->
<section class="relative min-h-[90vh] flex items-center bg-[var(--color-canvas)] overflow-hidden">
  <div class="absolute inset-0 opacity-10">
    <div class="absolute top-20 left-10 w-32 h-32 border-4 border-[var(--color-kepin-red)] rotate-12"></div>
    <div class="absolute top-40 right-20 w-24 h-24 bg-[var(--color-kepin-blue)]"></div>
    <div class="absolute bottom-32 left-1/4 w-16 h-16 border-4 border-[var(--color-kepin-yellow)] rotate-45"></div>
    <div class="absolute top-1/3 right-1/3 w-40 h-0.5 bg-[var(--color-kepin-red)] -rotate-45"></div>
    <div class="absolute bottom-40 right-10 w-20 h-20 border-2 border-[var(--color-ink)] rounded-full"></div>
    <div class="absolute top-1/2 left-5 w-3 h-3 bg-[var(--color-kepin-red)]"></div>
  </div>
  <div class="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20 sm:py-32">
    <div class="grid lg:grid-cols-2 gap-12 items-center">
      <div>
        <h1 class="text-5xl sm:text-6xl lg:text-7xl xl:text-8xl font-bold font-display leading-[0.95] tracking-tight text-[var(--color-ink)]">
          Keuangan rapi.<br>
          Operasional <span class="text-[var(--color-kepin-red)]">terkendali</span>.<br>
          Bisnis lebih <span class="text-[var(--color-kepin-blue)]">dipercaya</span>.
        </h1>
        <p class="mt-6 text-lg sm:text-xl text-[var(--color-muted)] max-w-lg leading-relaxed">
          KePin menyatukan akuntansi, inventaris, audit trail, dan insight bisnis untuk membantu UMKM tumbuh dengan keputusan yang lebih aman.
        </p>
        <div class="mt-8 flex flex-col sm:flex-row gap-3 sm:items-center">
          <a href="/auth/register" class="btn-primary btn-lg text-center">
            Coba Gratis 14 Hari
          </a>
          <a href="#solusi" class="btn-ghost btn-lg text-center border-2 border-[var(--color-ink)]">
            Lihat Cara Kerja
          </a>
        </div>
        <p class="mt-3 text-sm text-[var(--color-muted)]">Tanpa kartu kredit. Batalkan kapan saja.</p>
      </div>
      <div class="hidden lg:block relative">
        <div class="card p-6 shadow-[8px_8px_0px_var(--color-ink)] border-2 border-[var(--color-ink)]">
          <div class="grid grid-cols-2 gap-4 mb-4">
            <div>
              <p class="text-xs text-[hsl(var(--muted-foreground))] mb-1">Pendapatan Bulan Ini</p>
              <p class="text-2xl font-bold tabular-nums">Rp 89,5 Jt</p>
              <p class="text-xs text-[var(--color-kepin-green)]">+12.5%</p>
            </div>
            <div>
              <p class="text-xs text-[hsl(var(--muted-foreground))] mb-1">Stok Kritis</p>
              <p class="text-2xl font-bold tabular-nums">3</p>
              <p class="text-xs text-[var(--color-kepin-red)]">Perlu restock</p>
            </div>
          </div>
          <div class="h-32 border border-[var(--color-line)] rounded flex items-center justify-center bg-[hsl(var(--muted))]">
            <BarChart3 class="w-8 h-8 text-[hsl(var(--muted-foreground))]" />
          </div>
          <div class="flex justify-between items-center mt-4 pt-4 border-t border-[var(--color-line)]">
            <div class="flex items-center gap-2">
              <Shield class="w-4 h-4 text-[var(--color-kepin-green)]" />
              <span class="text-xs text-[hsl(var(--muted-foreground))]">Audit trail aktif</span>
            </div>
            <span class="text-xs font-medium text-[var(--color-kepin-blue)]">Live</span>
          </div>
        </div>
        <div class="absolute -bottom-4 -right-4 w-24 h-24 bg-[var(--color-kepin-yellow)] -z-10"></div>
      </div>
    </div>
  </div>
</section>

<!-- Trust Strip -->
<section class="py-8 sm:py-12 bg-[#171714]">
  <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
    <div class="flex flex-wrap items-center justify-center gap-8 sm:gap-12 text-center">
      <div>
        <p class="text-2xl sm:text-3xl font-bold text-white">5.000+</p>
        <p class="text-xs text-gray-400">UMKM Terdaftar</p>
      </div>
      <div>
        <p class="text-2xl sm:text-3xl font-bold text-white">50+</p>
        <p class="text-xs text-gray-400">Kota Tersebar</p>
      </div>
      <div>
        <p class="text-2xl sm:text-3xl font-bold text-white">99.9%</p>
        <p class="text-xs text-gray-400">Uptime Platform</p>
      </div>
      <div>
        <p class="text-2xl sm:text-3xl font-bold text-white">ISO 27001</p>
        <p class="text-xs text-gray-400">Sertifikasi Keamanan</p>
      </div>
    </div>
  </div>
</section>

<!-- Masalah -->
<section id="solusi" class="py-16 sm:py-24 bg-[var(--color-canvas)]">
  <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
    <div class="text-center mb-12 sm:mb-16">
      <h2 class="text-3xl sm:text-4xl lg:text-5xl font-bold font-display text-[var(--color-ink)]">
        Masalah yang Sering Terjadi
      </h2>
      <p class="mt-4 text-lg text-[var(--color-muted)] max-w-2xl mx-auto">
        Banyak UMKM menghadapi tantangan yang sama. KePin hadir sebagai solusi.
      </p>
    </div>
    <div class="grid md:grid-cols-3 gap-6 sm:gap-8">
      <div class="card-hover p-6 sm:p-8 border-2 border-[var(--color-ink)]">
        <div class="w-12 h-12 bg-[var(--color-kepin-red)] flex items-center justify-center mb-4">
          <Clock class="w-6 h-6 text-white" />
        </div>
        <h3 class="text-xl font-bold mb-2 text-[var(--color-ink)]">Fraud & Selisih Terlambat Diketahui</h3>
        <p class="text-[var(--color-muted)] leading-relaxed">
          Stok hilang atau uang tidak sesuai baru diketahui saat tutup buku. KePin memberikan notifikasi real-time atas setiap kejanggalan.
        </p>
      </div>
      <div class="card-hover p-6 sm:p-8 border-2 border-[var(--color-ink)]">
        <div class="w-12 h-12 bg-[var(--color-kepin-blue)] flex items-center justify-center mb-4">
          <Layers class="w-6 h-6 text-white" />
        </div>
        <h3 class="text-xl font-bold mb-2 text-[var(--color-ink)]">Data Keuangan Tersebar</h3>
        <p class="text-[var(--color-muted)] leading-relaxed">
          Catatan di buku, stok di spreadsheet, pembayaran di aplikasi terpisah. Sulit mendapatkan gambaran utuh bisnis Anda.
        </p>
      </div>
      <div class="card-hover p-6 sm:p-8 border-2 border-[var(--color-ink)]">
        <div class="w-12 h-12 bg-[var(--color-kepin-yellow)] flex items-center justify-center mb-4">
          <Target class="w-6 h-6 text-[var(--color-ink)]" />
        </div>
        <h3 class="text-xl font-bold mb-2 text-[var(--color-ink)]">Keputusan Tanpa Data</h3>
        <p class="text-[var(--color-muted)] leading-relaxed">
          Pembelian stok dilakukan tanpa melihat tren penjualan. Akibatnya: dead stock, cash flow terhambat, dan kehilangan peluang.
        </p>
      </div>
    </div>
  </div>
</section>

<!-- Alur Solusi -->
<section class="py-16 sm:py-24 bg-[var(--color-surface)]">
  <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
    <div class="text-center mb-12 sm:mb-16">
      <h2 class="text-3xl sm:text-4xl lg:text-5xl font-bold font-display text-[var(--color-ink)]">
        Satu Alur, dari Operasional ke Keputusan
      </h2>
      <p class="mt-4 text-lg text-[var(--color-muted)] max-w-2xl mx-auto">
        Data operasional mengalir otomatis ke pencatatan keuangan dengan kontrol di setiap tahap.
      </p>
    </div>
    <div class="flex flex-wrap items-center justify-center gap-4 sm:gap-8 text-center">
      <div class="flex flex-col items-center">
        <div class="w-14 h-14 bg-[var(--color-kepin-red)] flex items-center justify-center rounded-full">
          <ShoppingCart class="w-6 h-6 text-white" />
        </div>
        <p class="mt-2 font-semibold text-sm">Penjualan</p>
      </div>
      <ArrowRight class="w-6 h-6 text-[var(--color-muted)] hidden sm:block" />
      <div class="flex flex-col items-center">
        <div class="w-14 h-14 bg-[var(--color-kepin-blue)] flex items-center justify-center rounded-full">
          <Package class="w-6 h-6 text-white" />
        </div>
        <p class="mt-2 font-semibold text-sm">Stok</p>
      </div>
      <ArrowRight class="w-6 h-6 text-[var(--color-muted)] hidden sm:block" />
      <div class="flex flex-col items-center">
        <div class="w-14 h-14 bg-[hsl(var(--foreground))] flex items-center justify-center rounded-full">
          <BookOpen class="w-6 h-6 text-[hsl(var(--background))]" />
        </div>
        <p class="mt-2 font-semibold text-sm">Jurnal</p>
      </div>
      <ArrowRight class="w-6 h-6 text-[var(--color-muted)] hidden sm:block" />
      <div class="flex flex-col items-center">
        <div class="w-14 h-14 bg-[var(--color-kepin-yellow)] flex items-center justify-center rounded-full">
          <BarChart3 class="w-6 h-6 text-[var(--color-ink)]" />
        </div>
        <p class="mt-2 font-semibold text-sm">Laporan</p>
      </div>
      <ArrowRight class="w-6 h-6 text-[var(--color-muted)] hidden sm:block" />
      <div class="flex flex-col items-center">
        <div class="w-14 h-14 bg-[var(--color-kepin-green)] flex items-center justify-center rounded-full">
          <TrendingUp class="w-6 h-6 text-white" />
        </div>
        <p class="mt-2 font-semibold text-sm">Insight</p>
      </div>
      <ArrowRight class="w-6 h-6 text-[var(--color-muted)] hidden sm:block" />
      <div class="flex flex-col items-center">
        <div class="w-14 h-14 bg-[var(--color-kepin-red)] flex items-center justify-center rounded-full">
          <Target class="w-6 h-6 text-white" />
        </div>
        <p class="mt-2 font-semibold text-sm">Keputusan</p>
      </div>
    </div>
  </div>
</section>

<!-- Fitur Unggulan -->
<section id="fitur" class="py-16 sm:py-24 bg-[var(--color-canvas)]">
  <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
    <div class="text-center mb-12 sm:mb-16">
      <h2 class="text-3xl sm:text-4xl lg:text-5xl font-bold font-display text-[var(--color-ink)]">
        Fitur Unggulan
      </h2>
      <p class="mt-4 text-lg text-[var(--color-muted)] max-w-2xl mx-auto">
        Lebih dari sekadar aplikasi akuntansi. KePin adalah sistem operasional dan kontrol bisnis Anda.
      </p>
    </div>
    <div class="grid md:grid-cols-2 lg:grid-cols-3 gap-6 sm:gap-8">
      <div class="card-hover p-6 border-2 border-[var(--color-ink)]">
        <div class="w-10 h-10 bg-[var(--color-kepin-blue)] flex items-center justify-center mb-3">
          <BookOpen class="w-5 h-5 text-white" />
        </div>
        <h3 class="font-bold text-lg mb-1">Akuntansi Dasar</h3>
        <p class="text-sm text-[var(--color-muted)]">Transaksi, chart of accounts, jurnal, buku besar, dan laporan keuangan lengkap.</p>
      </div>
      <div class="card-hover p-6 border-2 border-[var(--color-ink)]">
        <div class="w-10 h-10 bg-[var(--color-kepin-green)] flex items-center justify-center mb-3">
          <Package class="w-5 h-5 text-white" />
        </div>
        <h3 class="font-bold text-lg mb-1">ERP Ringan</h3>
        <p class="text-sm text-[var(--color-muted)]">Penjualan, pembelian, pemasok, pelanggan, produk, dan stok dalam satu platform.</p>
      </div>
      <div class="card-hover p-6 border-2 border-[var(--color-ink)]">
        <div class="w-10 h-10 bg-[hsl(var(--foreground))] flex items-center justify-center mb-3">
          <Shield class="w-5 h-5 text-[hsl(var(--background))]" />
        </div>
        <h3 class="font-bold text-lg mb-1">Audit Trail</h3>
        <p class="text-sm text-[var(--color-muted)]">Setiap perubahan tercatat: siapa, apa, kapan, tenant, dan nilai sebelum-sesudah.</p>
      </div>
      <div class="card-hover p-6 border-2 border-[var(--color-ink)]">
        <div class="w-10 h-10 bg-[var(--color-kepin-yellow)] flex items-center justify-center mb-3">
          <TrendingUp class="w-5 h-5 text-[var(--color-ink)]" />
        </div>
        <h3 class="font-bold text-lg mb-1">AI Insight</h3>
        <p class="text-sm text-[var(--color-muted)]">Prediksi penjualan dan laba serta rekomendasi stok berdasarkan data bisnis Anda.</p>
      </div>
      <div class="card-hover p-6 border-2 border-[var(--color-ink)]">
        <div class="w-10 h-10 bg-[var(--color-kepin-red)] flex items-center justify-center mb-3">
          <FileText class="w-5 h-5 text-white" />
        </div>
        <h3 class="font-bold text-lg mb-1">Investor Report</h3>
        <p class="text-sm text-[var(--color-muted)]">Laporan kustom siap due diligence dengan metrik yang kredibel dan dapat diverifikasi.</p>
      </div>
      <div class="card-hover p-6 border-2 border-[var(--color-ink)]">
        <div class="w-10 h-10 bg-[var(--color-kepin-blue)] flex items-center justify-center mb-3">
          <Download class="w-5 h-5 text-white" />
        </div>
        <h3 class="font-bold text-lg mb-1">Multi-Format Export</h3>
        <p class="text-sm text-[var(--color-muted)]">Ekspor laporan ke PDF, CSV, XLSX. Data tetap milik Anda, dapat dibawa kapan saja.</p>
      </div>
    </div>
  </div>
</section>

<!-- Keamanan Zero Trust -->
<section id="keamanan" class="py-16 sm:py-24 bg-[var(--color-surface)]">
  <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
    <div class="grid lg:grid-cols-2 gap-12 items-center">
      <div>
        <div class="w-14 h-14 bg-[var(--color-kepin-red)] flex items-center justify-center mb-6">
          <Shield class="w-7 h-7 text-white" />
        </div>
        <h2 class="text-3xl sm:text-4xl lg:text-5xl font-bold font-display text-[var(--color-ink)] mb-4">
          Keamanan<br><span class="text-[var(--color-kepin-blue)]">Zero Trust</span>
        </h2>
        <p class="text-lg text-[var(--color-muted)] mb-6 leading-relaxed">
          Keamanan bukan fitur tambahan. Ini adalah fondasi platform.
        </p>
        <ul class="space-y-4">
          {#each securityItems as safeguard}
            <li class="flex items-start gap-3">
              <safeguard.icon class="w-5 h-5 text-[var(--color-kepin-green)] shrink-0 mt-0.5" />
              <span class="text-[var(--color-muted)]">{safeguard.text}</span>
            </li>
          {/each}
        </ul>
        <a href="/security" class="btn-ghost mt-6 inline-flex items-center gap-2 border-2 border-[var(--color-ink)]">
          Pelajari Lebih Lanjut <ArrowRight class="w-4 h-4" />
        </a>
      </div>
      <div class="relative hidden lg:block">
        <div class="border-4 border-[var(--color-ink)] p-8">
          <div class="grid grid-cols-2 gap-4">
            <div class="bg-[var(--color-kepin-red)] p-4">
              <p class="text-white font-bold text-lg">ISO 27001</p>
            </div>
            <div class="bg-[hsl(var(--foreground))] p-4">
              <p class="text-[hsl(var(--background))] font-bold text-lg">Enkripsi</p>
            </div>
            <div class="bg-[var(--color-kepin-blue)] p-4">
              <p class="text-white font-bold text-lg">MFA</p>
            </div>
            <div class="bg-[var(--color-kepin-yellow)] p-4">
              <p class="text-[var(--color-ink)] font-bold text-lg">Audit</p>
            </div>
          </div>
        </div>
        <div class="absolute -top-4 -left-4 w-full h-full border-4 border-[var(--color-kepin-red)] -z-10"></div>
      </div>
    </div>
  </div>
</section>

<!-- Cara Kerja -->
<section id="cara-kerja" class="py-16 sm:py-24 bg-[var(--color-canvas)]">
  <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
    <div class="text-center mb-12 sm:mb-16">
      <h2 class="text-3xl sm:text-4xl lg:text-5xl font-bold font-display text-[var(--color-ink)]">
        Cara Kerja
      </h2>
      <p class="mt-4 text-lg text-[var(--color-muted)] max-w-2xl mx-auto">
        Mulai dalam hitungan menit. Tidak perlu setup rumit.
      </p>
    </div>
    <div class="grid sm:grid-cols-2 lg:grid-cols-4 gap-6 sm:gap-8">
      {#each caraKerjaSteps as step}
        <div class="card-hover p-6 sm:p-8 border-2 border-[var(--color-ink)]">
          <p class="text-5xl font-bold font-display text-[var(--color-kepin-red)] mb-4">{step.num}</p>
          <h3 class="text-lg font-bold mb-2 text-[var(--color-ink)]">{step.title}</h3>
          <p class="text-sm text-[var(--color-muted)] leading-relaxed">{step.desc}</p>
        </div>
      {/each}
    </div>
  </div>
</section>

<!-- Use Case -->
<section class="py-16 sm:py-24 bg-[var(--color-surface)]">
  <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
    <div class="text-center mb-12 sm:mb-16">
      <h2 class="text-3xl sm:text-4xl lg:text-5xl font-bold font-display text-[var(--color-ink)]">
        Untuk Siapa KePin?
      </h2>
    </div>
    <div class="grid sm:grid-cols-2 lg:grid-cols-4 gap-6">
      {#each useCases as useCase}
        <div class="p-6 border-2 border-[var(--color-ink)]">
          <useCase.icon class="w-8 h-8 text-[var(--color-kepin-red)] mb-3" />
          <h3 class="font-bold text-lg mb-1">{useCase.title}</h3>
          <p class="text-sm text-[var(--color-muted)]">{useCase.desc}</p>
        </div>
      {/each}
    </div>
  </div>
</section>

<!-- Pricing -->
<section id="harga" class="py-16 sm:py-24 bg-[var(--color-canvas)]">
  <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
    <div class="text-center mb-12">
      <h2 class="text-3xl sm:text-4xl lg:text-5xl font-bold font-display text-[var(--color-ink)]">
        Harga Sederhana
      </h2>
      <p class="mt-4 text-lg text-[var(--color-muted)]">Pilih paket yang sesuai dengan kebutuhan bisnis Anda.</p>
    </div>
    <div class="grid md:grid-cols-3 gap-6 sm:gap-8 max-w-5xl mx-auto">
      {#each pricingPlans as plan}
        <div class="relative card p-6 sm:p-8 border-2 border-[var(--color-ink)] flex flex-col" class:shadow-[8px_8px_0px_var(--color-ink)]={plan.popular}>
          {#if plan.popular}
            <div class="absolute -top-3 left-1/2 -translate-x-1/2 bg-[var(--color-kepin-red)] text-white px-4 py-1 text-xs font-bold">
              POPULER
            </div>
          {/if}
          <h3 class="text-xl font-bold text-[var(--color-ink)]">{plan.name}</h3>
          <p class="text-sm text-[var(--color-muted)] mt-1">{plan.desc}</p>
          <div class="mt-4 mb-6">
            <span class="text-4xl font-bold text-[var(--color-ink)]">Rp{plan.price}</span>
            <span class="text-sm text-[var(--color-muted)]">{plan.period}</span>
          </div>
          <ul class="space-y-2 flex-1">
            {#each plan.features as feature}
              <li class="flex items-center gap-2 text-sm">
                <Check class="w-4 h-4 text-[var(--color-kepin-green)] shrink-0" />
                <span>{feature}</span>
              </li>
            {/each}
          </ul>
          <a
            href={plan.popular ? '/auth/register?plan=premium' : '/auth/register'}
            class="mt-6 btn-primary text-center w-full"
            class:bg-[var(--color-kepin-red)]={plan.popular}
          >
            {plan.cta}
          </a>
          {#if plan.popular}
            <p class="mt-2 text-xs text-center text-[var(--color-muted)]">Promo Early Adopter: 50% untuk tahun pertama</p>
          {/if}
        </div>
      {/each}
    </div>
  </div>
</section>

<!-- Early Adopter -->
<section class="py-12 sm:py-16 bg-[var(--color-kepin-red)]">
  <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
    <h2 class="text-2xl sm:text-3xl lg:text-4xl font-bold font-display text-white mb-3">
      Program Early Adopter
    </h2>
    <p class="text-white/80 max-w-2xl mx-auto mb-6">
      Dapatkan diskon 50% untuk tahun pertama. Kuota terbatas untuk 50 klien pertama. Sebagai imbalannya, Anda bersedia memberikan testimoni dan feedback untuk pengembangan produk.
    </p>
    <a href="/auth/register" class="inline-flex items-center gap-2 bg-white text-[var(--color-kepin-red)] font-bold px-8 py-3 text-lg hover:bg-gray-100 transition-colors">
      Ambil Diskon Early Adopter
    </a>
  </div>
</section>

<!-- FAQ -->
<section id="faq" class="py-16 sm:py-24 bg-[var(--color-surface)]">
  <div class="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8">
    <div class="text-center mb-12">
      <h2 class="text-3xl sm:text-4xl font-bold font-display text-[var(--color-ink)]">
        Pertanyaan Umum
      </h2>
    </div>
    <div class="space-y-3">
      {#each faqs as faq}
        <div class="border-2 border-[var(--color-ink)]">
          <button
            class="flex items-center justify-between w-full px-5 py-4 text-left bg-[var(--color-surface)] hover:bg-[var(--color-canvas)] transition-colors"
            onclick={() => toggleFaq(faq.id)}
          >
            <span class="font-semibold text-sm sm:text-base pr-4">{faq.q}</span>
            <span
              class="inline-flex transition-transform duration-200 {activeFaq === faq.id ? 'rotate-180' : ''}"
            >
              <ChevronDown class="w-5 h-5 shrink-0" />
            </span>
          </button>
          {#if activeFaq === faq.id}
            <div class="px-5 pb-4 text-sm text-[var(--color-muted)] leading-relaxed border-t-2 border-[var(--color-ink)] pt-3">
              {faq.a}
            </div>
          {/if}
        </div>
      {/each}
    </div>
  </div>
</section>

<!-- Final CTA -->
<section class="py-16 sm:py-24 bg-[#171714]">
  <div class="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
    <h2 class="text-3xl sm:text-4xl lg:text-5xl font-bold font-display text-white mb-4">
      Siap Mengelola Bisnis dengan Lebih Percaya Diri?
    </h2>
    <p class="text-gray-400 text-lg max-w-2xl mx-auto mb-8">
      Bergabung dengan ribuan UMKM yang sudah menggunakan KePin untuk transparansi, keamanan, dan pertumbuhan bisnis.
    </p>
    <div class="flex flex-col sm:flex-row gap-3 justify-center">
      <a href="/auth/register" class="btn-primary btn-lg text-center bg-white text-[var(--color-ink)] hover:bg-gray-100">
        Coba Gratis 14 Hari
      </a>
      <a href="/auth/register?plan=platinum" class="btn-ghost btn-lg text-center text-white border-2 border-white hover:bg-white/10">
        Jadwalkan Demo
      </a>
    </div>
    <p class="mt-4 text-sm text-gray-500">Tanpa kartu kredit. Dukungan setup gratis.</p>
  </div>
</section>


