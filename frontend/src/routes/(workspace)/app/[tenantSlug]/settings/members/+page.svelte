<script lang="ts">
  import PageHeader from '$lib/components/layout/PageHeader.svelte';
  import DataTable from '$lib/components/data-display/DataTable.svelte';
  import Button from '$lib/components/ui/Button.svelte';
  import StatusBadge from '$lib/components/data-display/StatusBadge.svelte';

  const members = [
    { name: 'Budi Santoso', email: 'budi@tokomaju.com', role: 'Owner', status: 'active' },
    { name: 'Ani Lestari', email: 'ani@tokomaju.com', role: 'Admin', status: 'active' },
    { name: 'Dedi Kurniawan', email: 'dedi@tokomaju.com', role: 'Staff', status: 'active' },
  ];
</script>

<PageHeader title="Anggota Tim" description="Kelola anggota workspace" breadcrumbs={[{ label: 'Pengaturan' }, { label: 'Anggota' }]}>
  {#snippet actions()}
    <Button>+ Undang Anggota</Button>
  {/snippet}
</PageHeader>

<DataTable
  columns={[
    { key: 'name', label: 'Nama', sortable: true },
    { key: 'email', label: 'Email' },
    { key: 'role', label: 'Peran' },
    { key: 'status', label: 'Status', render: (item: any) => `<span class="badge-${item.status}">${item.status}</span>` },
  ]}
  data={members}
  total={5}
/>
