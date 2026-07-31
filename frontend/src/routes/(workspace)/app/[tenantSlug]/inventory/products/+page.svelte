<script lang="ts">
  import { page } from '$app/stores';
  import PageHeader from '$lib/components/layout/PageHeader.svelte';
  import DataTable from '$lib/components/data-display/DataTable.svelte';
  import Button from '$lib/components/ui/Button.svelte';
  import MetricCard from '$lib/components/data-display/MetricCard.svelte';
  import Modal from '$lib/components/ui/Modal.svelte';
  import ExportModal from '$lib/components/ui/ExportModal.svelte';
  import ConfirmDialog from '$lib/components/ui/ConfirmDialog.svelte';
  import CurrencyInput from '$lib/components/ui/CurrencyInput.svelte';
  import { products, createProduct, updateProduct, deleteProduct, tenantApi } from '$lib/stores/data';
  import { showToast } from '$lib/stores/toast';
  import { Download } from '@lucide/svelte';

  const slug = $derived($page.params.tenantSlug || '');

  let showModal = $state(false);
  let showExport = $state(false);
  let editingIndex = $state<number | null>(null);
  let deleteIndex = $state<number | null>(null);

  let form = $state({ sku: '', name: '', category: '', unit: 'pcs', minStock: 0, price: 0, cost: 0, status: 'active' });
  let stockMap = $state<Record<string, number>>({});

  $effect(() => {
    if (!slug) return;
    void (async () => {
      try {
        const res: any = await tenantApi.getStockBalances(slug);
        const map: Record<string, number> = {};
        for (const sb of (Array.isArray(res) ? res : [])) {
          map[sb.productId || sb.product_id] = (map[sb.productId || sb.product_id] || 0) + parseFloat(sb.quantity || '0');
        }
        stockMap = map;
      } catch { stockMap = {}; }
    });
  });

  const rows = $derived($products.map((p) => ({ ...p, stock: stockMap[p.id] ?? p.stock ?? 0 })));
  const totalProduk = $derived($products.length);
  const stokKritis = $derived(rows.filter(p => p.stock > 0 && p.stock <= p.minStock).length);
  const nilaiStok = $derived(rows.reduce((s, p) => s + p.stock * p.cost, 0));
  const deadStock = $derived(rows.filter(p => p.stock > 0 && p.stock <= p.minStock / 2).length);

  const exportColumns = [
    { key: 'sku', label: 'SKU' },
    { key: 'name', label: 'Nama Produk' },
    { key: 'category', label: 'Kategori' },
    { key: 'stock', label: 'Stok' },
    { key: 'minStock', label: 'Min. Stok' },
    { key: 'price', label: 'Harga Jual', render: (r: any) => `Rp ${Number(r.price).toLocaleString('id-ID')}` },
    { key: 'cost', label: 'Harga Modal', render: (r: any) => `Rp ${Number(r.cost).toLocaleString('id-ID')}` },
    { key: 'status', label: 'Status' },
  ];

  function openCreate() {
    form = { sku: '', name: '', category: '', unit: 'pcs', minStock: 0, price: 0, cost: 0, status: 'active' };
    editingIndex = null;
    showModal = true;
  }

  function openEdit(i: number) {
    const p = $products[i];
    form = { sku: p.sku, name: p.name, category: p.category || '', unit: p.unit || 'pcs', minStock: p.minStock, price: p.price, cost: p.cost, status: p.status || 'active' };
    editingIndex = i;
    showModal = true;
  }

  async function save() {
    const data = {
      sku: form.sku,
      name: form.name,
      category: form.category,
      unit: form.unit,
      salePrice: String(form.price || '0'),
      costPrice: String(form.cost || '0'),
      minimumStock: String(form.minStock || '0'),
    };
    if (editingIndex !== null) {
      try {
        await updateProduct($products[editingIndex].id, { ...data, status: form.status });
        showToast('Produk berhasil diperbarui', 'success');
        showModal = false;
      } catch (err: any) { showToast(err?.message || 'Gagal memperbarui produk', 'error'); }
    } else {
      try {
        await createProduct(data);
        showToast('Produk berhasil ditambahkan', 'success');
        showModal = false;
      } catch (err: any) { showToast(err?.message || 'Gagal menambahkan produk', 'error'); }
    }
  }

  async function confirmDelete() {
    if (deleteIndex !== null) {
      try { await deleteProduct($products[deleteIndex].id); showToast('Produk berhasil dihapus', 'success'); }
      catch (err: any) { showToast(err?.message || 'Gagal menghapus produk', 'error'); }
      finally { deleteIndex = null; }
    }
  }
