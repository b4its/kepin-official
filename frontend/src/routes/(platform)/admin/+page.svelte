<script lang="ts">
  import PageHeader from '$lib/components/layout/PageHeader.svelte';
  import MetricCard from '$lib/components/data-display/MetricCard.svelte';
  import DataTable from '$lib/components/data-display/DataTable.svelte';
  import DateRangeFilter from '$lib/components/filters/DateRangeFilter.svelte';
  import BarChart from '$lib/components/charts/BarChart.svelte';
  import PieChart from '$lib/components/charts/PieChart.svelte';
  import Button from '$lib/components/ui/Button.svelte';
  import type { Preset } from '$lib/utils/dateRange';
  import { adminApi } from '$lib/stores/data';
  import { RefreshCw } from '@lucide/svelte';

  type Dashboard = {
    metrics: { activeTenants?: number; suspendedTenants?: number; mrr?: string };
    tenantGrowth: { date: string; count: number }[];
    tenant_growth?: { date: string; count: number }[];
    planDistribution: { plan: string; count: number; percentage: number }[];
    plan_distribution?: { plan: string; count: number; percentage: number }[];
    recentActivity: { id: string; timestamp: string | null; action: string; actorName?: string; tenantName?: string }[];
    recent_activity?: { id: string; timestamp: string | null; action: string; actorName?: string; tenantName?: string }[];
  };

  let startDate = $state('');
  let endDate = $state('');
  let dashboard = $state<Dashboard | null>(null);
  let loading = $state(false);
  let error = $state('');

  const growth = $derived(dashboard?.tenantGrowth ?? dashboard?.tenant_growth ?? []);
  const distribution = $derived(dashboard?.planDistribution ?? dashboard?.plan_distribution ?? []);
  const activity = $derived(dashboard?.recentActivity ?? dashboard?.recent_activity ?? []);
  const activeCount = $derived(Number(dashboard?.metrics?.activeTenants ?? 0));
  const suspendedCount = $derived(Number(dashboard?.metrics?.suspendedTenants ?? 0));
  const mrr = $derived(Number(dashboard?.metrics?.mrr ?? 0));
  const totalTenants = $derived(distribution.reduce((sum, row) => sum + Number(row.count || 0), 0));

  function onRangeChange(_preset: Preset, start: string, end: string) {
    startDate = start;
    endDate = end;
  }

  async function loadDashboard() {
    loading = true;
    error = '';
    const params = startDate && endDate ? `?startDate=${startDate}&endDate=${endDate}` : '';
    try {
      dashboard = await adminApi.getAdminDashboard(params) as Dashboard;
    } catch (err: any) {
      error = err?.message || 'Gagal memuat dashboard platform';
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

  $effect(() => { if (startDate && endDate) void loadDashboard(); });
</script>

<PageHeader title="Dashboard Admin" description="Ringkasan platform dari backend">
  {#snippet actions()}
    <Button variant="secondary" onclick={loadDashboard} loading={loading}><RefreshCw class="w-4 h-4" /> Refresh</Button>
  {/snippet}
</PageHeader>

<div class="mb-6">
  <DateRangeFilter onChange={onRangeChange} />
</div>

{#if error}
  <div class="mb-6 rounded-lg border border-red-200 bg-red-50 p-4 text-sm text-red-700">{error}</div>
{/if}

<div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
  <MetricCard label="Tenant Aktif" value={activeCount} loading={loading} format="number" />
  <MetricCard label="Total Tenant" value={totalTenants} loading={loading} format="number" />
  <MetricCard label="Ditangguhkan" value={suspendedCount} loading={loading} format="number" />
  <MetricCard label="MRR" value={mrr} loading={loading} format="currency" />
</div>

<div class="grid lg:grid-cols-2 gap-6 mb-6">
  <div class="card p-5">
    <h3 class="font-semibold mb-4">Pertumbuhan Tenant</h3>
    <BarChart labels={growth.map((row) => row.date.slice(5))} datasets={[
      { label: 'Tenant Baru', data: growth.map((row) => Number(row.count || 0)), color: '#1559c7' },
    ]} height={200} />
  </div>
  <div class="card p-5">
    <h3 class="font-semibold mb-4">Distribusi Status/Paket</h3>
    {#if distribution.length > 0}
      <PieChart labels={distribution.map((row) => row.plan)} values={distribution.map((row) => Number(row.count || 0))} height={200} donut={true} />
    {:else}
      <p class="text-sm text-[hsl(var(--muted-foreground))]">Belum ada data distribusi.</p>
    {/if}
  </div>
</div>

<DataTable
  columns={[
    { key: 'timestamp', label: 'Waktu', render: (r: any) => r.timestamp || '-' },
    { key: 'action', label: 'Aksi' },
    { key: 'actorName', label: 'Actor', render: (r: any) => r.actorName || r.tenantName || '-' },
  ]}
  data={activity}
  total={activity.length}
  pageSize={10}
  loading={loading}
  searchable={true}
/>
