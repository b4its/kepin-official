<script lang="ts">
  import PageHeader from '$lib/components/layout/PageHeader.svelte';
  import MetricCard from '$lib/components/data-display/MetricCard.svelte';
  import DataTable from '$lib/components/data-display/DataTable.svelte';

  const recentTenants = [
    { name: 'Toko Maju Jaya', plan: 'Premium', status: 'active', users: 5, created: '2026-01-15' },
    { name: 'Restoran Sederhana', plan: 'Basic', status: 'trial', users: 2, created: '2026-07-20' },
    { name: 'Bengkel Motor Prima', plan: 'Premium', status: 'active', users: 4, created: '2026-03-10' },
  ];
</script>

<PageHeader title="Dashboard Admin" description="Ringkasan platform KePin" />

<div class="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
  <MetricCard label="Tenant Aktif" value={48} format="number" />
  <MetricCard label="Tenant Trial" value={12} format="number" />
  <MetricCard label="Churn Rate" value={3.2} format="percent" previousValue={4.1} />
  <MetricCard label="MRR" value={23400000} previousValue={21000000} />
</div>

<div class="card p-5 mb-6">
  <div class="flex items-center justify-between mb-4">
    <h2 class="font-semibold">Aktivitas Terbaru</h2>
  </div>
  <div class="space-y-2 text-sm">
    <div class="flex items-center justify-between py-1">
      <span>Tenant baru: <strong>Warung Sejahtera</strong> mendaftar Premium</span>
      <span class="text-xs text-[hsl(var(--muted-foreground))]">2 menit lalu</span>
    </div>
    <div class="flex items-center justify-between py-1">
      <span>Pembayaran gagal: <strong>PT ABC</strong> - kartu kedaluwarsa</span>
      <span class="text-xs text-[hsl(var(--muted-foreground))] var(--color-kepin-red)]">15 menit lalu</span>
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
    { key: 'users', label: 'Pengguna', align: 'right' },
    { key: 'created', label: 'Dibuat' },
  ]}
  data={recentTenants}
  total={48}
  pageSize={10}
  page={1}
/>
