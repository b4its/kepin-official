<script lang="ts">
  import PageHeader from '$lib/components/layout/PageHeader.svelte';
  import MetricCard from '$lib/components/data-display/MetricCard.svelte';
  import DataTable from '$lib/components/data-display/DataTable.svelte';
  import { BarChart3, TrendingUp, AlertTriangle, Activity } from '@lucide/svelte';

  const recentTransactions = [
    { date: '25 Jul', desc: 'Penjualan Tunai', account: 'Kas', amount: 2500000, type: 'income' },
    { date: '24 Jul', desc: 'Pembelian Stok', account: 'Persediaan', amount: -1800000, type: 'expense' },
    { date: '24 Jul', desc: 'Pembayaran Listrik', account: 'Beban', amount: -450000, type: 'expense' },
    { date: '23 Jul', desc: 'Penjualan Online', account: 'Bank', amount: 3200000, type: 'income' },
  ];
</script>

<PageHeader title="Dashboard" description="Toko Maju Jaya · Periode: Juli 2026 · Diperbarui: 2 menit lalu" />

<div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
  <MetricCard label="Pendapatan" value={45200000} previousValue={38900000} />
  <MetricCard label="Pengeluaran" value={28100000} previousValue={26400000} />
  <MetricCard label="Laba Kotor" value={17100000} previousValue={12500000} format="currency" />
  <MetricCard label="Saldo Kas" value={45300000} format="currency" />
</div>

<div class="grid lg:grid-cols-3 gap-6 mb-6">
  <div class="card p-5 lg:col-span-2">
    <h3 class="font-semibold mb-4">Arus Kas (30 Hari)</h3>
    <div class="h-48 bg-[hsl(var(--muted))] rounded flex items-center justify-center">
      <BarChart3 class="w-8 h-8 text-[hsl(var(--muted-foreground))]" />
    </div>
  </div>
  <div class="space-y-3">
    <div class="card p-4">
      <div class="flex items-center gap-2 text-[var(--color-kepin-red)] mb-2">
        <AlertTriangle class="w-4 h-4" />
        <span class="font-semibold text-sm">Alert</span>
      </div>
      <p class="text-sm">3 invoice jatuh tempo dalam 7 hari</p>
      <p class="text-sm mt-1">2 produk stok kritis</p>
    </div>
    <div class="card p-4">
      <div class="flex items-center gap-2 text-[var(--color-kepin-blue)] mb-2">
        <Activity class="w-4 h-4" />
        <span class="font-semibold text-sm">AI Insight</span>
      </div>
      <p class="text-sm">Penjualan diperkirakan naik 15% bulan depan</p>
      <p class="text-xs text-[hsl(var(--muted-foreground))] mt-1">Berdasarkan data 90 hari terakhir</p>
    </div>
    <div class="card p-4">
      <div class="flex items-center gap-2 text-[var(--color-kepin-green)] mb-2">
        <TrendingUp class="w-4 h-4" />
        <span class="font-semibold text-sm">Rekomendasi</span>
      </div>
      <p class="text-sm">Restock produk A & C dalam 3 hari</p>
    </div>
  </div>
</div>

<DataTable
  columns={[
    { key: 'date', label: 'Tanggal' },
    { key: 'desc', label: 'Deskripsi' },
    { key: 'account', label: 'Akun' },
    { key: 'amount', label: 'Jumlah', align: 'right', render: (item: any) => item.amount > 0 ? `Rp ${item.amount.toLocaleString('id-ID')}` : `(Rp ${Math.abs(item.amount).toLocaleString('id-ID')})` },
  ]}
  data={recentTransactions}
  total={128}
  page={1}
  pageSize={10}
/>
