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
  import { createProduct, updateProduct, deleteProduct, tenantApi } from '$lib/stores/data';
  import { showToast } from '$lib/stores/toast';
  import { Download, Search } from '@lucide/svelte';

  const slug = $derived($page.params.tenantSlug || '');

  let showModal = $state(false);
  let showExport = $state(false);
  let editingId = $state<string | null>(null);
  let deleteId = $state<string | null>(null);

  let rows = $state<any[]>([]);
  let search = $state('');
  let pageNo = $state(1);
  let total = $state(0);
  let loading = $state(false);
  let searchTimer: ReturnType<typeof setTimeout> | undefined;
  const PAGE_SIZE = 20;

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

  async function load(q = search, p = pageNo) {
    loading = true;
    try {
      const res: any = await tenantApi.getProducts(slug, q || undefined, PAGE_SIZE, p);
      const items = Array.isArray(res.items) ? res.items : [];
      rows = items.map((prod: any) => ({
        id: prod.id,
        sku: prod.sku || '',
        name: prod.name,
        category: prod.category || '',
        unit: prod.unit || 'pcs',
        price: parseFloat(prod.salePrice || prod.sale_price || '0'),
        cost: parseFloat(prod.costPrice || prod.cost_price || '0'),
        minStock: parseFloat(prod.minimumStock || prod.minimum_stock || '0'),
        status: prod.status || 'active',
        stock: stockMap[prod.id] ?? 0,
      }));
      total = res.total ?? 0;
    } catch {
      /* biarkan data lama */
    } finally {
      loading = false;
    }
  }

  $effect(() => {
    if (!slug) return;
    void stockMap;
    clearTimeout(searchTimer);
    searchTimer = setTimeout(() => {
      pageNo = 1;
      void load(search, 1);
    }, search ? 250 : 0);
    return () => clearTimeout(searchTimer);
  });

  const totalProduk = $derived(total);
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
    editingId = null;
    showModal = true;
  }

  function openEdit(row: any) {
    form = { sku: row.sku, name: row.name, category: row.category || '', unit: row.unit || 'pcs', minStock: row.minStock, price: row.price, cost: row.cost, status: row.status || 'active' };
    editingId = row.id;
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
    if (editingId !== null) {
      try {
        await updateProduct(editingId, { ...data, status: form.status });
        showToast('Produk berhasil diperbarui', 'success');
        showModal = false;
        void load(search, pageNo);
      } catch (err: any) { showToast(err?.message || 'Gagal memperbarui produk', 'error'); }
    } else {
      try {
        await createProduct(data);
        showToast('Produk berhasil ditambahkan', 'success');
        showModal = false;
        void load(search, pageNo);
      } catch (err: any) { showToast(err?.message || 'Gagal menambahkan produk', 'error'); }
    }
  }

  async function confirmDelete() {
    if (deleteId !== null) {
      try {
        await deleteProduct(deleteId);
        showToast('Produk berhasil dihapus', 'success');
        void load(search, pageNo);
      }
      catch (err: any) { showToast(err?.message || 'Gagal menghapus produk', 'error'); }
      finally { deleteId = null; }
    }
  }
</script>

<PageHeader title="Produk" description="Manajemen produk dan SKU" breadcrumbs={[{ label: 'Inventaris' }, { label: 'Produk' }]}>
  {#snippet actions()}
    <Button variant="secondary" onclick={() => showExport = true}><Download class="w-4 h-4" /> Ekspor</Button>
    <Button onclick={openCreate} tourHook="add-product">+ Produk Baru</Button>
  {/snippet}
</PageHeader>

<div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
  <MetricCard label="Total Produk" value={totalProduk} format="number" />
  <MetricCard label="Stok Kritis" value={stokKritis} format="number" />
  <MetricCard label="Nilai Stok" value={nilaiStok} format="currency" />
  <MetricCard label="Dead Stock" value={deadStock} format="number" />
</div>

<div class="flex items-center gap-2 mb-4 card px-3 py-2">
  <Search class="w-4 h-4 shrink-0 text-[hsl(var(--muted-foreground))]" />
  <input
    type="search"
    bind:value={search}
    placeholder="Cari nama, SKU, kategori..."
    class="flex-1 bg-transparent border-none outline-none text-sm placeholder:text-[hsl(var(--muted-foreground))]"
  />
</div>

<DataTable
  columns={[
    { key: 'sku', label: 'SKU', sortable: false },
    { key: 'name', label: 'Nama' },
    { key: 'category', label: 'Kategori' },
    { key: 'stock', label: 'Stok', align: 'right' },
    { key: 'minStock', label: 'Min. Stok', align: 'right' },
    { key: 'price', label: 'Harga Jual', align: 'right', render: (item: any) => `Rp ${item.price.toLocaleString('id-ID')}` },
    { key: 'cost', label: 'Harga Modal', align: 'right', render: (item: any) => `Rp ${item.cost.toLocaleString('id-ID')}` },
    { key: 'status', label: 'Status', render: (item: any) => `<span class="badge-${item.status}">${item.status}</span>` },
  ]}
  data={rows}
  loading={loading}
  total={total}
  page={pageNo}
  pageSize={PAGE_SIZE}
  tourHook="products-table"
  onpagechange={(p) => { pageNo = p; void load(search, p); }}
>
  {#snippet rowActions(item: any)}
    <button onclick={() => openEdit(item)} class="text-xs text-[hsl(var(--primary))] hover:underline mr-2">Edit</button>
    <button onclick={() => deleteId = item.id} class="text-xs text-[var(--color-kepin-danger)] hover:underline">Hapus</button>
  {/snippet}
</DataTable>

<Modal title={editingId !== null ? 'Edit Produk' : 'Produk Baru'} open={showModal} onclose={() => showModal = false}>
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
    {#if editingId !== null}
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
  open={deleteId !== null}
  onclose={() => deleteId = null}
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
