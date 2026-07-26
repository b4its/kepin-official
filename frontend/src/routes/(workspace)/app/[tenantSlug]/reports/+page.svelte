<script lang="ts">
  import PageHeader from '$lib/components/layout/PageHeader.svelte';
  import { FileText, BarChart3, TrendingUp, Download } from '@lucide/svelte';
  import Button from '$lib/components/ui/Button.svelte';

  const reportTypes = [
    { icon: BarChart3, name: 'Laba Rugi', desc: 'Pendapatan, beban, dan laba bersih periode berjalan' },
    { icon: FileText, name: 'Neraca', desc: 'Aset, kewajiban, dan ekuitas per tanggal tertentu' },
    { icon: TrendingUp, name: 'Arus Kas', desc: 'Arus kas dari operasi, investasi, dan pendanaan' },
    { icon: FileText, name: 'Buku Besar', desc: 'Riwayat transaksi per akun secara detail' },
    { icon: BarChart3, name: 'Aging Piutang', desc: 'Analisa umur piutang pelanggan' },
    { icon: BarChart3, name: 'Aging Utang', desc: 'Analisa umur utang pemasok' },
    { icon: TrendingUp, name: 'Penjualan', desc: 'Rekap penjualan per periode dan pelanggan' },
    { icon: TrendingUp, name: 'Pembelian', desc: 'Rekap pembelian per periode dan pemasok' },
    { icon: BarChart3, name: 'Stok', desc: 'Nilai, pergerakan, dan status stok terkini' },
  ];
</script>

<PageHeader title="Laporan Keuangan" description="Laporan akuntansi dan bisnis" breadcrumbs={[{ label: 'Laporan' }]}>
  {#snippet actions()}
    <Button variant="secondary">
      <Download class="w-4 h-4" /> Export
    </Button>
  {/snippet}
</PageHeader>

<div class="grid sm:grid-cols-2 lg:grid-cols-3 gap-4">
  {#each reportTypes as report}
    <div class="card-hover p-5 cursor-pointer">
      <report.icon class="w-6 h-6 text-[var(--color-kepin-blue)] mb-3" />
      <h3 class="font-semibold mb-1">{report.name}</h3>
      <p class="text-sm text-[hsl(var(--muted-foreground))]">{report.desc}</p>
    </div>
  {/each}
</div>
