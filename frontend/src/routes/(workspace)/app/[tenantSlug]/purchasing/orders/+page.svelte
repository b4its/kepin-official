<script lang="ts">
  import { page } from '$app/stores';
  import PageHeader from '$lib/components/layout/PageHeader.svelte';
  import DataTable from '$lib/components/data-display/DataTable.svelte';
  import Button from '$lib/components/ui/Button.svelte';
  import MetricCard from '$lib/components/data-display/MetricCard.svelte';
  import Modal from '$lib/components/ui/Modal.svelte';
  import ExportModal from '$lib/components/ui/ExportModal.svelte';
  import ConfirmDialog from '$lib/components/ui/ConfirmDialog.svelte';
  import { currentRole, suppliers, products, purchaseOrders, inventoryLocations, createPurchaseOrder, updatePurchaseOrder, deletePurchaseOrder, sendPurchaseOrder, receivePurchaseOrder, cancelPurchaseOrder, tenantApi } from '$lib/stores/data';
  import { showToast } from '$lib/stores/toast';
  import { Download, Plus } from '@lucide/svelte';

  type PoLine = { productId: string; itemName: string; quantity: string; unitPrice: string };
  type ReceiveLine = { lineId: string; itemName: string; quantity: number; receivedQuantity: number; quantityReceived: string };

  const slug = $derived($page.params.tenantSlug || '');
  const isOwner = $derived($currentRole === 'tenant_owner');

  const statusLabel = (s: string) => ({ draft: 'Konsep', sent: 'Terkirim', partial: 'Sebagian', received: 'Diterima', cancelled: 'Dibatalkan' }[s] || s);
  const rows = $derived($purchaseOrders.map((p) => ({ ...p, supplierName: $suppliers.find((s) => s.id === p.supplierId)?.name || p.supplierName || '' })));
  const poTerbuka = $derived($purchaseOrders.filter(p => ['draft', 'sent', 'partial'].includes(p.status)).reduce((s, p) => s + p.total, 0));
  const poBulanIni = $derived($purchaseOrders.filter(p => new Date(p.date).getMonth() === new Date().getMonth() && new Date(p.date).getFullYear() === new Date().getFullYear()).length);
  const poDiterima = $derived($purchaseOrders.filter(p => p.status === 'received').length);
  const rataRata = $derived($purchaseOrders.length ? Math.round($purchaseOrders.reduce((s, p) => s + p.total, 0) / $purchaseOrders.length) : 0);

  let showModal = $state(false);
  let showReceive = $state(false);
  let showExport = $state(false);
  let deleteIndex = $state<number | null>(null);
  let cancelIndex = $state<number | null>(null);
  let editingIndex = $state<number | null>(null);
  let receivingPo = $state<any>(null);
  let saving = $state(false);

  let form = $state({ supplierId: '', orderDate: '', expectedDate: '', notes: '', lines: [] as PoLine[] });
  let receiveForm = $state({ locationId: '', notes: '', lines: [] as ReceiveLine[] });
  const draftTotal = $derived(form.lines.reduce((sum, line) => sum + Number(line.quantity || 0) * Number(line.unitPrice || 0), 0));

  const exportColumns = [
    { key: 'number', label: 'No. PO' },
    { key: 'supplierName', label: 'Pemasok' },
    { key: 'date', label: 'Tanggal' },
    { key: 'expectedDate', label: 'Jatuh Tempo' },
    { key: 'total', label: 'Total', render: (r: any) => `Rp ${Number(r.total).toLocaleString('id-ID')}` },
    { key: 'status', label: 'Status', render: (r: any) => statusLabel(r.status) },
  ];

  function defaultLine(): PoLine { return { productId: '', itemName: '', quantity: '1', unitPrice: '' }; }
  function openCreate() {
    const today = new Date().toISOString().slice(0, 10);
    form = { supplierId: '', orderDate: today, expectedDate: '', notes: '', lines: [defaultLine()] };
    editingIndex = null;
    showModal = true;
  }
  function openEdit(i: number) {
    const po = $purchaseOrders[i];
    form = {
      supplierId: po.supplierId,
      orderDate: po.date,
      expectedDate: po.expectedDate || '',
      notes: po.notes || '',
      lines: (po.lines || []).map((l: any) => ({ productId: l.productId || '', itemName: l.itemName, quantity: String(l.quantity), unitPrice: String(l.unitPrice) })),
    };
    editingIndex = i;
    showModal = true;
  }
  function addLine() { form.lines = [...form.lines, defaultLine()]; }
  function removeLine(index: number) { if (form.lines.length > 1) form.lines = form.lines.filter((_, current) => current !== index); }
  function onProductSelect(line: PoLine, productId: string) {
    const product = $products.find(p => p.id === productId);
    line.productId = productId;
    if (product) {
      line.itemName = product.name;
      if (!line.unitPrice) line.unitPrice = product.cost ? String(product.cost) : '';
    }
  }

  async function save() {
    if (!slug || !isOwner) return;
    if (!form.supplierId || !form.lines.length) { showToast('Pilih pemasok dan minimal satu item', 'error'); return; }
    saving = true;
    try {
      const payload = {
        supplier_id: form.supplierId,
        order_date: form.orderDate,
        expected_date: form.expectedDate || null,
        notes: form.notes,
        lines: form.lines.map((line) => ({ product_id: line.productId || null, item_name: line.itemName, quantity: line.quantity || '0', unit_price: line.unitPrice || '0' })),
      };
      if (editingIndex !== null) {
        await updatePurchaseOrder($purchaseOrders[editingIndex].id, { expected_date: payload.expected_date, notes: payload.notes, lines: payload.lines });
        showToast('PO berhasil diperbarui', 'success');
      } else {
        await createPurchaseOrder(payload);
        showToast('PO berhasil dibuat', 'success');
      }
      showModal = false;
    } catch (err: any) { showToast(err?.message || 'Gagal menyimpan PO', 'error'); }
    finally { saving = false; }
  }

  async function sendPo(item: any) {
    if (!slug || !isOwner) return;
    try { await sendPurchaseOrder(item.id); showToast('PO dikirim ke pemasok', 'success'); }
    catch (err: any) { showToast(err?.message || 'Gagal mengirim PO', 'error'); }
  }

  function openReceive(i: number) {
    const po = $purchaseOrders[i];
    receivingPo = po;
    const activeLocations = $inventoryLocations.filter(l => l.status === 'active');
    receiveForm = {
      locationId: activeLocations.length ? activeLocations[0].id : '',
      notes: '',
      lines: (po.lines || []).map((l: any) => ({
        lineId: l.id, itemName: l.itemName, quantity: l.quantity, receivedQuantity: l.receivedQuantity || 0,
        quantityReceived: String(Math.max(l.quantity - (l.receivedQuantity || 0), 0)),
      })),
    };
    showReceive = true;
  }

  async function confirmReceive() {
    if (!slug || !isOwner || !receivingPo) return;
    if (!receiveForm.locationId) { showToast('Pilih lokasi penerimaan', 'error'); return; }
    const lines = receiveForm.lines
      .filter(l => Number(l.quantityReceived) > 0)
      .map(l => ({ line_id: l.lineId, quantity_received: l.quantityReceived }));
    if (!lines.length) { showToast('Tidak ada item yang diterima', 'error'); return; }
    saving = true;
    try {
      await receivePurchaseOrder(receivingPo.id, { locationId: receiveForm.locationId, lines, notes: receiveForm.notes });
      showReceive = false;
      receivingPo = null;
      showToast('Penerimaan barang berhasil dicatat', 'success');
    } catch (err: any) { showToast(err?.message || 'Gagal mencatat penerimaan', 'error'); }
    finally { saving = false; }
  }

  async function confirmCancel() {
    if (cancelIndex === null) return;
    try {
      await cancelPurchaseOrder($purchaseOrders[cancelIndex].id);
      cancelIndex = null;
      showToast('PO dibatalkan', 'success');
    } catch (err: any) { showToast(err?.message || 'Gagal membatalkan PO', 'error'); }
  }

  async function confirmDelete() {
    if (deleteIndex === null) return;
    try {
      await deletePurchaseOrder($purchaseOrders[deleteIndex].id);
      deleteIndex = null;
      showToast('PO dihapus', 'success');
    } catch (err: any) { showToast(err?.message || 'Gagal menghapus PO', 'error'); }
  }
