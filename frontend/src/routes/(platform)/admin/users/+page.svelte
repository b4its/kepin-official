<script lang="ts">
  import PageHeader from '$lib/components/layout/PageHeader.svelte';
  import DataTable from '$lib/components/data-display/DataTable.svelte';

  const users = [
    { name: 'Budi Santoso', email: 'budi@tokomaju.com', role: 'Owner', status: 'active', mfa: true },
    { name: 'Ani Lestari', email: 'ani@tokomaju.com', role: 'Admin', status: 'active', mfa: true },
    { name: 'Dedi Kurniawan', email: 'dedi@tokomaju.com', role: 'Staff', status: 'active', mfa: false },
  ];
</script>

<PageHeader title="Manajemen Pengguna" description="Kelola pengguna platform" />

<DataTable
  columns={[
    { key: 'name', label: 'Nama', sortable: true },
    { key: 'email', label: 'Email' },
    { key: 'role', label: 'Peran' },
    { key: 'status', label: 'Status' },
    { key: 'mfa', label: 'MFA', render: (item: any) => item.mfa ? 'Aktif' : 'Nonaktif' },
  ]}
  data={users}
  total={128}
/>
