<script lang="ts">
  import { page } from '$app/stores';
  import PageHeader from '$lib/components/layout/PageHeader.svelte';
  import DataTable from '$lib/components/data-display/DataTable.svelte';
  import Button from '$lib/components/ui/Button.svelte';
  import MetricCard from '$lib/components/data-display/MetricCard.svelte';
  import Modal from '$lib/components/ui/Modal.svelte';
  import ExportModal from '$lib/components/ui/ExportModal.svelte';
  import { currentRole, suppliers, supplierPayments, createSupplierPayment, postSupplierPayment, voidSupplierPayment } from '$lib/stores/data';
  import { showToast } from '$lib/stores/toast';
  import { Download, Plus } from '@lucide/svelte';

  const isOwner = $derived($currentRole === 'tenant_owner');
  const rows = $derived($supplierPayments.map((p) => ({ ...p, supplierName: $suppliers.find((s) => s.id === p.supplierId)?.name || '' })));
  const totalHutang = $derived(rows.filter(p => p.status === 'posted').reduce((s, p) => s + p.amount, 0));
  const dibayarBulanIni = $derived(rows.filter(p => p.status === 'posted' && new Date(p.date).getMonth() === new Date().getMonth() && new Date(p.date).getFullYear() === new Date().getFullYear()).reduce((s, p) => s + p.amount, 0));
  const draftCount = $derived(rows.filter(p => p.status === 'draft').length);
  const rataRata = $derived(rows.filter(p => p.status === 'posted').length ? Math.round(rows.filter(p => p.status === 'posted').reduce((s, p) => s + p.amount, 0) / rows.filter(p => p.status === 'posted').length) : 0);

  const statusLabel = (s: string) => ({ draft: 'Konsep', posted: 'Terkirim', voided: 'Dibatalkan' }[s] || s);
  const methodLabel = (m: string) => ({ cash: 'Kas', bank: 'Bank', transfer: 'Transfer', bca: 'BCA', mandiri: 'Mandiri', bni: 'BNI', bri: 'BRI' }[m] || m || 'Kas');

  let showModal = $state(false);
  let showExport = $state(false);
  let voidIndex = $state<number | null>(null);
  let saving = $state(false);
  let form = $state({ supplierId: '', paymentDate: '', amount: '', method: 'cash', reference: '' });

  const exportColumns = [
    { key: 'number', label: 'No. Pembayaran' },
    { key: 'supplierName', label: 'Pemasok' },
    { key: 'date', label: 'Tanggal' },
    { key: 'amount', label: 'Jumlah', render: (r: any) => `Rp ${Number(r.amount).toLocaleString('id-ID')}` },
    { key: 'method', label: 'Metode', render: (r: any) => methodLabel(r.method) },
    { key: 'status', label: 'Status', render: (r: any) => statusLabel(r.status) },
  ];

  function openCreate() {
    form = { supplierId: '', paymentDate: new Date().toISOString().slice(0, 10), amount: '', method: 'cash', reference: '' };
    showModal = true;
  }

  async function save() {
    if (!isOwner) return;
    if (!form.supplierId || !form.amount) { showToast('Pilih pemasok dan isi jumlah', 'error'); return; }
    saving = true;
    try {
      await createSupplierPayment({ supplierId: form.supplierId, paymentDate: form.paymentDate, amount: form.amount, method: form.method, reference: form.reference });
      showModal = false;
      showToast('Draft pembayaran dibuat', 'success');
    } catch (err: any) { showToast(err?.message || 'Gagal membuat pembayaran', 'error'); }
    finally { saving = false; }
  }

  async function post(item: any) {
    if (!isOwner) return;
    try { await postSupplierPayment(item.id); showToast('Pembayaran berhasil diposting ke buku besar', 'success'); }
    catch (err: any) { showToast(err?.message || 'Gagal memposting pembayaran', 'error'); }
  }

  async function confirmVoid() {
    if (voidIndex === null) return;
    try {
      await voidSupplierPayment($supplierPayments[voidIndex].id);
      voidIndex = null;
      showToast('Pembayaran dibatalkan (jurnal reversal dibuat)', 'success');
    } catch (err: any) { showToast(err?.message || 'Gagal membatalkan pembayaran', 'error'); }
  }
</script>

