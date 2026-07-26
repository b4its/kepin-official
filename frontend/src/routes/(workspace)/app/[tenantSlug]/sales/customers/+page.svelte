<script lang="ts">
  import PageHeader from '$lib/components/layout/PageHeader.svelte';
  import DataTable from '$lib/components/data-display/DataTable.svelte';
  import Button from '$lib/components/ui/Button.svelte';

  const customers = [
    { name: 'Toko ABC', email: 'abc@email.com', phone: '0812-3456-7890', totalTrans: 12, totalAmount: 18500000, lastTrans: '25 Jul 2026' },
    { name: 'PT Maju Jaya', email: 'maju@email.com', phone: '0813-3456-7890', totalTrans: 8, totalAmount: 42000000, lastTrans: '20 Jul 2026' },
    { name: 'CV Sukses', email: 'sukses@email.com', phone: '0815-3456-7890', totalTrans: 5, totalAmount: 9500000, lastTrans: '25 Jul 2026' },
    { name: 'Restoran Sari', email: 'sari@email.com', phone: '0821-3456-7890', totalTrans: 3, totalAmount: 3200000, lastTrans: '28 Jul 2026' },
  ];
</script>

<PageHeader title="Pelanggan" description="Daftar pelanggan" breadcrumbs={[{ label: 'Penjualan' }, { label: 'Pelanggan' }]}>
  {#snippet actions()}
    <Button variant="secondary">+ Pelanggan Baru</Button>
  {/snippet}
</PageHeader>

<DataTable
  columns={[
    { key: 'name', label: 'Nama', sortable: true },
    { key: 'email', label: 'Email' },
    { key: 'phone', label: 'Telepon' },
    { key: 'totalTrans', label: 'Transaksi', align: 'right' },
    { key: 'totalAmount', label: 'Total', align: 'right', render: (item: any) => `Rp ${item.totalAmount.toLocaleString('id-ID')}` },
    { key: 'lastTrans', label: 'Transaksi Terakhir' },
  ]}
  data={customers}
  total={24}
/>
