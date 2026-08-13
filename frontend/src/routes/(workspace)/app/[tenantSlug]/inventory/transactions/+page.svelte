<script lang="ts">
  import { page } from '$app/stores';
  import PageHeader from '$lib/components/layout/PageHeader.svelte';
  import DataTable from '$lib/components/data-display/DataTable.svelte';
  import Button from '$lib/components/ui/Button.svelte';
  import MetricCard from '$lib/components/data-display/MetricCard.svelte';
  import Modal from '$lib/components/ui/Modal.svelte';
  import ExportModal from '$lib/components/ui/ExportModal.svelte';
  import { tenantApi } from '$lib/stores/data';
  import { showToast } from '$lib/stores/toast';
  import { formatIDR } from '$lib/utils/currency';
  import { Download, Search } from '@lucide/svelte';

  const slug = $derived($page.params.tenantSlug || '');

  let rows = $state<any[]>([]);
  let search = $state('');
  let pageNo = $state(1);
  let total = $state(0);
  let loading = $state(false);
  let searchTimer: ReturnType<typeof setTimeout> | undefined;
  const PAGE_SIZE = 20;

  let detail = $state<any | null>(null);
  let showExport = $state(false);

  const exportColumns = [
    { key: 'checkoutNumber', label: 'No. Checkout' },
    { key: 'transactionDate', label: 'Tanggal' },
    { key: 'products', label: 'Produk' },
    { key: 'itemsCount', label: 'Total Qty' },
    { key: 'totalAmount', label: 'Total Harga', render: (r: any) => formatIDR(Number(r.totalAmount)) },
    { key: 'amountPaid', label: 'Dibayar', render: (r: any) => formatIDR(Number(r.amountPaid)) },
    { key: 'changeAmount', label: 'Kembalian', render: (r: any) => formatIDR(Number(r.changeAmount)) },
  ];

  function fmtDate(v: string) {
    if (!v) return '-';
    return v.slice(0, 10);
  }

  function productSummary(txn: any): string {
    const names = (txn.lines || []).map((l: any) => `${l.productName} ×${Number(l.quantity)}`);
    if (names.length === 0) return '-';
    return names.slice(0, 2).join(', ') + (names.length > 2 ? ` +${names.length - 2} lagi` : '');
  }

  async function load(q = search, p = pageNo) {
    loading = true;
    try {
      const res: any = await tenantApi.getPosTransactions(slug, q || undefined, PAGE_SIZE, p);
      rows = (Array.isArray(res.items) ? res.items : []).map((t: any) => ({
        ...t,
        transactionDate: fmtDate(t.transactionDate || t.createdAt),
        products: productSummary(t),
      }));
      total = res.total ?? 0;
    } catch (err: any) {
      showToast(err?.message || 'Gagal memuat transaksi produk', 'error');
    } finally {
      loading = false;
    }
  }

  $effect(() => {
    if (!slug) return;
    clearTimeout(searchTimer);
    searchTimer = setTimeout(() => {
      pageNo = 1;
      void load(search, 1);
    }, search ? 250 : 0);
    return () => clearTimeout(searchTimer);
  });

  const totalTransaksi = $derived(total);
  const totalPenjualan = $derived(rows.reduce((s, r) => s + Number(r.totalAmount || 0), 0));
  const totalKembalian = $derived(rows.reduce((s, r) => s + Number(r.changeAmount || 0), 0));

  function openDetail(row: any) {
    detail = row;
  }
</script>

