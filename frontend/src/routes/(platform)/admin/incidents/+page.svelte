<script lang="ts">
  import PageHeader from '$lib/components/layout/PageHeader.svelte';
  import DataTable from '$lib/components/data-display/DataTable.svelte';
  import StatusBadge from '$lib/components/data-display/StatusBadge.svelte';
  import { adminTenants } from '$lib/stores/data';

  const incidents = [
    { id: 'INC-001', severity: 'high', title: 'Failed login attempts >100 from single IP', status: 'resolved', date: '2026-07-25' },
    { id: 'INC-002', severity: 'medium', title: 'Suspicious API key usage detected', status: 'investigating', date: '2026-07-24' },
    { id: 'INC-003', severity: 'low', title: 'TLS certificate renewal', status: 'resolved', date: '2026-07-20' },
  ];
</script>

<PageHeader title="Insiden Keamanan" description="Riwayat insiden dan penanganan" />

<DataTable
  columns={[
    { key: 'id', label: 'ID' },
    { key: 'title', label: 'Deskripsi' },
    { key: 'severity', label: 'Severitas' },
    { key: 'status', label: 'Status' },
    { key: 'date', label: 'Tanggal' },
  ]}
  data={incidents}
  searchable={true}
/>
