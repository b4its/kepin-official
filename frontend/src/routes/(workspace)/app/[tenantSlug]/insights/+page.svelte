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
    const map = new Map<string, number>();
    $transactions.filter(t => t.type === 'income').forEach(t => {
      const month = t.date.slice(0, 7);
      map.set(month, (map.get(month) || 0) + t.amount);
    });
    const sorted = [...map.entries()].sort((a, b) => a[0].localeCompare(b[0]));
    const labels = sorted.map(([m]) => {
      const d = new Date(m + '-01');
      return d.toLocaleDateString('id-ID', { month: 'short' });
    });
    const data = sorted.map(([, v]) => v);
    return { labels, data };
  });

  const leadingProduct = $derived(() => {
    return $transactions.filter(t => t.type === 'income').reduce((max, t) => t.amount > max.amount ? t : max, { amount: 0, description: '' } as any).description || '';
  });

  const totalIncomeAll = $derived($transactions.filter(t => t.type === 'income').reduce((s, t) => s + t.amount, 0));
  const insightData = $derived(() => {
    const list = [];
    if (totalIncomeAll > 0) {
      list.push({
        icon: TrendingUp, iconBg: 'bg-[var(--color-kepin-green)]',
        title: `Pendapatan ${filtered.length > 0 ? (totalIncome > totalExpense ? 'Melebihi' : 'Di Bawah') : '—'}`,
        desc: filtered.length > 0 ? `${totalIncome > totalExpense ? 'Laba' : 'Rugi bersih'} Rp ${Math.abs(totalIncome - totalExpense).toLocaleString('id-ID')} pada periode ini.` : 'Belum ada transaksi pada periode ini.',
        range: `Rp ${totalIncome.toLocaleString('id-ID')}`,
        confidence: 100, factors: `${$transactions.length} total transaksi tercatat`,
        cta: 'Lihat Laporan',
      });
    }
    if (monthlyIncome().data.length > 1) {
      const trend = monthlyIncome().data.slice(-1)[0] - monthlyIncome().data.slice(-2)[0];
      list.push({
        icon: trend > 0 ? TrendingUp : AlertTriangle, iconBg: trend > 0 ? 'bg-[var(--color-kepin-green)]' : 'bg-[var(--color-kepin-yellow)]',
        title: trend > 0 ? 'Pendapatan Meningkat' : 'Pendapatan Menurun',
        desc: `${trend > 0 ? 'Kenaikan' : 'Penurunan'} Rp ${Math.abs(trend).toLocaleString('id-ID')} dibanding bulan sebelumnya.`,
        range: trend > 0 ? `+Rp ${trend.toLocaleString('id-ID')}` : `-Rp ${Math.abs(trend).toLocaleString('id-ID')}`,
        confidence: 90, factors: `Data ${monthlyIncome().labels.length} bulan terakhir`,
        cta: 'Analisis Tren',
      });
    }
    return list;
  });

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
  {#if monthlyIncome().data.length > 0}
    <BarChart labels={monthlyIncome().labels} datasets={[
      { label: 'Pendapatan', data: monthlyIncome().data, color: '#059669' },
    ]} height={200} yFormat="currency" />
  {:else}
    <div class="h-48 flex items-center justify-center text-sm text-[hsl(var(--muted-foreground))]">Belum ada data pendapatan</div>
  {/if}
</div>

<div class="space-y-4">
  {#if insightData().length === 0}
    <div class="card p-5 text-center text-[hsl(var(--muted-foreground))]">
      <p>Belum cukup data untuk menghasilkan insight. Lakukan transaksi terlebih dahulu.</p>
    </div>
  {/if}
  {#each insightData() as insight}
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
