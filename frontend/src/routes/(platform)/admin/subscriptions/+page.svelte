<script lang="ts">
  import PageHeader from '$lib/components/layout/PageHeader.svelte';
  import DataTable from '$lib/components/data-display/DataTable.svelte';
  import MetricCard from '$lib/components/data-display/MetricCard.svelte';
  import { adminTenants } from '$lib/stores/data';
</script>

<PageHeader title="Langganan" description="Paket dan pembayaran tenant" />

<div class="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-6">
  <MetricCard label="MRR" value={23400000} previousValue={21000000} />
  <MetricCard label="ARR" value={280800000} format="currency" />
  <MetricCard label="Aktif/Trial" value={48} format="number" />
</div>

<DataTable
  columns={[
    { key: 'name', label: 'Tenant', sortable: true },
    { key: 'plan', label: 'Paket' },
    { key: 'status', label: 'Status' },
    { key: 'createdAt', label: 'Bergabung' },
    { key: 'sector', label: 'Sektor' },
  ]}
  data={$adminTenants}
  total={$adminTenants.length}
  searchable={true}
/>
