<script lang="ts">
  import PageHeader from '$lib/components/layout/PageHeader.svelte';
  import DataTable from '$lib/components/data-display/DataTable.svelte';
  import StatusBadge from '$lib/components/data-display/StatusBadge.svelte';

  const reconciliations = [
    { date: '25 Jul 2026', bank: 'BCA', bankBalance: 45800000, bookBalance: 45300000, diff: 500000, status: 'open' },
    { date: '24 Jul 2026', bank: 'Mandiri', bankBalance: 22000000, bookBalance: 22000000, diff: 0, status: 'matched' },
  ];
</script>

<PageHeader title="Rekonsiliasi Bank" description="Cocokkan catatan bank dengan pembukuan" breadcrumbs={[{ label: 'Akuntansi' }, { label: 'Rekonsiliasi' }]} />

<DataTable
  columns={[
    { key: 'date', label: 'Periode', sortable: true },
    { key: 'bank', label: 'Bank' },
    { key: 'bankBalance', label: 'Saldo Bank', align: 'right', render: (item: any) => `Rp ${item.bankBalance.toLocaleString('id-ID')}` },
    { key: 'bookBalance', label: 'Saldo Buku', align: 'right', render: (item: any) => `Rp ${item.bookBalance.toLocaleString('id-ID')}` },
    { key: 'diff', label: 'Selisih', align: 'right', render: (item: any) => `Rp ${item.diff.toLocaleString('id-ID')}` },
    { key: 'status', label: 'Status', render: (item: any) => `<span class="badge-${item.status}">${item.status}</span>` },
  ]}
  data={reconciliations}
  total={12}
/>
