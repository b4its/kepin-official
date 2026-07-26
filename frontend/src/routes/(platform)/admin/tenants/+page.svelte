<script lang="ts">
  import PageHeader from '$lib/components/layout/PageHeader.svelte';
  import DataTable from '$lib/components/data-display/DataTable.svelte';
  import StatusBadge from '$lib/components/data-display/StatusBadge.svelte';

  const tenants = [
    { id: '1', name: 'Toko Maju Jaya', owner: 'Budi Santoso', plan: 'Premium', status: 'active', users: 5 },
    { id: '2', name: 'Restoran Sederhana', owner: 'Siti Rahayu', plan: 'Basic', status: 'trial', users: 2 },
    { id: '3', name: 'Bengkel Motor Prima', owner: 'Agus Wijaya', plan: 'Premium', status: 'active', users: 4 },
  ];
</script>

<PageHeader title="Manajemen Tenant" description="Kelola seluruh organisasi pelanggan" />

<DataTable
  columns={[
    { key: 'name', label: 'Nama', sortable: true },
    { key: 'owner', label: 'Pemilik' },
    { key: 'plan', label: 'Paket' },
    { key: 'users', label: 'Pengguna', align: 'right' },
    { key: 'status', label: 'Status', render: (item: any) => `<span class="badge-${item.status}">${item.status}</span>` },
  ]}
  data={tenants}
  total={48}
/>
