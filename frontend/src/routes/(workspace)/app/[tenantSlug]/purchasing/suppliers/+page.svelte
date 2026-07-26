<script lang="ts">
  import PageHeader from '$lib/components/layout/PageHeader.svelte';
  import DataTable from '$lib/components/data-display/DataTable.svelte';
  import Button from '$lib/components/ui/Button.svelte';

  const suppliers = [
    { name: 'PT Supplier ABC', email: 'abc@supplier.com', phone: '021-3456789', address: 'Jakarta', totalPo: 15, totalAmount: 52000000 },
    { name: 'CV Bahan Baku', email: 'bahan@supplier.com', phone: '021-9876543', address: 'Bandung', totalPo: 8, totalAmount: 18500000 },
    { name: 'UD Sumber Rejeki', email: 'rejeki@supplier.com', phone: '031-4567890', address: 'Surabaya', totalPo: 5, totalAmount: 9500000 },
  ];
</script>

<PageHeader title="Pemasok" description="Daftar pemasok" breadcrumbs={[{ label: 'Pembelian' }, { label: 'Pemasok' }]}>
  {#snippet actions()}
    <Button variant="secondary">+ Pemasok Baru</Button>
  {/snippet}
</PageHeader>

<DataTable
  columns={[
    { key: 'name', label: 'Nama', sortable: true },
    { key: 'email', label: 'Email' },
    { key: 'phone', label: 'Telepon' },
    { key: 'address', label: 'Kota' },
    { key: 'totalPo', label: 'PO', align: 'right' },
    { key: 'totalAmount', label: 'Total', align: 'right', render: (item: any) => `Rp ${item.totalAmount.toLocaleString('id-ID')}` },
  ]}
  data={suppliers}
  total={12}
/>