<PageHeader title="Transaksi Produk" description="Riwayat penjualan Point of Sales — produk dibeli, jumlah dibayarkan, total harga, dan kembalian" breadcrumbs={[{ label: 'Inventaris' }, { label: 'Transaksi Produk' }]}>
  {#snippet actions()}
    <Button variant="secondary" onclick={() => showExport = true}><Download class="w-4 h-4" /> Ekspor</Button>
  {/snippet}
</PageHeader>

<div class="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-6">
  <MetricCard label="Total Transaksi" value={totalTransaksi} format="number" />
  <MetricCard label="Total Penjualan (halaman)" value={totalPenjualan} format="currency" />
  <MetricCard label="Total Kembalian (halaman)" value={totalKembalian} format="currency" />
</div>

<div class="flex items-center gap-2 mb-4 card px-3 py-2">
  <Search class="w-4 h-4 shrink-0 text-[hsl(var(--muted-foreground))]" />
  <input
    type="search"
    bind:value={search}
    placeholder="Cari no. checkout atau nama produk..."
    class="flex-1 bg-transparent border-none outline-none text-sm placeholder:text-[hsl(var(--muted-foreground))]"
  />
</div>

<DataTable
  columns={[
    { key: 'checkoutNumber', label: 'No. Checkout', sortable: false },
    { key: 'transactionDate', label: 'Tanggal' },
    { key: 'products', label: 'Produk' },
    { key: 'itemsCount', label: 'Qty', align: 'right' },
    { key: 'totalAmount', label: 'Total Harga', align: 'right', render: (item: any) => formatIDR(Number(item.totalAmount)) },
    { key: 'amountPaid', label: 'Dibayar', align: 'right', render: (item: any) => formatIDR(Number(item.amountPaid)) },
    { key: 'changeAmount', label: 'Kembalian', align: 'right', render: (item: any) => `<span class="tabular-nums">${formatIDR(Number(item.changeAmount))}</span>` },
  ]}
  data={rows}
  loading={loading}
  total={total}
  page={pageNo}
  pageSize={PAGE_SIZE}
  onpagechange={(p) => { pageNo = p; void load(search, p); }}
  emptyMessage="Belum ada transaksi POS. Lakukan checkout di halaman Point of Sales."
>
  {#snippet rowActions(item: any)}
    <button onclick={() => openDetail(item)} class="text-xs text-[hsl(var(--primary))] hover:underline">Detail</button>
  {/snippet}
</DataTable>

<Modal title={detail ? `Transaksi ${detail.checkoutNumber}` : 'Detail Transaksi'} open={detail !== null} onclose={() => detail = null} size="md">
  {#if detail}
    <div class="space-y-4">
      <div class="grid grid-cols-2 sm:grid-cols-4 gap-3 text-sm">
        <div>
          <p class="text-xs text-[hsl(var(--muted-foreground))]">Tanggal</p>
          <p class="font-medium">{detail.transactionDate}</p>
        </div>
        <div>
          <p class="text-xs text-[hsl(var(--muted-foreground))]">Total Qty</p>
          <p class="font-medium tabular-nums">{Number(detail.itemsCount)}</p>
        </div>
        <div>
          <p class="text-xs text-[hsl(var(--muted-foreground))]">Dibayar</p>
          <p class="font-medium tabular-nums">{formatIDR(Number(detail.amountPaid))}</p>
        </div>
        <div>
          <p class="text-xs text-[hsl(var(--muted-foreground))]">Kembalian</p>
          <p class="font-medium tabular-nums text-[var(--color-kepin-green)]">{formatIDR(Number(detail.changeAmount))}</p>
        </div>
      </div>

      <div>
        <h4 class="text-sm font-semibold mb-2">Produk Dibeli</h4>
        <div class="overflow-x-auto rounded-md border border-[hsl(var(--border))]">
          <table class="w-full text-sm">
            <thead class="bg-[hsl(var(--muted))]">
              <tr>
                <th class="px-3 py-2 text-left font-medium text-xs text-[hsl(var(--muted-foreground))]">Produk</th>
                <th class="px-3 py-2 text-right font-medium text-xs text-[hsl(var(--muted-foreground))]">Qty</th>
                <th class="px-3 py-2 text-right font-medium text-xs text-[hsl(var(--muted-foreground))]">Harga Satuan</th>
                <th class="px-3 py-2 text-right font-medium text-xs text-[hsl(var(--muted-foreground))]">Subtotal</th>
              </tr>
            </thead>
            <tbody>
              {#each detail.lines || [] as line}
                <tr class="border-t border-[hsl(var(--border))]">
                  <td class="px-3 py-2">{line.productName}</td>
                  <td class="px-3 py-2 text-right tabular-nums">{Number(line.quantity)}</td>
                  <td class="px-3 py-2 text-right tabular-nums">{formatIDR(Number(line.unitPrice))}</td>
                  <td class="px-3 py-2 text-right tabular-nums">{formatIDR(Number(line.lineTotal))}</td>
                </tr>
              {/each}
              <tr class="border-t border-[hsl(var(--border))] bg-[hsl(var(--muted))]">
                <td class="px-3 py-2 font-semibold" colspan="3">Total Harga</td>
                <td class="px-3 py-2 text-right font-semibold tabular-nums">{formatIDR(Number(detail.totalAmount))}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <div class="flex justify-end gap-2 pt-1">
        <Button variant="secondary" onclick={() => detail = null}>Tutup</Button>
      </div>
    </div>
  {/if}
</Modal>

<ExportModal
  open={showExport}
  onclose={() => showExport = false}
  title="Transaksi Produk"
  subtitle="Riwayat penjualan Point of Sales"
  columns={exportColumns}
  rows={rows}
  filename="transaksi-produk"
/>
