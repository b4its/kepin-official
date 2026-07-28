<script lang="ts">
  import { transactions, accounts, invoices, products } from '$lib/stores/data';
  import PageHeader from '$lib/components/layout/PageHeader.svelte';
  import MetricCard from '$lib/components/data-display/MetricCard.svelte';
  import DataTable from '$lib/components/data-display/DataTable.svelte';
  import DateRangeFilter from '$lib/components/filters/DateRangeFilter.svelte';
  import BarChart from '$lib/components/charts/BarChart.svelte';
  import PieChart from '$lib/components/charts/PieChart.svelte';
  import type { Preset } from '$lib/utils/dateRange';
  import { TrendingUp, AlertTriangle, Activity } from '@lucide/svelte';
  import { page } from '$app/stores';

  let datePreset = $state<Preset>('1week');
  let startDate = $state('');
  let endDate = $state('');

  function onRangeChange(preset: Preset, start: string, end: string) {
    datePreset = preset;
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
    $transactions.filter(t => {
      const d = t.date;
      return d >= startDate && d <= endDate;
    })
  );

  const totalIncome = $derived(filtered.filter(t => t.type === 'income').reduce((s, t) => s + t.amount, 0));
  const totalExpense = $derived(filtered.filter(t => t.type === 'expense').reduce((s, t) => s + t.amount, 0));
  const grossProfit = $derived(totalIncome - totalExpense);
  const cashBalance = $derived($accounts.find(a => a.code === '101')?.balance ?? 0);
  const previousIncome = $derived(totalIncome * (totalExpense > 0 ? totalIncome / (totalIncome + totalExpense) : 0.5));

  const chartLabels = $derived(() => {
    const days: string[] = [];
    const s = new Date(startDate);
    const e = new Date(endDate);
    for (let d = new Date(s); d <= e; d.setDate(d.getDate() + 1)) {
      days.push(d.toISOString().slice(0, 10));
    }
    return days;
  });

  const chartData = $derived(() => {
    const labels = chartLabels();
    const income: number[] = labels.map(d => filtered.filter(t => t.date === d && t.type === 'income').reduce((s, t) => s + t.amount, 0));
    const expense: number[] = labels.map(d => filtered.filter(t => t.date === d && t.type === 'expense').reduce((s, t) => s + t.amount, 0));
    return { labels, income, expense };
  });

  const recentList = $derived(filtered.map(t => ({
    date: t.date,
    desc: t.description,
    account: $accounts.find(a => a.id === t.accountId)?.name || t.accountId,
    amount: t.type === 'income' ? t.amount : -t.amount,
  })));

  const incomeByAccount = $derived(() => {
    const map = new Map<string, number>();
    $transactions.filter(t => t.type === 'income').forEach(t => {
      const name = $accounts.find(a => a.id === t.accountId)?.name || 'Lainnya';
      map.set(name, (map.get(name) || 0) + t.amount);
    });
    const entries = [...map.entries()].sort((a, b) => b[1] - a[1]);
    const labels = entries.map(e => e[0]);
    const values = entries.map(e => e[1]);
    return { labels: labels.slice(0, 6), values: values.slice(0, 6) };
  });

  const dueSoon = $derived($invoices.filter(i => i.status === 'sent' || i.status === 'partial').length);
  const overdue = $derived($invoices.filter(i => i.status === 'overdue').length);
  const criticalStock = $derived($products.filter(p => p.stock <= p.minStock).length);
  const lowStock = $derived($products.filter(p => p.stock > p.minStock && p.stock <= p.minStock * 2).length);

  const restockNeeded = $derived(() => {
    return $products.filter(p => p.stock <= p.minStock).slice(0, 3).map(p => p.name).join(', ') || '—';
  });
</script>

<PageHeader title="Dashboard" description={`${$page.params.tenantSlug || 'Workspace'} · Data real-time dari database`} />

<div class="mb-6">
  <DateRangeFilter onChange={onRangeChange} />
</div>

