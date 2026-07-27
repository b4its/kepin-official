<script lang="ts">
  import { auditEvents } from '$lib/stores/data';
  import PageHeader from '$lib/components/layout/PageHeader.svelte';
  import DataTable from '$lib/components/data-display/DataTable.svelte';
  import ExportModal from '$lib/components/ui/ExportModal.svelte';
  import Button from '$lib/components/ui/Button.svelte';
  import { Download } from '@lucide/svelte';

  let showExport = $state(false);

  const exportColumns = [
    { key: 'timestamp', label: 'Waktu' },
    { key: 'actor', label: 'Pelaku' },
    { key: 'action', label: 'Aksi' },
    { key: 'module', label: 'Modul' },
    { key: 'objectId', label: 'Objek' },
    { key: 'integrityVerified', label: 'Verifikasi', render: (r: any) => r.integrityVerified ? 'Terverifikasi' : '-' },
  ];
</script>

<PageHeader title="Audit Trail" description="Riwayat aktivitas dan perubahan data" breadcrumbs={[{ label: 'Audit Trail' }]}>
  {#snippet actions()}
    <Button variant="secondary" onclick={() => showExport = true}><Download class="w-4 h-4" /> Ekspor</Button>
  {/snippet}
</PageHeader>

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

<ExportModal
  open={showExport}
  onclose={() => showExport = false}
  title="Audit Trail"
  subtitle="Riwayat aktivitas sistem"
  columns={exportColumns}
  rows={$auditEvents}
  filename="audit-trail"
/>
