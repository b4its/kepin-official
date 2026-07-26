<script lang="ts">
  import PageHeader from '$lib/components/layout/PageHeader.svelte';
  import MetricCard from '$lib/components/data-display/MetricCard.svelte';
  import Button from '$lib/components/ui/Button.svelte';
  import { Download, Share2, TrendingUp, BarChart3 } from '@lucide/svelte';

  type MetricFormat = 'currency' | 'number' | 'percent';

  const metrics: { label: string; value: number; prev?: number; format: MetricFormat; unit?: string }[] = [
    { label: 'Pendapatan', value: 45200000, prev: 38900000, format: 'currency' },
    { label: 'Gross Margin', value: 37.8, prev: 32.1, format: 'percent' },
    { label: 'Burn Rate', value: 28100000, format: 'currency' },
    { label: 'Cash Position', value: 45300000, format: 'currency' },
    { label: 'Runway', value: 1.6, format: 'number', unit: ' bulan' },
    { label: 'ARPU', value: 3750000, format: 'currency' },
  ];
</script>

<PageHeader title="Investor Report" description="Laporan untuk investor dan due diligence" breadcrumbs={[{ label: 'Laporan' }, { label: 'Investor' }]}>
  {#snippet actions()}
    <Button variant="secondary">
      <Share2 class="w-4 h-4" /> Bagikan
    </Button>
    <Button>
      <Download class="w-4 h-4" /> Export PDF
    </Button>
  {/snippet}
</PageHeader>

<div class="card p-5 mb-6">
  <h2 class="text-xl font-bold mb-1">Executive Summary</h2>
  <p class="text-sm text-[hsl(var(--muted-foreground))] mb-4">Periode: Juli 2026 | Dibuat: 25 Jul 2026</p>
  <p class="text-sm leading-relaxed">
    Toko Maju Jaya menunjukkan pertumbuhan pendapatan yang solid sebesar 16.2% dibandingkan periode sebelumnya, didorong oleh peningkatan penjualan online dan perluasan lini produk. Gross margin meningkat 5.7 poin persentase berkat optimalisasi rantai pasok. Posisi kas tetap sehat dengan runway lebih dari 1.5 bulan pada burn rate saat ini.
  </p>
</div>

<div class="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-4 mb-6">
  {#each metrics as m}
    <MetricCard label={m.label} value={m.value as number} previousValue={m.prev} format={m.format} unit={m.unit} />
  {/each}
</div>

<div class="grid lg:grid-cols-2 gap-6">
  <div class="card p-5">
    <h3 class="font-semibold mb-4">Tren Pendapatan (6 Bulan)</h3>
    <div class="h-48 bg-[hsl(var(--muted))] rounded flex items-center justify-center">
      <TrendingUp class="w-8 h-8 text-[hsl(var(--muted-foreground))]" />
    </div>
  </div>
  <div class="card p-5">
    <h3 class="font-semibold mb-4">Komposisi Biaya</h3>
    <div class="h-48 bg-[hsl(var(--muted))] rounded flex items-center justify-center">
      <BarChart3 class="w-8 h-8 text-[hsl(var(--muted-foreground))]" />
    </div>
  </div>
</div>
