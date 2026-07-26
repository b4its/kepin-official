<script lang="ts">
  import PageHeader from '$lib/components/layout/PageHeader.svelte';
  import DataTable from '$lib/components/data-display/DataTable.svelte';
  import Button from '$lib/components/ui/Button.svelte';

  const accounts = [
    { code: '1-1000', name: 'Kas', type: 'Asset', balance: 15000000, status: 'active' },
    { code: '1-1100', name: 'Bank BCA', type: 'Asset', balance: 45300000, status: 'active' },
    { code: '1-2000', name: 'Piutang Usaha', type: 'Asset', balance: 8500000, status: 'active' },
    { code: '1-3000', name: 'Persediaan', type: 'Asset', balance: 12000000, status: 'active' },
    { code: '2-1000', name: 'Utang Usaha', type: 'Liability', balance: -5000000, status: 'active' },
    { code: '3-1000', name: 'Modal', type: 'Equity', balance: -50000000, status: 'active' },
    { code: '4-1000', name: 'Penjualan', type: 'Income', balance: -45200000, status: 'active' },
    { code: '5-1000', name: 'Beban Gaji', type: 'Expense', balance: 15000000, status: 'active' },
  ];
</script>

<PageHeader title="Chart of Accounts" description="Daftar akun akuntansi" breadcrumbs={[{ label: 'Akuntansi' }, { label: 'Chart of Accounts' }]}>
  {#snippet actions()}
    <Button variant="secondary">+ Akun Baru</Button>
  {/snippet}
</PageHeader>

<DataTable
  columns={[
    { key: 'code', label: 'Kode', sortable: true },
    { key: 'name', label: 'Nama Akun', sortable: true },
    { key: 'type', label: 'Tipe' },
    { key: 'balance', label: 'Saldo', align: 'right', render: (item: any) => `Rp ${Math.abs(item.balance).toLocaleString('id-ID')}` },
    { key: 'status', label: 'Status', render: (item: any) => `<span class="badge-${item.status}">${item.status}</span>` },
  ]}
  data={accounts}
  total={24}
/>
