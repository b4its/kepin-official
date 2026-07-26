<script lang="ts">
  import PageHeader from '$lib/components/layout/PageHeader.svelte';
</script>

<PageHeader title="Kebijakan Privasi" breadcrumbs={[{ label: 'Beranda', href: '/' }, { label: 'Kebijakan Privasi' }]} />

<div class="prose prose-sm max-w-3xl text-[hsl(var(--foreground))] space-y-6">
  <p>Terakhir diperbarui: 1 Januari 2026</p>
  <section>
    <h2 class="text-xl font-bold mt-6">1. Pengumpulan Data</h2>
    <p>Kami mengumpulkan data yang Anda berikan saat pendaftaran dan penggunaan platform, termasuk nama, email, informasi perusahaan, dan data transaksi bisnis.</p>
  </section>
  <section>
    <h2 class="text-xl font-bold mt-6">2. Penggunaan Data</h2>
    <p>Data digunakan untuk menyediakan layanan akuntansi dan ERP, meningkatkan kualitas produk, serta mematuhi kewajiban hukum. Kami tidak menjual data Anda kepada pihak ketiga.</p>
  </section>
  <section>
    <h2 class="text-xl font-bold mt-6">3. Keamanan Data</h2>
    <p>Kami menerapkan enkripsi end-to-end, akses berbasis peran, dan audit trail untuk melindungi data Anda. Seluruh data disimpan di pusat data yang aman dengan sertifikasi ISO 27001.</p>
  </section>
  <section>
    <h2 class="text-xl font-bold mt-6">4. Hak Anda</h2>
    <p>Anda berhak mengakses, memperbaiki, dan mengekspor data kapan saja. Permintaan penghapusan data dapat diajukan melalui dukungan pelanggan.</p>
  </section>
  <section>
    <h2 class="text-xl font-bold mt-6">5. Cookie</h2>
    <p>Kami menggunakan cookie esensial untuk autentikasi dan preferensi tema. Cookie pelacakan hanya digunakan dengan persetujuan eksplisit.</p>
  </section>
</div>
