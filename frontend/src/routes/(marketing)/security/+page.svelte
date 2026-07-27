<script lang="ts">
  import { Shield, Lock, Layers, FileText, Server, Key } from '@lucide/svelte';
  import PageHeader from '$lib/components/layout/PageHeader.svelte';

  const securityItems = [
    { icon: Shield, title: 'Sertifikasi ISO 27001', desc: 'Sistem manajemen keamanan informasi bersertifikasi internasional.' },
    { icon: Lock, title: 'Enkripsi End-to-End', desc: 'Data dienkripsi dengan TLS 1.3 saat transit dan AES-256 saat penyimpanan.' },
    { icon: Layers, title: 'Isolasi Tenant', desc: 'Setiap organisasi memiliki workspace terpisah dengan akses yang dikontrol ketat.' },
    { icon: FileText, title: 'Audit Trail Immutable', desc: 'Setiap perubahan tercatat secara permanen dan tidak dapat diubah oleh siapapun.' },
    { icon: Key, title: 'Multi-Factor Auth', desc: 'Lapisan keamanan tambahan dengan MFA untuk akun dengan akses sensitif.' },
    { icon: Server, title: 'Infrastruktur Aman', desc: 'Hosting di pusat data tier-4 dengan redundansi penuh dan pemantauan 24/7.' },
  ];
</script>

<PageHeader title="Keamanan" breadcrumbs={[{ label: 'Beranda', href: '/' }, { label: 'Keamanan' }]} description="Komitmen kami terhadap keamanan dan privasi data Anda." />

<div class="space-y-8 max-w-3xl">
  <div class="grid sm:grid-cols-2 gap-4">
    {#each securityItems as item}
      <div class="card p-5">
        <item.icon class="w-6 h-6 text-[var(--color-kepin-red)] mb-3" />
        <h3 class="font-bold mb-1">{item.title}</h3>
        <p class="text-sm text-[hsl(var(--muted-foreground))]">{item.desc}</p>
      </div>
    {/each}
  </div>

  <section>
    <h2 class="text-xl font-bold mb-3">Praktik Keamanan</h2>
    <ul class="space-y-2 list-disc pl-5 text-sm text-[hsl(var(--muted-foreground))]">
      <li>Penetration testing rutin oleh pihak ketiga independen.</li>
      <li>Pemantauan ancaman real-time dengan SIEM terintegrasi.</li>
      <li>Kebijakan akses prinsip hak minimum (least privilege).</li>
      <li>Backup harian dengan retention 90 hari.</li>
      <li>Incident response plan yang diuji secara berkala.</li>
      <li>Semua akses administratif dicatat dan diaudit.</li>
    </ul>
  </section>

  <section>
    <h2 class="text-xl font-bold mb-3">Laporan Kerentanan</h2>
    <p class="text-sm text-[hsl(var(--muted-foreground))]">
      Jika Anda menemukan kerentanan keamanan, laporkan ke <a href="mailto:security@kepin.id" class="text-[hsl(var(--primary))] hover:underline">security@kepin.id</a>. Kami berkomitmen merespon dalam 24 jam dan menangani temuan sesuai prioritas.
    </p>
  </section>
</div>
