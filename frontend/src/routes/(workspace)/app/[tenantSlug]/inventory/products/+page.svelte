<script lang="ts">
  import PageHeader from '$lib/components/layout/PageHeader.svelte';
  import DataTable from '$lib/components/data-display/DataTable.svelte';
  import Button from '$lib/components/ui/Button.svelte';
  import MetricCard from '$lib/components/data-display/MetricCard.svelte';

  const products = [
    { sku: 'PRD-001', name: 'Produk A', category: 'Kategori 1', stock: 45, minStock: 10, price: 150000, cost: 100000, status: 'active' },
    { sku: 'PRD-002', name: 'Produk B', category: 'Kategori 1', stock: 8, minStock: 15, price: 250000, cost: 175000, status: 'active' },
    { sku: 'PRD-003', name: 'Produk C', category: 'Kategori 2', stock: 120, minStock: 20, price: 75000, cost: 50000, status: 'active' },
    { sku: 'PRD-004', name: 'Produk D', category: 'Kategori 2', stock: 0, minStock: 10, price: 0, cost: 0, status: 'inactive' },
  ];
</script>

<PageHeader title="Produk" description="Manajemen produk dan SKU" breadcrumbs={[{ label: 'Inventaris' }, { label: 'Produk' }]}>
  {#snippet actions()}
    <Button>+ Produk Baru</Button>
  {/snippet}
</PageHeader>

<div class="grid grid-cols-2 sm:grid-cols-4 gap-4 mb-6">
  <MetricCard label="Total Produk" value={24} format="number" />
  <MetricCard label="Stok Kritis" value={1} format="number" />
  <MetricCard label="Nilai Stok" value={38500000} format="currency" />
  <MetricCard label="Dead Stock" value={3} format="number" />
</div>

<DataTable
  columns={[
    { key: 'sku', label: 'SKU', sortable: true },
    { key: 'name', label: 'Nama', sortable: true },
    { key: 'category', label: 'Kategori' },
    { key: 'stock', label: 'Stok', align: 'right' },
    { key: 'price', label: 'Harga', align: 'right', render: (item: any) => `Rp ${item.price.toLocaleString('id-ID')}` },
    { key: 'status', label: 'Status', render: (item: any) => `<span class="badge-${item.status}">${item.status}</span>` },
  ]}
  data={products}
  total={24}
/>
