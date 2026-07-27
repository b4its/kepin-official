<script lang="ts">
  import { transactions } from '$lib/stores/data';
  import PageHeader from '$lib/components/layout/PageHeader.svelte';
  import MetricCard from '$lib/components/data-display/MetricCard.svelte';
  import DateRangeFilter from '$lib/components/filters/DateRangeFilter.svelte';
  import BarChart from '$lib/components/charts/BarChart.svelte';
  import type { Preset } from '$lib/utils/dateRange';
  import { Activity, TrendingUp, AlertTriangle, Lightbulb } from '@lucide/svelte';
  import Button from '$lib/components/ui/Button.svelte';

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

  const monthlyIncome = $derived(() => {
    const months = ['Feb', 'Mar', 'Apr', 'Mei', 'Jun', 'Jul'];
    const data = [32000000, 35000000, 38000000, 41000000, 45000000, 45200000];
    return { labels: months, data };
  });

  const insights = [
    {
      icon: TrendingUp,
      iconBg: 'bg-[var(--color-kepin-green)]',
      title: 'Penjualan Diprediksi Naik 15%',
      desc: 'Berdasarkan tren 90 hari terakhir dan pola musiman, penjualan bulan depan diperkirakan mencapai Rp 52 juta.',
      range: 'Rp 48-56 Juta',
      confidence: 85,
      factors: 'Meningkatnya penjualan online, musim liburan',
      cta: 'Lihat Detail Penjualan',
    },
    {
      icon: AlertTriangle,
      iconBg: 'bg-[var(--color-kepin-yellow)]',
      title: 'Stok Menipis, Segera Restock',
      desc: 'Produk B diperkirakan habis dalam 6 hari berdasarkan rata-rata penjualan harian.',
      range: '6 hari',
      confidence: 78,
      factors: 'Penjualan meningkat 25%, lead time supplier 4 hari',
      cta: 'Buat Purchase Order',
    },
    {
      icon: Lightbulb,
      iconBg: 'bg-[var(--color-kepin-blue)]',
      title: 'Optimasi Margin Produk A',
      desc: 'Menaikkan harga produk A sebesar 10% berpotensi meningkatkan laba kotor hingga Rp 3 juta/bulan tanpa menurunkan permintaan signifikan.',
      range: '+Rp 3 Juta/bulan',
      confidence: 72,
      factors: 'Harga kompetitor 15% lebih tinggi, elastisitas permintaan rendah',
      cta: 'Analisis Harga',
    },
  ];

  const totalIncome = $derived(filtered.filter(t => t.type === 'income').reduce((s, t) => s + t.amount, 0));
  const totalExpense = $derived(filtered.filter(t => t.type === 'expense').reduce((s, t) => s + t.amount, 0));
</script>

<PageHeader title="AI Insight" description="Rekomendasi dan prediksi bisnis berbasis AI" breadcrumbs={[{ label: 'AI Insight' }]} />

<div class="mb-6">
  <DateRangeFilter onChange={onRangeChange} />
</div>

<div class="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-6">
  <MetricCard label="Pendapatan Periode Ini" value={totalIncome} format="currency" />
  <MetricCard label="Beban Periode Ini" value={totalExpense} format="currency" />
  <MetricCard label="Transaksi" value={filtered.length} format="number" />
</div>

<div class="card p-5 mb-6">
  <h3 class="font-semibold mb-4">Tren Pendapatan (6 Bulan)</h3>
  <BarChart labels={monthlyIncome().labels} datasets={[
    { label: 'Pendapatan', data: monthlyIncome().data, color: '#059669' },
  ]} height={200} yFormat="currency" />
  <p class="text-xs text-[hsl(var(--muted-foreground))] mt-2">Prediksi bulan depan: <strong class="text-[var(--color-kepin-green)]">Rp 48-56 Juta</strong> (naik 6-15%)</p>
</div>

<div class="space-y-4">
  {#each insights as insight}
    <div class="card p-5">
      <div class="flex items-start gap-4">
        <div class="w-10 h-10 {insight.iconBg} rounded flex items-center justify-center shrink-0">
          <insight.icon class="w-5 h-5 text-white" />
        </div>
        <div class="flex-1 min-w-0">
          <div class="flex items-start justify-between gap-2">
            <h3 class="font-semibold">{insight.title}</h3>
            <span class="text-xs text-[hsl(var(--muted-foreground))] shrink-0">Confidence: {insight.confidence}%</span>
          </div>
          <p class="text-sm text-[hsl(var(--muted-foreground))] mt-1">{insight.desc}</p>
          <div class="flex flex-wrap gap-4 mt-2 text-xs text-[hsl(var(--muted-foreground))]">
            <span>Rentang: <strong>{insight.range}</strong></span>
            <span>Faktor: <strong>{insight.factors}</strong></span>
          </div>
          <div class="mt-3">
            <Button variant="ghost" size="sm">{insight.cta}</Button>
          </div>
        </div>
      </div>
    </div>
  {/each}
</div>
