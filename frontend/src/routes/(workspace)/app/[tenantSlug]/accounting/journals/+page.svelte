<script lang="ts">
  import PageHeader from '$lib/components/layout/PageHeader.svelte';
  import DataTable from '$lib/components/data-display/DataTable.svelte';
  import StatusBadge from '$lib/components/data-display/StatusBadge.svelte';
  import Button from '$lib/components/ui/Button.svelte';

  const journals = [
    { date: '25 Jul 2026', ref: 'JNL-001', desc: 'Penjualan Tunai', status: 'posted', total: 2500000 },
    { date: '24 Jul 2026', ref: 'JNL-002', desc: 'Pembelian Stok', status: 'posted', total: 1800000 },
    { date: '23 Jul 2026', ref: 'JNL-003', desc: 'Pembayaran Listrik', status: 'posted', total: 450000 },
    { date: '22 Jul 2026', ref: 'JNL-004', desc: 'Penyesuaian Persediaan', status: 'draft', total: 0 },
  ];
</script>

<PageHeader title="Jurnal" description="Jurnal akuntansi" breadcrumbs={[{ label: 'Akuntansi' }, { label: 'Jurnal' }]}>
  {#snippet actions()}
    <Button>+ Jurnal Baru</Button>
  {/snippet}
</PageHeader>

<DataTable
  columns={[
    { key: 'date', label: 'Tanggal', sortable: true },
    { key: 'ref', label: 'Referensi' },
    { key: 'desc', label: 'Deskripsi' },
    { key: 'status', label: 'Status', render: (item: any) => `<span class="badge-${item.status}">${item.status}</span>` },
    { key: 'total', label: 'Total', align: 'right', render: (item: any) => `Rp ${item.total.toLocaleString('id-ID')}` },
  ]}
  data={journals}
  total={64}
  page={1}
  pageSize={10}
/>
