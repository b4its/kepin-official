<script lang="ts">
  import PageHeader from '$lib/components/layout/PageHeader.svelte';
  import DataTable from '$lib/components/data-display/DataTable.svelte';
  import { platformAuditEvents } from '$lib/stores/data';
</script>

<PageHeader title="Audit Platform" description="Log aktivitas administratif platform" />

<DataTable
  columns={[
    { key: 'timestamp', label: 'Waktu', sortable: true },
    { key: 'actor', label: 'Pelaku' },
    { key: 'action', label: 'Aksi' },
    { key: 'objectId', label: 'Target' },
    { key: 'module', label: 'Modul' },
  ]}
  data={$platformAuditEvents}
  total={$platformAuditEvents.length}
  searchable={true}
/>