</script>

<PageHeader title="Produk" description="Manajemen produk dan SKU" breadcrumbs={[{ label: 'Inventaris' }, { label: 'Produk' }]}>
  {#snippet actions()}
    <Button variant="secondary" onclick={() => showExport = true}><Download class="w-4 h-4" /> Ekspor</Button>
    <Button onclick={openCreate}>+ Produk Baru</Button>
  {/snippet}
</PageHeader>

<div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
  <MetricCard label="Total Produk" value={totalProduk} format="number" />
  <MetricCard label="Stok Kritis" value={stokKritis} format="number" />
  <MetricCard label="Nilai Stok" value={nilaiStok} format="currency" />
  <MetricCard label="Dead Stock" value={deadStock} format="number" />
</div>

<DataTable
  columns={[
    { key: 'sku', label: 'SKU', sortable: true },
    { key: 'name', label: 'Nama', sortable: true },
    { key: 'category', label: 'Kategori' },
    { key: 'stock', label: 'Stok', align: 'right' },
    { key: 'minStock', label: 'Min. Stok', align: 'right' },
    { key: 'price', label: 'Harga Jual', align: 'right', render: (item: any) => `Rp ${item.price.toLocaleString('id-ID')}` },
    { key: 'cost', label: 'Harga Modal', align: 'right', render: (item: any) => `Rp ${item.cost.toLocaleString('id-ID')}` },
    { key: 'status', label: 'Status', render: (item: any) => `<span class="badge-${item.status}">${item.status}</span>` },
  ]}
  data={rows}
  total={totalProduk}
  searchable={true}
>
  {#snippet rowActions(item: any, i: number)}
    <button onclick={() => openEdit(i)} class="text-xs text-[hsl(var(--primary))] hover:underline mr-2">Edit</button>
    <button onclick={() => deleteIndex = i} class="text-xs text-[var(--color-kepin-danger)] hover:underline">Hapus</button>
  {/snippet}
</DataTable>

<Modal title={editingIndex !== null ? 'Edit Produk' : 'Produk Baru'} open={showModal} onclose={() => showModal = false}>
  <form onsubmit={save} class="space-y-4">
    <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
      <div>
        <label class="label-text">SKU</label>
        <input type="text" bind:value={form.sku} class="input-field mt-1" required />
      </div>
      <div>
        <label class="label-text">Kategori</label>
        <input type="text" bind:value={form.category} class="input-field mt-1" required />
      </div>
    </div>
    <div>
      <label class="label-text">Nama Produk</label>
      <input type="text" bind:value={form.name} class="input-field mt-1" required />
    </div>
    <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
      <div>
        <label class="label-text">Satuan</label>
        <input type="text" bind:value={form.unit} class="input-field mt-1" placeholder="pcs" />
      </div>
      <div>
        <label class="label-text">Min. Stok</label>
        <input type="number" min="0" bind:value={form.minStock} class="input-field mt-1" />
      </div>
    </div>
    <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
      <div>
        <label class="label-text">Harga Jual (Rp)</label>
        <CurrencyInput value={form.price} onchange={(v) => form.price = v} class="input-field mt-1" required />
      </div>
      <div>
        <label class="label-text">Harga Modal (Rp)</label>
        <CurrencyInput value={form.cost} onchange={(v) => form.cost = v} class="input-field mt-1" />
      </div>
    </div>
    {#if editingIndex !== null}
      <div>
        <label class="label-text">Status</label>
        <select bind:value={form.status} class="input-field mt-1">
          <option value="active">Aktif</option>
          <option value="inactive">Nonaktif</option>
        </select>
      </div>
    {/if}
    <div class="flex justify-end gap-2 pt-2">
      <Button variant="secondary" type="button" onclick={() => showModal = false}>Batal</Button>
      <Button type="submit">Simpan</Button>
    </div>
  </form>
</Modal>

<ConfirmDialog
  open={deleteIndex !== null}
  onclose={() => deleteIndex = null}
  onconfirm={confirmDelete}
  message="Hapus produk ini? Tindakan ini tidak dapat dibatalkan."
/>

<ExportModal
  open={showExport}
  onclose={() => showExport = false}
  title="Daftar Produk"
  subtitle="Data produk dan inventaris"
  columns={exportColumns}
  rows={rows}
  filename="produk"
/>
