<script lang="ts">
  import PageHeader from '$lib/components/layout/PageHeader.svelte';
  import DataTable from '$lib/components/data-display/DataTable.svelte';
  import StatusBadge from '$lib/components/data-display/StatusBadge.svelte';

  const movements = [
    { date: '25 Jul 2026', product: 'Produk A', type: 'in', qty: 50, before: 20, after: 70, reason: 'Pembelian dari supplier', ref: 'PO-001' },
    { date: '24 Jul 2026', product: 'Produk B', type: 'out', qty: -5, before: 15, after: 10, reason: 'Penjualan', ref: 'INV-001' },
    { date: '23 Jul 2026', product: 'Produk C', type: 'adjustment', qty: -2, before: 15, after: 13, reason: 'Barang rusak', ref: 'ADJ-001' },
    { date: '22 Jul 2026', product: 'Produk A', type: 'transfer', qty: -10, before: 40, after: 30, reason: 'Transfer ke Cabang 2', ref: 'TRF-001' },
  ];
</script>

<PageHeader title="Pergerakan Stok" description="Riwayat pergerakan inventaris" breadcrumbs={[{ label: 'Inventaris' }, { label: 'Pergerakan' }]} />

<DataTable
  columns={[
    { key: 'date', label: 'Tanggal', sortable: true },
    { key: 'product', label: 'Produk', sortable: true },
    { key: 'type', label: 'Tipe', render: (item: any) => `<span class="badge-${item.type}">${item.type}</span>` },
    { key: 'qty', label: 'Qty', align: 'right' },
    { key: 'before', label: 'Stok Awal', align: 'right' },
    { key: 'after', label: 'Stok Akhir', align: 'right' },
    { key: 'reason', label: 'Alasan' },
  ]}
  data={movements}
  total={256}
  page={1}
  pageSize={10}
/>
