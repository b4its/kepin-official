<script lang="ts">
  import PageHeader from '$lib/components/layout/PageHeader.svelte';
  import MetricCard from '$lib/components/data-display/MetricCard.svelte';
  import DataTable from '$lib/components/data-display/DataTable.svelte';
  import DateRangeFilter from '$lib/components/filters/DateRangeFilter.svelte';
  import BarChart from '$lib/components/charts/BarChart.svelte';
  import PieChart from '$lib/components/charts/PieChart.svelte';
  import type { Preset } from '$lib/utils/dateRange';
  import { adminTenants } from '$lib/stores/data';

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

  const recentTenants = $derived(
    $adminTenants.filter(t => t.createdAt.slice(0, 10) >= startDate && t.createdAt.slice(0, 10) <= endDate).slice(0, 10)
  );

  const activeCount = $derived($adminTenants.filter(t => t.status === 'active').length);
  const trialCount = $derived($adminTenants.filter(t => t.status === 'trial').length);
  const suspendedCount = $derived($adminTenants.filter(t => t.status === 'suspended').length);
  const mrr = $derived(activeCount * 500000 + trialCount * 99000);
</script>

<PageHeader title="Dashboard Admin" description="Ringkasan platform KePin" />

<div class="mb-6">
  <DateRangeFilter onChange={onRangeChange} />
</div>

<div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
  <MetricCard label="Tenant Aktif" value={activeCount} format="number" />
  <MetricCard label="Tenant Trial" value={trialCount} format="number" />
  <MetricCard label="Ditangguhkan" value={suspendedCount} format="number" previousValue={0} />
  <MetricCard label="MRR" value={mrr} previousValue={mrr * 0.9} />
</div>

<div class="grid lg:grid-cols-2 gap-6 mb-6">
  <div class="card p-5">
    <h3 class="font-semibold mb-4">Pertumbuhan Tenant</h3>
    <BarChart labels={['Feb', 'Mar', 'Apr', 'Mei', 'Jun', 'Jul']} datasets={[
      { label: 'Tenant Aktif', data: [28, 32, 36, 40, 44, activeCount], color: '#059669' },
      { label: 'Tenant Baru', data: [4, 4, 4, 4, 4, activeCount - 44], color: '#1559c7' },
    ]} height={200} />
  </div>
  <div class="card p-5">
    <h3 class="font-semibold mb-4">Distribusi Paket</h3>
    <PieChart labels={['Pro', 'Basic', 'Enterprise', 'Trial']} values={[activeCount - trialCount, Math.max(0, Math.floor(activeCount * 0.3)), Math.max(0, Math.floor(activeCount * 0.1)), trialCount]} height={200} donut={true} />
  </div>
</div>

<div class="card p-5 mb-6">
  <div class="flex items-center justify-between mb-4">
    <h2 class="font-semibold">Aktivitas Terbaru</h2>
  </div>
  <div class="space-y-2 text-sm">
    <div class="flex items-center justify-between py-1">
      <span>Tenant baru: <strong>Warung Sejahtera</strong> mendaftar Pro</span>
      <span class="text-xs text-[hsl(var(--muted-foreground))]">2 menit lalu</span>
    </div>
    <div class="flex items-center justify-between py-1">
      <span>Pembayaran gagal: <strong>PT ABC</strong> - kartu kedaluwarsa</span>
      <span class="text-xs text-[var(--color-kepin-danger)]">15 menit lalu</span>
    </div>
    <div class="flex items-center justify-between py-1">
      <span>Tenant <strong>Toko Maju</strong> mencapai 1.000 transaksi</span>
      <span class="text-xs text-[hsl(var(--muted-foreground))]">1 jam lalu</span>
    </div>
  </div>
</div>

<DataTable
  columns={[
    { key: 'name', label: 'Tenant', sortable: true },
    { key: 'plan', label: 'Paket' },
    { key: 'status', label: 'Status' },
    { key: 'createdAt', label: 'Dibuat' },
  ]}
  data={recentTenants}
  total={$adminTenants.length}
  pageSize={5}
  page={1}
  searchable={true}
/>
