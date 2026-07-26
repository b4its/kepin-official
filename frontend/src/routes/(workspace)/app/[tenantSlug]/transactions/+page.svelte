<script lang="ts">
  import PageHeader from '$lib/components/layout/PageHeader.svelte';
  import DataTable from '$lib/components/data-display/DataTable.svelte';
  import StatusBadge from '$lib/components/data-display/StatusBadge.svelte';
  import MetricCard from '$lib/components/data-display/MetricCard.svelte';
  import Button from '$lib/components/ui/Button.svelte';

  const transactions = [
    { date: '25 Jul 2026', desc: 'Penjualan Tunai', account: 'Kas', type: 'income', amount: 2500000, status: 'posted' },
    { date: '24 Jul 2026', desc: 'Pembelian Stok Barang', account: 'Persediaan', type: 'expense', amount: -1800000, status: 'posted' },
    { date: '24 Jul 2026', desc: 'Pembayaran Listrik', account: 'Beban Listrik', type: 'expense', amount: -450000, status: 'posted' },
    { date: '23 Jul 2026', desc: 'Penjualan Online', account: 'Bank BCA', type: 'income', amount: 3200000, status: 'posted' },
    { date: '22 Jul 2026', desc: 'Gaji Karyawan', account: 'Beban Gaji', type: 'expense', amount: -5000000, status: 'draft' },
  ];
</script>

<PageHeader title="Transaksi" description="Catatan transaksi keuangan">
  {#snippet actions()}
    <Button>+ Transaksi Baru</Button>
  {/snippet}
</PageHeader>

<div class="grid grid-cols-2 sm:grid-cols-4 gap-4 mb-6">
  <MetricCard label="Total Pemasukan" value={5700000} format="currency" />
  <MetricCard label="Total Pengeluaran" value={-7250000} format="currency" />
  <MetricCard label="Rata-rata Harian" value={850000} format="currency" />
  <MetricCard label="Transaksi Bulan Ini" value={128} format="number" />
</div>

<DataTable
  columns={[
    { key: 'date', label: 'Tanggal', sortable: true },
    { key: 'desc', label: 'Deskripsi', sortable: true },
    { key: 'account', label: 'Akun' },
    { key: 'type', label: 'Tipe' },
    { key: 'amount', label: 'Jumlah', align: 'right', render: (item: any) => item.amount > 0 ? `Rp ${item.amount.toLocaleString('id-ID')}` : `(Rp ${Math.abs(item.amount).toLocaleString('id-ID')})` },
    { key: 'status', label: 'Status', render: (item: any) => `<span class="badge-${item.status}">${item.status}</span>` },
  ]}
  data={transactions}
  total={128}
  page={1}
  pageSize={10}
/>