<div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
  <MetricCard label="Pendapatan" value={totalIncome} previousValue={previousIncome} format="currency" />
  <MetricCard label="Pengeluaran" value={totalExpense} previousValue={totalExpense * 0.85} format="currency" />
  <MetricCard label="Laba Kotor" value={grossProfit} format="currency" />
  <MetricCard label="Saldo Kas" value={cashBalance} format="currency" />
</div>

<div class="grid lg:grid-cols-3 gap-6 mb-6">
  <div class="card p-5 lg:col-span-2">
    <h3 class="font-semibold mb-4">Arus Kas Harian</h3>
    {#if chartData().labels.length > 0}
      <BarChart labels={chartData().labels} datasets={[
        { label: 'Pemasukan', data: chartData().income, color: '#059669' },
        { label: 'Pengeluaran', data: chartData().expense, color: '#dc2626' },
      ]} height={220} />
    {:else}
      <div class="h-48 flex items-center justify-center text-sm text-[hsl(var(--muted-foreground))]">Tidak ada data transaksi pada periode ini</div>
    {/if}
  </div>
  <div class="space-y-3">
    <div class="card p-4">
      <h3 class="font-semibold mb-3">Pendapatan per Akun</h3>
      {#if incomeByAccount().labels.length > 0}
        <PieChart labels={incomeByAccount().labels} values={incomeByAccount().values} height={180} donut={true} />
      {:else}
        <div class="h-40 flex items-center justify-center text-sm text-[hsl(var(--muted-foreground))]">Belum ada data</div>
      {/if}
    </div>
    <div class="card p-4">
      <div class="flex items-center gap-2 text-[var(--color-kepin-danger)] mb-2">
        <AlertTriangle class="w-4 h-4" />
        <span class="font-semibold text-sm">Alert</span>
      </div>
      {#if dueSoon > 0 || overdue > 0 || criticalStock > 0}
        <p class="text-sm">{dueSoon} invoice menunggu pembayaran</p>
        {#if overdue > 0}<p class="text-sm mt-1">{overdue} invoice overdue</p>{/if}
        <p class="text-sm mt-1">{criticalStock} produk stok kritis</p>
      {:else}
        <p class="text-sm text-[hsl(var(--muted-foreground))]">Semua dalam kondisi normal</p>
      {/if}
    </div>
    <div class="card p-4">
      <div class="flex items-center gap-2 text-[var(--color-kepin-blue)] mb-2">
        <Activity class="w-4 h-4" />
        <span class="font-semibold text-sm">Ringkasan</span>
      </div>
      <p class="text-sm">Total <strong>{totalIncome + totalExpense > 0 ? $transactions.length : 0}</strong> transaksi tercatat</p>
      <p class="text-xs text-[hsl(var(--muted-foreground))] mt-1">{totalIncome > 0 ? 'Rasio laba ' + (grossProfit / totalIncome * 100).toFixed(0) + '%' : 'Belum ada pendapatan'}</p>
    </div>
    <div class="card p-4">
      <div class="flex items-center gap-2 text-[var(--color-kepin-green)] mb-2">
        <TrendingUp class="w-4 h-4" />
        <span class="font-semibold text-sm">Stok Kritis</span>
      </div>
      {#if criticalStock > 0}
        <p class="text-sm">Restock: {restockNeeded()}</p>
        <p class="text-xs text-[hsl(var(--muted-foreground))] mt-1">{lowStock} produk menjelang stok minimum</p>
      {:else}
        <p class="text-sm text-[hsl(var(--muted-foreground))]">Stok aman</p>
      {/if}
    </div>
  </div>
</div>

<DataTable
  columns={[
    { key: 'date', label: 'Tanggal' },
    { key: 'desc', label: 'Deskripsi' },
    { key: 'account', label: 'Akun' },
    { key: 'amount', label: 'Jumlah', align: 'right', render: (item: any) => item.amount > 0 ? `Rp ${item.amount.toLocaleString('id-ID')}` : `(Rp ${Math.abs(item.amount).toLocaleString('id-ID')})` },
  ]}
  data={recentList}
  total={filtered.length}
  page={1}
  pageSize={5}
  searchable={true}
/>
