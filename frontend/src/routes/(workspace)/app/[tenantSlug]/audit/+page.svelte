<script lang="ts">
  import { auditEvents } from '$lib/stores/data';
  import PageHeader from '$lib/components/layout/PageHeader.svelte';
  import DataTable from '$lib/components/data-display/DataTable.svelte';
</script>

<PageHeader title="Audit Trail" description="Riwayat aktivitas dan perubahan data" breadcrumbs={[{ label: 'Audit Trail' }]} />

<DataTable
  columns={[
    { key: 'timestamp', label: 'Waktu', sortable: true },
    { key: 'actor', label: 'Pelaku', sortable: true },
    { key: 'action', label: 'Aksi' },
    { key: 'module', label: 'Modul' },
    { key: 'objectId', label: 'Objek' },
    { key: 'integrityVerified', label: 'Verifikasi', render: (item: any) => item.integrityVerified ? 'Terverifikasi' : '-' },
  ]}
  data={$auditEvents}
  total={1250}
  page={1}
  pageSize={5}
  searchable={true}
/>
