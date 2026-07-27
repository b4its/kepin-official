<script lang="ts">
  import { transactions, accounts } from '$lib/stores/data';
  import PageHeader from '$lib/components/layout/PageHeader.svelte';
  import MetricCard from '$lib/components/data-display/MetricCard.svelte';
  import DataTable from '$lib/components/data-display/DataTable.svelte';
  import DateRangeFilter from '$lib/components/filters/DateRangeFilter.svelte';
  import BarChart from '$lib/components/charts/BarChart.svelte';
  import PieChart from '$lib/components/charts/PieChart.svelte';
  import type { Preset } from '$lib/utils/dateRange';
  import { TrendingUp, AlertTriangle, Activity } from '@lucide/svelte';

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
    account: accounts ? $accounts.find(a => a.id === t.accountId)?.name || t.accountId : t.accountId,
    amount: t.type === 'income' ? t.amount : -t.amount,
  })));

  const expenseLabels = ['Operasional', 'Stok', 'Gaji', 'Marketing', 'Lainnya'];
  const expenseValues = [8500000, 12000000, 5000000, 2800000, 1800000];
</script>

<PageHeader title="Dashboard" description="Toko Maju Jaya · Diperbarui: 2 menit lalu" />

<div class="mb-6">
  <DateRangeFilter onChange={onRangeChange} />
</div>

<div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
  <MetricCard label="Pendapatan" value={totalIncome} previousValue={totalIncome * 0.9} />
  <MetricCard label="Pengeluaran" value={totalExpense} previousValue={totalExpense * 0.9} />
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
      <div class="h-48 flex items-center justify-center text-sm text-[hsl(var(--muted-foreground))]">Tidak ada data</div>
    {/if}
  </div>
  <div class="space-y-3">
    <div class="card p-4">
      <h3 class="font-semibold mb-3">Komposisi Biaya</h3>
      <PieChart labels={expenseLabels} values={expenseValues} height={180} donut={true} />
    </div>
    <div class="card p-4">
      <div class="flex items-center gap-2 text-[var(--color-kepin-danger)] mb-2">
        <AlertTriangle class="w-4 h-4" />
        <span class="font-semibold text-sm">Alert</span>
      </div>
      <p class="text-sm">3 invoice jatuh tempo dalam 7 hari</p>
      <p class="text-sm mt-1">2 produk stok kritis</p>
    </div>
    <div class="card p-4">
      <div class="flex items-center gap-2 text-[var(--color-kepin-blue)] mb-2">
        <Activity class="w-4 h-4" />
        <span class="font-semibold text-sm">AI Insight</span>
      </div>
      <p class="text-sm">Penjualan diperkirakan naik 15% bulan depan</p>
      <p class="text-xs text-[hsl(var(--muted-foreground))] mt-1">Berdasarkan data 90 hari terakhir</p>
    </div>
    <div class="card p-4">
      <div class="flex items-center gap-2 text-[var(--color-kepin-green)] mb-2">
        <TrendingUp class="w-4 h-4" />
        <span class="font-semibold text-sm">Rekomendasi</span>
      </div>
      <p class="text-sm">Restock produk A & C dalam 3 hari</p>
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
