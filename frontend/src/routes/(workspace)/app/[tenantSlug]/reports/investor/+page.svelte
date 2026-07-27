<script lang="ts">
  import { transactions, accounts } from '$lib/stores/data';
  import PageHeader from '$lib/components/layout/PageHeader.svelte';
  import MetricCard from '$lib/components/data-display/MetricCard.svelte';
  import DateRangeFilter from '$lib/components/filters/DateRangeFilter.svelte';
  import BarChart from '$lib/components/charts/BarChart.svelte';
  import PieChart from '$lib/components/charts/PieChart.svelte';
  import Button from '$lib/components/ui/Button.svelte';
  import type { Preset } from '$lib/utils/dateRange';
  import { Download, Share2 } from '@lucide/svelte';

  let startDate = $state('');
  let endDate = $state('');

  function onRangeChange(preset: Preset, start: string, end: string) {
    startDate = start;
    endDate = end;
  }

  $effect(() => {
    const now = new Date();
    const end = now.toISOString().slice(0, 10);
    const start = new Date(now.getTime() - 7 * 86400000).toISOString().slice(0, 10);
    if (!startDate) { startDate = start; endDate = end; }
  });

  const filtered = $derived(
    $transactions.filter(t => t.date >= startDate && t.date <= endDate)
  );

  const totalRevenue = $derived(filtered.filter(t => t.type === 'income').reduce((s, t) => s + t.amount, 0));
  const totalExpense = $derived(filtered.filter(t => t.type === 'expense').reduce((s, t) => s + t.amount, 0));
  const grossMargin = $derived(totalRevenue > 0 ? ((totalRevenue - totalExpense) / totalRevenue * 100) : 0);
  const cashBalance = $derived($accounts.find(a => a.code === '101')?.balance ?? 0);
  const burnRate = $derived(totalExpense);
  const runway = $derived(burnRate > 0 ? cashBalance / burnRate : 0);
</script>

<PageHeader title="Investor Report" description="Laporan untuk investor dan due diligence" breadcrumbs={[{ label: 'Laporan' }, { label: 'Investor' }]}>
  {#snippet actions()}
    <Button variant="secondary"><Share2 class="w-4 h-4" /> Bagikan</Button>
    <Button><Download class="w-4 h-4" /> Export PDF</Button>
  {/snippet}
</PageHeader>

<div class="mb-6">
  <DateRangeFilter onChange={onRangeChange} />
</div>

<div class="card p-5 mb-6">
  <h2 class="text-xl font-bold mb-1">Executive Summary</h2>
  <p class="text-sm text-[hsl(var(--muted-foreground))] mb-4">Periode: {startDate} s/d {endDate} | Dibuat: {new Date().toLocaleDateString('id-ID')}</p>
  <p class="text-sm leading-relaxed">
    Toko Maju Jaya mencatat pendapatan <strong>Rp {totalRevenue.toLocaleString('id-ID')}</strong> dengan beban <strong>Rp {totalExpense.toLocaleString('id-ID')}</strong> pada periode ini. Gross margin tercatat <strong>{grossMargin.toFixed(1)}%</strong>. Posisi kas tetap sehat dengan runway <strong>{runway.toFixed(1)} bulan</strong> pada burn rate saat ini.
  </p>
</div>

<div class="grid grid-cols-1 sm:grid-cols-3 lg:grid-cols-6 gap-4 mb-6">
  <MetricCard label="Pendapatan" value={totalRevenue} format="currency" />
  <MetricCard label="Gross Margin" value={grossMargin} previousValue={grossMargin * 0.95} format="percent" />
  <MetricCard label="Burn Rate" value={burnRate} format="currency" />
  <MetricCard label="Cash Position" value={cashBalance} format="currency" />
  <MetricCard label="Runway" value={runway} format="number" unit=" bulan" />
</div>

<div class="grid lg:grid-cols-2 gap-6">
  <div class="card p-5">
    <h3 class="font-semibold mb-4">Pendapatan vs Beban</h3>
    <BarChart labels={['Pendapatan', 'Beban', 'Laba']} datasets={[
      { label: 'Rp', data: [totalRevenue, totalExpense, totalRevenue - totalExpense], color: '#059669' },
    ]} height={220} yFormat="currency" />
  </div>
  <div class="card p-5">
    <h3 class="font-semibold mb-4">Komposisi Biaya</h3>
    <PieChart labels={['Operasional', 'Stok', 'Gaji', 'Marketing', 'Lainnya']} values={[8500000, 12000000, 5000000, 2800000, 1800000]} height={220} donut={true} />
  </div>
</div>
