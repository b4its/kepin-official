<script lang="ts">
  import PageHeader from '$lib/components/layout/PageHeader.svelte';
  import DataTable from '$lib/components/data-display/DataTable.svelte';
  import Button from '$lib/components/ui/Button.svelte';
  import MetricCard from '$lib/components/data-display/MetricCard.svelte';

  const invoices = [
    { number: 'INV-2026-001', customer: 'Toko ABC', date: '20 Jul 2026', dueDate: '19 Agu 2026', total: 3500000, paid: 2000000, status: 'partial' },
    { number: 'INV-2026-002', customer: 'PT Maju Jaya', date: '15 Jul 2026', dueDate: '14 Agu 2026', total: 5200000, paid: 0, status: 'overdue' },
    { number: 'INV-2026-003', customer: 'CV Sukses', date: '25 Jul 2026', dueDate: '24 Agu 2026', total: 1800000, paid: 0, status: 'sent' },
    { number: 'INV-2026-004', customer: 'Toko ABC', date: '10 Jul 2026', dueDate: '09 Agu 2026', total: 2500000, paid: 2500000, status: 'paid' },
    { number: 'INV-2026-005', customer: 'Restoran Sari', date: '28 Jul 2026', dueDate: '27 Agu 2026', total: 1250000, paid: 0, status: 'draft' },
  ];
</script>

<PageHeader title="Invoice" description="Manajemen faktur penjualan" breadcrumbs={[{ label: 'Penjualan' }, { label: 'Invoice' }]}>
  {#snippet actions()}
    <Button>+ Invoice Baru</Button>
  {/snippet}
</PageHeader>

<div class="grid grid-cols-2 sm:grid-cols-4 gap-4 mb-6">
  <MetricCard label="Total Piutang" value={13200000} format="currency" />
  <MetricCard label="Jatuh Tempo" value={5200000} format="currency" />
  <MetricCard label="Invoice Bulan Ini" value={12} format="number" />
  <MetricCard label="Rata-rata" value={2800000} format="currency" />
</div>

<DataTable
  columns={[
    { key: 'number', label: 'No. Invoice', sortable: true },
    { key: 'customer', label: 'Pelanggan', sortable: true },
    { key: 'date', label: 'Tanggal' },
    { key: 'dueDate', label: 'Jatuh Tempo' },
    { key: 'total', label: 'Total', align: 'right', render: (item: any) => `Rp ${item.total.toLocaleString('id-ID')}` },
    { key: 'status', label: 'Status', render: (item: any) => `<span class="badge-${item.status}">${item.status}</span>` },
  ]}
  data={invoices}
  total={48}
  page={1}
  pageSize={10}
/>
