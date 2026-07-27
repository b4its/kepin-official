<script lang="ts">
  import { transactions, accounts } from '$lib/stores/data';
  import PageHeader from '$lib/components/layout/PageHeader.svelte';
  import MetricCard from '$lib/components/data-display/MetricCard.svelte';
  import DateRangeFilter from '$lib/components/filters/DateRangeFilter.svelte';
  import BarChart from '$lib/components/charts/BarChart.svelte';
  import PieChart from '$lib/components/charts/PieChart.svelte';
  import type { Preset } from '$lib/utils/dateRange';
  import { Download } from '@lucide/svelte';
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

  const totalIncome = $derived(filtered.filter(t => t.type === 'income').reduce((s, t) => s + t.amount, 0));
  const totalExpense = $derived(filtered.filter(t => t.type === 'expense').reduce((s, t) => s + t.amount, 0));
  const cashBalance = $derived($accounts.find(a => a.code === '101')?.balance ?? 0);
  const totalAssets = $derived($accounts.filter(a => a.type === 'asset').reduce((s, a) => s + a.balance, 0));
  const totalLiabilities = $derived($accounts.filter(a => a.type === 'liability').reduce((s, a) => s + a.balance, 0));
  const equity = $derived($accounts.filter(a => a.type === 'equity').reduce((s, a) => s + a.balance, 0));

  const incomeByAccount = $derived(() => {
    const map: Record<string, number> = {};
    filtered.filter(t => t.type === 'income').forEach(t => { map[t.accountId] = (map[t.accountId] || 0) + t.amount; });
    return Object.entries(map).map(([id, val]) => ({ label: $accounts.find(a => a.id === id)?.name || id, value: val }));
  });

  const expenseByAccount = $derived(() => {
    const map: Record<string, number> = {};
    filtered.filter(t => t.type === 'expense').forEach(t => { map[t.accountId] = (map[t.accountId] || 0) + t.amount; });
    return Object.entries(map).map(([id, val]) => ({ label: $accounts.find(a => a.id === id)?.name || id, value: val }));
  });
</script>

<PageHeader title="Laporan Keuangan" description="Ringkasan keuangan periode ini">
  {#snippet actions()}
    <Button variant="secondary"><Download class="w-4 h-4" /> Export</Button>
  {/snippet}
</PageHeader>

<div class="mb-6">
  <DateRangeFilter onChange={onRangeChange} />
</div>

<div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
  <MetricCard label="Pendapatan" value={totalIncome} format="currency" />
  <MetricCard label="Beban" value={totalExpense} format="currency" />
  <MetricCard label="Laba Bersih" value={totalIncome - totalExpense} format="currency" />
  <MetricCard label="Saldo Kas" value={cashBalance} format="currency" />
</div>

<div class="grid lg:grid-cols-2 gap-6 mb-6">
  <div class="card p-5">
    <h3 class="font-semibold mb-4">Pendapatan vs Beban</h3>
    <BarChart labels={['Pendapatan', 'Beban', 'Laba']} datasets={[
      { label: 'Rp', data: [totalIncome, totalExpense, totalIncome - totalExpense], color: '#059669' },
    ]} height={220} yFormat="currency" />
  </div>
  <div class="card p-5">
    <h3 class="font-semibold mb-4">Neraca (Total)</h3>
    <BarChart labels={['Aset', 'Kewajiban', 'Ekuitas']} datasets={[
      { label: 'Rp', data: [totalAssets, totalLiabilities, equity], color: '#1559c7' },
    ]} height={220} yFormat="currency" />
  </div>
</div>

<div class="grid lg:grid-cols-2 gap-6">
  <div class="card p-5">
    <h3 class="font-semibold mb-4">Pendapatan per Akun</h3>
    {#if incomeByAccount().length > 0}
      <BarChart labels={incomeByAccount().map(i => i.label)} datasets={[
        { label: 'Pendapatan', data: incomeByAccount().map(i => i.value), color: '#059669' },
      ]} height={200} yFormat="currency" />
    {:else}
      <p class="text-sm text-[hsl(var(--muted-foreground))]">Tidak ada data pendapatan</p>
    {/if}
  </div>
  <div class="card p-5">
    <h3 class="font-semibold mb-4">Komposisi Beban</h3>
    {#if expenseByAccount().length > 0}
      <PieChart labels={expenseByAccount().map(e => e.label)} values={expenseByAccount().map(e => e.value)} height={200} donut={true} />
    {:else}
      <p class="text-sm text-[hsl(var(--muted-foreground))]">Tidak ada data beban</p>
    {/if}
  </div>
</div>
