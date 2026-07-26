<script lang="ts">
  import PageHeader from '$lib/components/layout/PageHeader.svelte';
  import DataTable from '$lib/components/data-display/DataTable.svelte';

  const events = [
    { time: '25 Jul 2026 14:30', actor: 'Budi Santoso', action: 'Post Jurnal', module: 'Accounting', obj: 'JNL-001', integrity: true },
    { time: '25 Jul 2026 11:20', actor: 'Ani Lestari', action: 'Buat Invoice', module: 'Sales', obj: 'INV-005', integrity: true },
    { time: '24 Jul 2026 16:45', actor: 'Budi Santoso', action: 'Adjust Stok', module: 'Inventory', obj: 'ADJ-001', integrity: true },
    { time: '24 Jul 2026 09:15', actor: 'System', action: 'Backup Otomatis', module: 'System', obj: 'Daily', integrity: true },
    { time: '23 Jul 2026 15:00', actor: 'Dedi Kurniawan', action: 'Login', module: 'Auth', obj: 'Session', integrity: true },
  ];
</script>

<PageHeader title="Audit Trail" description="Riwayat aktivitas dan perubahan data" breadcrumbs={[{ label: 'Audit Trail' }]} />

<DataTable
  columns={[
    { key: 'time', label: 'Waktu', sortable: true },
    { key: 'actor', label: 'Pelaku', sortable: true },
    { key: 'action', label: 'Aksi' },
    { key: 'module', label: 'Modul' },
    { key: 'obj', label: 'Objek' },
    { key: 'integrity', label: 'Verifikasi', render: (item: any) => item.integrity ? 'Terverifikasi' : '-' },
  ]}
  data={events}
  total={1250}
  page={1}
  pageSize={10}
/>
