<script lang="ts">
  import PageHeader from '$lib/components/layout/PageHeader.svelte';
  import DataTable from '$lib/components/data-display/DataTable.svelte';
  import MetricCard from '$lib/components/data-display/MetricCard.svelte';

  const subs = [
    { tenant: 'Toko Maju Jaya', plan: 'Premium', status: 'active', nextBilling: '2026-08-15', amount: 499000 },
    { tenant: 'Restoran Sederhana', plan: 'Basic', status: 'trial', nextBilling: '2026-08-01', amount: 0 },
    { tenant: 'Bengkel Motor Prima', plan: 'Premium', status: 'active', nextBilling: '2026-09-10', amount: 499000 },
  ];
</script>

<PageHeader title="Langganan" description="Paket dan pembayaran tenant" />

<div class="grid grid-cols-3 gap-4 mb-6">
  <MetricCard label="MRR" value={23400000} previousValue={21000000} />
  <MetricCard label="ARR" value={280800000} format="currency" />
  <MetricCard label="Aktif/Trial" value={48} format="number" />
</div>

<DataTable
  columns={[
    { key: 'tenant', label: 'Tenant', sortable: true },
    { key: 'plan', label: 'Paket' },
    { key: 'status', label: 'Status' },
    { key: 'nextBilling', label: 'Tagihan Berikutnya' },
    { key: 'amount', label: 'Jumlah', align: 'right', render: (item: any) => `Rp ${item.amount.toLocaleString('id-ID')}` },
  ]}
  data={subs}
  total={48}
/>
