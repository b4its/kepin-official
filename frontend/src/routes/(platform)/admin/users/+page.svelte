<script lang="ts">
  import PageHeader from '$lib/components/layout/PageHeader.svelte';
  import DataTable from '$lib/components/data-display/DataTable.svelte';
  import { adminUsers } from '$lib/stores/data';
</script>

<PageHeader title="Manajemen Pengguna" description="Kelola pengguna platform" />

<DataTable
  columns={[
    { key: 'name', label: 'Nama', sortable: true },
    { key: 'email', label: 'Email' },
    { key: 'id', label: 'ID' },
  ]}
  data={$adminUsers}
  total={$adminUsers.length}
  searchable={true}
/>