</script>

<PageHeader title="Pesanan Pembelian" description="Purchase order" breadcrumbs={[{ label: 'Pembelian' }, { label: 'Pesanan' }]}>
  {#snippet actions()}
    <Button variant="secondary" onclick={() => showExport = true}><Download class="w-4 h-4" /> Ekspor</Button>
    {#if isOwner}<Button onclick={openCreate}><Plus class="w-4 h-4" /> PO Baru</Button>{/if}
  {/snippet}
</PageHeader>

{#if !isOwner}<div class="card p-4 mb-6 text-sm text-[hsl(var(--muted-foreground))]">Purchase order ditampilkan read-only. Hanya owner dapat membuat, kirim, terima, atau batal PO.</div>{/if}

<div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
  <MetricCard label="Total PO Terbuka" value={poTerbuka} format="currency" />
  <MetricCard label="PO Bulan Ini" value={poBulanIni} format="number" />
  <MetricCard label="PO Diterima" value={poDiterima} format="number" />
  <MetricCard label="Rata-rata Nilai PO" value={rataRata} format="currency" />
</div>

<DataTable
  columns={[
    { key: 'number', label: 'No. PO', sortable: true },
    { key: 'supplierName', label: 'Pemasok', sortable: true },
    { key: 'date', label: 'Tanggal' },
    { key: 'expectedDate', label: 'Jatuh Tempo' },
    { key: 'items', label: 'Item', align: 'right' },
    { key: 'total', label: 'Total', align: 'right', render: (item: any) => `Rp ${item.total.toLocaleString('id-ID')}` },
    { key: 'status', label: 'Status', render: (item: any) => `<span class="badge-${item.status}">${statusLabel(item.status)}</span>` },
  ]}
  data={rows}
  total={rows.length}
  pageSize={10}
  searchable={true}
>
  {#snippet rowActions(item: any, i: number)}
    {#if isOwner}
      {#if item.status === 'draft'}
        <button class="text-xs text-[var(--color-kepin-green)] hover:underline mr-2" onclick={() => sendPo(item)}>Kirim</button>
        <button class="text-xs text-[hsl(var(--primary))] hover:underline mr-2" onclick={() => openEdit(i)}>Edit</button>
        <button class="text-xs text-[var(--color-kepin-danger)] hover:underline mr-2" onclick={() => deleteIndex = i}>Hapus</button>
      {/if}
      {#if ['sent', 'partial'].includes(item.status)}
        <button class="text-xs text-[var(--color-kepin-green)] hover:underline mr-2" onclick={() => openReceive(i)}>Terima</button>
      {/if}
      {#if ['draft', 'sent', 'partial'].includes(item.status)}
        <button class="text-xs text-[var(--color-kepin-danger)] hover:underline" onclick={() => cancelIndex = i}>Batal</button>
      {/if}
    {/if}
  {/snippet}
</DataTable>

<Modal title={editingIndex !== null ? 'Edit PO' : 'PO Baru'} open={showModal} onclose={() => showModal = false}>
  <form onsubmit={save} class="space-y-4">
    <div class="grid sm:grid-cols-2 gap-4">
      <div>
        <label class="label-text" for="po-supplier">Pemasok</label>
        <select id="po-supplier" bind:value={form.supplierId} class="input-field mt-1" required>
          <option value="">Pilih pemasok</option>
          {#each $suppliers as supplier}<option value={supplier.id}>{supplier.name}</option>{/each}
        </select>
      </div>
      <div>
        <label class="label-text" for="po-date">Tanggal PO</label>
        <input id="po-date" type="date" bind:value={form.orderDate} class="input-field mt-1" required />
      </div>
      <div>
        <label class="label-text" for="po-expected">Jatuh Tempo</label>
        <input id="po-expected" type="date" bind:value={form.expectedDate} class="input-field mt-1" />
      </div>
      <div>
        <label class="label-text" for="po-notes">Catatan</label>
        <input id="po-notes" bind:value={form.notes} class="input-field mt-1" />
      </div>
    </div>
    <div class="space-y-2">
      <div class="flex justify-between items-center">
        <h3 class="text-sm font-semibold">Item</h3>
        <Button size="sm" variant="secondary" type="button" onclick={addLine}>+ Item</Button>
      </div>
      {#each form.lines as line, index}
        <div class="grid grid-cols-12 gap-2 rounded border border-[hsl(var(--border))] p-2">
          <select class="input-field col-span-3" value={line.productId} onchange={(e) => onProductSelect(line, (e.currentTarget as HTMLSelectElement).value)}>
            <option value="">Pilih produk</option>
            {#each $products as product}<option value={product.id}>{product.sku || product.name}</option>{/each}
          </select>
          <input class="input-field col-span-3" bind:value={line.itemName} placeholder="Nama item" required />
          <input class="input-field col-span-2" type="number" min="0.01" step="0.01" bind:value={line.quantity} placeholder="Qty" required />
          <input class="input-field col-span-3" type="number" min="0" step="0.01" bind:value={line.unitPrice} placeholder="Harga satuan" required />
          {#if form.lines.length > 1}
            <button type="button" class="col-span-1 text-right text-xs text-[var(--color-kepin-danger)]" onclick={() => removeLine(index)}>Hapus</button>
          {/if}
        </div>
      {/each}
      <div class="text-sm font-semibold text-right">Total: Rp {draftTotal.toLocaleString('id-ID')}</div>
    </div>
    <div class="flex justify-end gap-2 pt-2">
      <Button variant="secondary" type="button" onclick={() => showModal = false}>Batal</Button>
      <Button type="submit" disabled={saving}>{saving ? 'Menyimpan...' : 'Simpan'}</Button>
    </div>
  </form>
</Modal>

<Modal title={`Terima Barang — ${receivingPo?.number || ''}`} open={showReceive} onclose={() => showReceive = false}>
  <div class="space-y-4">
    {#if $inventoryLocations.length === 0}
      <div class="card p-4 text-sm text-[hsl(var(--muted-foreground))]">Belum ada lokasi inventori. Buat lokasi terlebih dahulu sebelum menerima barang.</div>
    {:else}
      <div>
        <label class="label-text" for="recv-location">Lokasi Penerimaan</label>
        <select id="recv-location" bind:value={receiveForm.locationId} class="input-field mt-1" required>
          <option value="">Pilih lokasi</option>
          {#each $inventoryLocations.filter(l => l.status === 'active') as location}<option value={location.id}>{location.name} ({location.code})</option>{/each}
        </select>
      </div>
      <div class="space-y-2">
        <h3 class="text-sm font-semibold">Item Diterima</h3>
        {#each receiveForm.lines as line}
          <div class="grid grid-cols-12 gap-2 items-center rounded border border-[hsl(var(--border))] p-2">
            <span class="col-span-7 text-sm">{line.itemName} <span class="text-[hsl(var(--muted-foreground))]">(pesan {line.quantity}, sudah {line.receivedQuantity})</span></span>
            <input class="input-field col-span-5" type="number" min="0" step="0.01" bind:value={line.quantityReceived} placeholder="Diterima" />
          </div>
        {/each}
      </div>
      <div>
        <label class="label-text" for="recv-notes">Catatan</label>
        <input id="recv-notes" bind:value={receiveForm.notes} class="input-field mt-1" />
      </div>
    {/if}
    <div class="flex justify-end gap-2 pt-2">
      <Button variant="secondary" onclick={() => showReceive = false}>Batal</Button>
      <Button onclick={confirmReceive} disabled={saving || $inventoryLocations.length === 0}>{saving ? 'Menyimpan...' : 'Terima Barang'}</Button>
    </div>
  </div>
</Modal>

<Modal title="Batal PO" open={cancelIndex !== null} onclose={() => cancelIndex = null}>
  <p class="text-sm mb-4">Batalkan PO ini? PO yang dibatalkan tidak dapat diproses lagi.</p>
  <div class="flex justify-end gap-2">
    <Button variant="secondary" onclick={() => cancelIndex = null}>Tidak</Button>
    <Button variant="destructive" onclick={confirmCancel}>Ya, Batalkan</Button>
  </div>
</Modal>

<ConfirmDialog
  open={deleteIndex !== null}
  onclose={() => deleteIndex = null}
  onconfirm={confirmDelete}
  message="Hapus draft purchase order ini? Tindakan ini tidak dapat dibatalkan."
/>

<ExportModal
  open={showExport}
  onclose={() => showExport = false}
  title="Purchase Order"
  subtitle="Daftar pesanan pembelian"
  columns={exportColumns}
  rows={rows}
  filename="purchase-order"
/>
