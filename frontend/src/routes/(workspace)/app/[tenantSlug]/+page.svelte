<script lang="ts">
  import { page } from '$app/stores';
  import PageHeader from '$lib/components/layout/PageHeader.svelte';
  import MetricCard from '$lib/components/data-display/MetricCard.svelte';
  import DataTable from '$lib/components/data-display/DataTable.svelte';
  import DateRangeFilter from '$lib/components/filters/DateRangeFilter.svelte';
  import BarChart from '$lib/components/charts/BarChart.svelte';
  import PieChart from '$lib/components/charts/PieChart.svelte';
  import Button from '$lib/components/ui/Button.svelte';
  import { api } from '$lib/api/client';
  import { tenantApi } from '$lib/stores/data';
  import { formatIDR } from '$lib/utils/currency';
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

  type AgingReport = {
    buckets: Record<string, { label: string; total: string; items: unknown[] }>;
    grandTotal: string;
  };

  const AGING_BUCKETS = [
    { key: 'current', label: 'Lancar' },
    { key: '1_30', label: '1-30' },
    { key: '31_60', label: '31-60' },
    { key: '61_90', label: '61-90' },
    { key: '90_plus', label: '>90' },
  ];

  const slug = $derived($page.params.tenantSlug || '');
  let startDate = $state('');
  let endDate = $state('');
  let dashboard = $state<Dashboard | null>(null);
  let loading = $state(false);
  let error = $state('');
  let compareMode = $state(false);
  let compareStart = $state('');
  let compareEnd = $state('');
  let compareDashboard = $state<Dashboard | null>(null);
  let compareLoading = $state(false);
  let receivableAging = $state<AgingReport | null>(null);
  let payableAging = $state<AgingReport | null>(null);

  const income = $derived(number(dashboard?.metrics.income));
  const expense = $derived(number(dashboard?.metrics.expense));
  const profit = $derived(number(dashboard?.metrics.grossProfit));
  const cash = $derived(number(dashboard?.metrics.cashBalance));
  const compareIncome = $derived(compareMode ? number(compareDashboard?.metrics.income) : null);
  const compareExpense = $derived(compareMode ? number(compareDashboard?.metrics.expense) : null);
  const compareProfit = $derived(compareMode ? number(compareDashboard?.metrics.grossProfit) : null);
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

  function defaultCompareRange() {
    if (!startDate || !endDate) return;
    const span = new Date(`${endDate}T00:00:00`).getTime() - new Date(`${startDate}T00:00:00`).getTime();
    const cEnd = new Date(`${startDate}T00:00:00`).getTime() - 86400000;
    compareStart = new Date(cEnd - span).toISOString().slice(0, 10);
    compareEnd = new Date(cEnd).toISOString().slice(0, 10);
  }

  function toggleCompare() {
    compareMode = !compareMode;
    if (compareMode) defaultCompareRange();
  }

  async function loadCompare() {
    if (!slug || !compareStart || !compareEnd) return;
    compareLoading = true;
    try {
      compareDashboard = await tenantApi.getTenantDashboard(slug, { startDate: compareStart, endDate: compareEnd }) as Dashboard;
    } catch {
      compareDashboard = null;
    } finally {
      compareLoading = false;
    }
  }

  async function loadDashboard() {
    if (!slug || !startDate || !endDate) return;
    loading = true;
    error = '';
    try {
      const [dash, ar, ap] = await Promise.all([
        tenantApi.getTenantDashboard(slug, { startDate, endDate }) as Promise<Dashboard>,
        api<AgingReport>(`/tenants/${slug}/reports/receivable-aging`).catch(() => null),
        api<AgingReport>(`/tenants/${slug}/reports/payable-aging`).catch(() => null),
      ]);
      dashboard = dash;
      receivableAging = ar;
      payableAging = ap;
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
  $effect(() => {
    if (slug && compareMode && compareStart && compareEnd) {
      void loadCompare();
    }
  });
</script>

<PageHeader title="Dashboard" description={`${$page.params.tenantSlug || 'Workspace'} · data backend real-time`}>
  {#snippet actions()}
    <Button variant="secondary" onclick={loadDashboard} loading={loading}><RefreshCw class="w-4 h-4" /> Refresh</Button>
  {/snippet}
</PageHeader>

<div class="mb-6"><DateRangeFilter onChange={onRangeChange} /></div>
{#if error}<div class="mb-6 rounded-lg border border-red-200 bg-red-50 p-4 text-sm text-red-700">{error}</div>{/if}

<div class="card mb-4 flex flex-wrap items-center gap-x-5 gap-y-2 p-4">
  <label class="flex cursor-pointer items-center gap-2 text-sm font-medium">
    <input type="checkbox" checked={compareMode} onclick={toggleCompare} class="h-4 w-4" />
    Bandingkan dengan periode sebelumnya
  </label>
  {#if compareMode}
    <div class="flex flex-wrap items-center gap-2 text-sm text-[hsl(var(--muted-foreground))]">
      <span>Periode pembanding:</span>
      <input type="date" bind:value={compareStart} class="input-field" aria-label="Tanggal mulai pembanding" />
      <span>s.d.</span>
      <input type="date" bind:value={compareEnd} class="input-field" aria-label="Tanggal akhir pembanding" />
    </div>
    <button class="text-xs text-[hsl(var(--primary))] hover:underline" onclick={defaultCompareRange}>← Periode sebelumnya</button>
    {#if compareLoading}<span class="text-xs text-[hsl(var(--muted-foreground))]">Memuat…</span>{/if}
  {/if}
</div>

<div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-6" data-tour="metric-cards">
  <MetricCard label="Pendapatan" value={income} previousValue={compareMode ? compareIncome : undefined} loading={loading} format="currency" />
  <MetricCard label="Pengeluaran" value={expense} previousValue={compareMode ? compareExpense : undefined} loading={loading} format="currency" />
  <MetricCard label="Laba Bersih" value={profit} previousValue={compareMode ? compareProfit : undefined} loading={loading} format="currency" />
  <MetricCard label="Kas & Bank" value={cash} loading={loading} format="currency" />
</div>

<div class="grid lg:grid-cols-2 gap-6 mb-6">
  <div class="card p-5">
    <div class="mb-3 flex items-center justify-between">
      <h3 class="font-semibold">Piutang Usaha</h3>
      <a href={`/app/${slug}/reports?tab=aging`} class="text-xs text-[hsl(var(--primary))] hover:underline">Lihat laporan →</a>
    </div>
    {#if receivableAging}
      <p class="mb-3 text-2xl font-semibold tabular-nums">{formatIDR(Number(receivableAging.grandTotal))}</p>
      <div class="space-y-2">
        {#each AGING_BUCKETS as b}
          <div class="flex items-center justify-between text-sm">
            <span class="text-[hsl(var(--muted-foreground))]">{b.label}</span>
            <span class="font-medium tabular-nums">{formatIDR(Number(receivableAging.buckets[b.key]?.total ?? 0))}</span>
          </div>
        {/each}
      </div>
    {:else if loading}
      <p class="text-sm text-[hsl(var(--muted-foreground))]">Memuat…</p>
    {:else}
      <p class="text-sm text-[hsl(var(--muted-foreground))]">Belum ada piutang.</p>
    {/if}
  </div>
  <div class="card p-5">
    <div class="mb-3 flex items-center justify-between">
      <h3 class="font-semibold">Hutang Usaha</h3>
      <a href={`/app/${slug}/reports?tab=aging`} class="text-xs text-[hsl(var(--primary))] hover:underline">Lihat laporan →</a>
    </div>
    {#if payableAging}
      <p class="mb-3 text-2xl font-semibold tabular-nums">{formatIDR(Number(payableAging.grandTotal))}</p>
      <div class="space-y-2">
        {#each AGING_BUCKETS as b}
          <div class="flex items-center justify-between text-sm">
            <span class="text-[hsl(var(--muted-foreground))]">{b.label}</span>
            <span class="font-medium tabular-nums">{formatIDR(Number(payableAging.buckets[b.key]?.total ?? 0))}</span>
          </div>
        {/each}
      </div>
    {:else if loading}
      <p class="text-sm text-[hsl(var(--muted-foreground))]">Memuat…</p>
    {:else}
      <p class="text-sm text-[hsl(var(--muted-foreground))]">Belum ada hutang.</p>
    {/if}
  </div>
</div>

<div class="grid lg:grid-cols-3 gap-6 mb-6" data-tour="dashboard-charts">
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
