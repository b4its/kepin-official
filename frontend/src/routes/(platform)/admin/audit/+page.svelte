<script lang="ts">
  import PageHeader from '$lib/components/layout/PageHeader.svelte';
  import DataTable from '$lib/components/data-display/DataTable.svelte';

  const auditEvents = [
    { time: '2026-07-25 14:30', actor: 'Super Admin', action: 'Suspend tenant', target: 'Toko ABC', module: 'Tenant' },
    { time: '2026-07-25 11:20', actor: 'Super Admin', action: 'Change plan', target: 'PT Maju', module: 'Subscription' },
    { time: '2026-07-24 09:15', actor: 'System', action: 'Auto-renewal', target: '48 tenants', module: 'Billing' },
  ];
</script>

<PageHeader title="Audit Platform" description="Log aktivitas administratif platform" />

<DataTable
  columns={[
    { key: 'time', label: 'Waktu', sortable: true },
    { key: 'actor', label: 'Pelaku' },
    { key: 'action', label: 'Aksi' },
    { key: 'target', label: 'Target' },
    { key: 'module', label: 'Modul' },
  ]}
  data={auditEvents}
  total={156}
/>
