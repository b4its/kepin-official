<script lang="ts">
  import { page } from '$app/stores';
  import PageHeader from '$lib/components/layout/PageHeader.svelte';
  import MetricCard from '$lib/components/data-display/MetricCard.svelte';
  import DataTable from '$lib/components/data-display/DataTable.svelte';
  import DateRangeFilter from '$lib/components/filters/DateRangeFilter.svelte';
  import BarChart from '$lib/components/charts/BarChart.svelte';
  import PieChart from '$lib/components/charts/PieChart.svelte';
  import Button from '$lib/components/ui/Button.svelte';
  import { tenantApi } from '$lib/stores/data';
  import type { Preset } from '$lib/utils/dateRange';
  import { RefreshCw } from '@lucide/svelte';

  type Dashboard = {
    metrics: { income: string; expense: string; grossProfit: string; cashBalance: string };
    cashFlow: { date: string; income: string; expense: string }[];
    cash_flow?: { date: string; income: string; expense: string }[];
    expenseComposition: { accountName: string; amount: string }[];
    expense_composition?: { accountName: string; amount: string }[];
    alerts: { type: string; message: string }[];
    recentTransactions: { id: string; date: string; description: string; amount: string; type: string; status: string }[];
    recent_transactions?: { id: string; date: string; description: string; amount: string; type: string; status: string }[];
  };

  const slug = $derived($page.params.tenantSlug || '');
  let startDate = $state('');
  let endDate = $state('');
  let dashboard = $state<Dashboard | null>(null);
  let loading = $state(false);
  let error = $state('');

  const income = $derived(number(dashboard?.metrics.income));
  const expense = $derived(number(dashboard?.metrics.expense));
  const profit = $derived(number(dashboard?.metrics.grossProfit));
  const cash = $derived(number(dashboard?.metrics.cashBalance));
  const cashFlow = $derived(dashboard?.cashFlow ?? dashboard?.cash_flow ?? []);
  const composition = $derived(dashboard?.expenseComposition ?? dashboard?.expense_composition ?? []);
  const recent = $derived(dashboard?.recentTransactions ?? dashboard?.recent_transactions ?? []);

  function number(value: string | number | undefined) {
    const parsed = Number(value ?? 0);
    return Number.isFinite(parsed) ? parsed : 0;
  }

  function onRangeChange(_preset: Preset, start: string, end: string) {
    startDate = start;
    endDate = end;
  }

  async function loadDashboard() {
    if (!slug || !startDate || !endDate) return;
    loading = true;
    error = '';
    try {
      dashboard = await tenantApi.getTenantDashboard(slug, { startDate, endDate }) as Dashboard;
    } catch (err: any) {
      error = err?.message || 'Gagal memuat dashboard';
    } finally {
      loading = false;
    }
  }

  $effect(() => {
    const now = new Date();
    const end = now.toISOString().slice(0, 10);
    const start = new Date(now.getTime() - 7 * 86400000).toISOString().slice(0, 10);
    if (!startDate) { startDate = start; endDate = end; }
  });

  $effect(() => { if (slug && startDate && endDate) void loadDashboard(); });
</script>

<PageHeader title="Dashboard" description={`${$page.params.tenantSlug || 'Workspace'} · data backend real-time`}>
  {#snippet actions()}
    <Button variant="secondary" onclick={loadDashboard} loading={loading}><RefreshCw class="w-4 h-4" /> Refresh</Button>
  {/snippet}
</PageHeader>

<div class="mb-6"><DateRangeFilter onChange={onRangeChange} /></div>
{#if error}<div class="mb-6 rounded-lg border border-red-200 bg-red-50 p-4 text-sm text-red-700">{error}</div>{/if}

<div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
  <MetricCard label="Pendapatan" value={income} loading={loading} format="currency" />
  <MetricCard label="Pengeluaran" value={expense} loading={loading} format="currency" />
  <MetricCard label="Laba Bersih" value={profit} loading={loading} format="currency" />
  <MetricCard label="Kas & Bank" value={cash} loading={loading} format="currency" />
</div>

<div class="grid lg:grid-cols-3 gap-6 mb-6">
  <div class="card p-5 lg:col-span-2">
    <h3 class="font-semibold mb-4">Arus Kas Harian</h3>
    <BarChart labels={cashFlow.map((row) => row.date.slice(5))} datasets={[
      { label: 'Pemasukan', data: cashFlow.map((row) => number(row.income)), color: '#059669' },
      { label: 'Pengeluaran', data: cashFlow.map((row) => number(row.expense)), color: '#dc2626' },
    ]} height={220} yFormat="currency" />
  </div>
  <div class="card p-5">
    <h3 class="font-semibold mb-4">Komposisi Beban</h3>
    {#if composition.length > 0}
      <PieChart labels={composition.map((row) => row.accountName)} values={composition.map((row) => number(row.amount))} height={190} donut={true} />
    {:else}
      <p class="text-sm text-[hsl(var(--muted-foreground))]">Belum ada beban posted pada periode ini.</p>
    {/if}
  </div>
</div>

{#if (dashboard?.alerts ?? []).length > 0}
  <div class="card p-5 mb-6">
    <h3 class="font-semibold mb-3">Perhatian</h3>
    <div class="space-y-2 text-sm">
      {#each dashboard?.alerts ?? [] as alert}
        <p>{alert.message}</p>
      {/each}
    </div>
  </div>
{/if}

<DataTable
  columns={[
    { key: 'date', label: 'Tanggal' },
    { key: 'description', label: 'Deskripsi' },
    { key: 'type', label: 'Tipe' },
    { key: 'amount', label: 'Jumlah', align: 'right', render: (r: any) => `Rp ${number(r.amount).toLocaleString('id-ID')}` },
    { key: 'status', label: 'Status' },
  ]}
  data={recent}
  total={recent.length}
  loading={loading}
  searchable={true}
/>
