<script lang="ts">
  import PageHeader from '$lib/components/layout/PageHeader.svelte';
  import DataTable from '$lib/components/data-display/DataTable.svelte';
  import Button from '$lib/components/ui/Button.svelte';
  import StatusBadge from '$lib/components/data-display/StatusBadge.svelte';

  const orders = [
    { number: 'PO-001', supplier: 'PT Supplier ABC', date: '22 Jul 2026', items: 5, total: 8500000, status: 'pending' },
    { number: 'PO-002', supplier: 'CV Bahan Baku', date: '20 Jul 2026', items: 3, total: 4200000, status: 'received' },
    { number: 'PO-003', supplier: 'PT Supplier ABC', date: '15 Jul 2026', items: 8, total: 12500000, status: 'completed' },
  ];
</script>

<PageHeader title="Pesanan Pembelian" description="Purchase order" breadcrumbs={[{ label: 'Pembelian' }, { label: 'Pesanan' }]}>
  {#snippet actions()}
    <Button>+ PO Baru</Button>
  {/snippet}
</PageHeader>

<DataTable
  columns={[
    { key: 'number', label: 'No. PO', sortable: true },
    { key: 'supplier', label: 'Pemasok', sortable: true },
    { key: 'date', label: 'Tanggal' },
    { key: 'items', label: 'Item', align: 'right' },
    { key: 'total', label: 'Total', align: 'right', render: (item: any) => `Rp ${item.total.toLocaleString('id-ID')}` },
    { key: 'status', label: 'Status', render: (item: any) => `<span class="badge-${item.status}">${item.status}</span>` },
  ]}
  data={orders}
  total={18}
/>