<PageHeader title="Pembayaran Pemasok" description="Supplier payment" breadcrumbs={[{ label: 'Pembelian' }, { label: 'Pembayaran' }]}>
  {#snippet actions()}
    <Button variant="secondary" onclick={() => showExport = true}><Download class="w-4 h-4" /> Ekspor</Button>
    {#if isOwner}<Button onclick={openCreate}><Plus class="w-4 h-4" /> Pembayaran Baru</Button>{/if}
  {/snippet}
</PageHeader>

{#if !isOwner}<div class="card p-4 mb-6 text-sm text-[hsl(var(--muted-foreground))]">Pembayaran ditampilkan read-only. Hanya owner dapat membuat, posting, atau void pembayaran.</div>{/if}

<div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
  <MetricCard label="Total Terbayar" value={totalHutang} format="currency" />
  <MetricCard label="Dibayar Bulan Ini" value={dibayarBulanIni} format="currency" />
  <MetricCard label="Draft Menunggu Posting" value={draftCount} format="number" />
  <MetricCard label="Rata-rata Pembayaran" value={rataRata} format="currency" />
</div>

<DataTable
  tourHook="payments-table"
  columns={[
    { key: 'number', label: 'No. Pembayaran', sortable: true },
    { key: 'supplierName', label: 'Pemasok', sortable: true },
    { key: 'date', label: 'Tanggal' },
    { key: 'method', label: 'Metode', render: (item: any) => methodLabel(item.method) },
    { key: 'amount', label: 'Jumlah', align: 'right', render: (item: any) => `Rp ${item.amount.toLocaleString('id-ID')}` },
    { key: 'status', label: 'Status', render: (item: any) => `<span class="badge-${item.status}">${statusLabel(item.status)}</span>` },
  ]}
  data={rows}
  total={rows.length}
  pageSize={10}
  searchable={true}
>
  {#snippet rowActions(item: any, i: number)}
    {#if isOwner}
      {#if item.status === 'draft'}<button class="text-xs text-[var(--color-kepin-green)] hover:underline mr-2" onclick={() => post(item)}>Post</button>{/if}
      {#if item.status === 'posted'}<button class="text-xs text-[var(--color-kepin-danger)] hover:underline" onclick={() => voidIndex = i}>Void</button>{/if}
    {/if}
  {/snippet}
</DataTable>

<Modal title="Pembayaran Baru" open={showModal} onclose={() => showModal = false}>
  <form onsubmit={save} class="space-y-4">
    <div class="grid sm:grid-cols-2 gap-4">
      <div>
        <label class="label-text" for="pay-supplier">Pemasok</label>
        <select id="pay-supplier" bind:value={form.supplierId} class="input-field mt-1" required>
          <option value="">Pilih pemasok</option>
          {#each $suppliers as supplier}<option value={supplier.id}>{supplier.name}</option>{/each}
        </select>
      </div>
      <div>
        <label class="label-text" for="pay-date">Tanggal</label>
        <input id="pay-date" type="date" bind:value={form.paymentDate} class="input-field mt-1" required />
      </div>
      <div>
        <label class="label-text" for="pay-method">Metode</label>
        <select id="pay-method" bind:value={form.method} class="input-field mt-1">
          <option value="cash">Kas</option>
          <option value="bank">Transfer Bank</option>
        </select>
        <p class="text-xs text-[hsl(var(--muted-foreground))] mt-1">Kas diposting ke akun Kas, transfer ke akun Bank.</p>
      </div>
      <div>
        <label class="label-text" for="pay-amount">Jumlah (Rp)</label>
        <input id="pay-amount" type="number" min="0.01" step="0.01" bind:value={form.amount} class="input-field mt-1" required />
      </div>
      <div class="sm:col-span-2">
        <label class="label-text" for="pay-reference">Referensi</label>
        <input id="pay-reference" bind:value={form.reference} class="input-field mt-1" placeholder="No. transfer / nota" />
      </div>
    </div>
    <div class="flex justify-end gap-2 pt-2">
      <Button variant="secondary" type="button" onclick={() => showModal = false}>Batal</Button>
      <Button type="submit" disabled={saving}>{saving ? 'Menyimpan...' : 'Simpan Draft'}</Button>
    </div>
  </form>
</Modal>

<Modal title="Void Pembayaran" open={voidIndex !== null} onclose={() => voidIndex = null}>
  <p class="text-sm mb-4">Void pembayaran ini? Jurnal pembayaran akan di-reverse (dibatalkan) di buku besar.</p>
  <div class="flex justify-end gap-2">
    <Button variant="secondary" onclick={() => voidIndex = null}>Tidak</Button>
    <Button variant="destructive" onclick={confirmVoid}>Ya, Void</Button>
  </div>
</Modal>

<ExportModal
  open={showExport}
  onclose={() => showExport = false}
  title="Pembayaran Pemasok"
  subtitle="Daftar pembayaran ke pemasok"
  columns={exportColumns}
  rows={rows}
  filename="supplier-payments"
/>
