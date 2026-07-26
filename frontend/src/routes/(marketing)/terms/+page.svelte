<script lang="ts">
  import PageHeader from '$lib/components/layout/PageHeader.svelte';
</script>

<PageHeader title="Syarat & Ketentuan" breadcrumbs={[{ label: 'Beranda', href: '/' }, { label: 'Syarat & Ketentuan' }]} />

<div class="prose prose-sm max-w-3xl text-[hsl(var(--foreground))] space-y-6">
  <p>Terakhir diperbarui: 1 Januari 2026</p>
  <section>
    <h2 class="text-xl font-bold mt-6">1. Layanan</h2>
    <p>KePin menyediakan platform SaaS akuntansi dan ERP berbasis langganan. Fitur tersedia sesuai paket yang dipilih dan dapat berubah seiring pengembangan produk.</p>
  </section>
  <section>
    <h2 class="text-xl font-bold mt-6">2. Akun dan Tanggung Jawab</h2>
    <p>Pengguna bertanggung jawab atas keamanan kredensial akun dan aktivitas yang terjadi dalam workspace. Admin organisasi bertanggung jawab atas pengaturan izin akses anggota.</p>
  </section>
  <section>
    <h2 class="text-xl font-bold mt-6">3. Pembayaran dan Langganan</h2>
    <p>Langganan diperbarui otomatis setiap periode. Pembatalan dapat dilakukan kapan saja. Data tetap dapat diakses hingga akhir periode yang telah dibayar.</p>
  </section>
  <section>
    <h2 class="text-xl font-bold mt-6">4. Batasan Tanggung Jawab</h2>
    <p>KePin tidak bertanggung jawab atas kerugian akibat keputusan bisnis yang dibuat berdasarkan data platform. Laporan keuangan tetap harus diverifikasi oleh profesional.</p>
  </section>
  <section>
    <h2 class="text-xl font-bold mt-6">5. Penghentian Layanan</h2>
    <p>Kami dapat menghentikan akses jika terjadi pelanggaran ketentuan. Pemberitahuan akan diberikan sebelumnya kecuali dalam kasus pelanggaran serius.</p>
  </section>
</div>
