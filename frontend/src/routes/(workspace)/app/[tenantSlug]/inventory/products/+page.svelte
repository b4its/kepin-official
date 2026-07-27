<script lang="ts">
  import PageHeader from '$lib/components/layout/PageHeader.svelte';
  import DataTable from '$lib/components/data-display/DataTable.svelte';
  import Button from '$lib/components/ui/Button.svelte';
  import MetricCard from '$lib/components/data-display/MetricCard.svelte';
  import Modal from '$lib/components/ui/Modal.svelte';
  import ExportModal from '$lib/components/ui/ExportModal.svelte';
  import ConfirmDialog from '$lib/components/ui/ConfirmDialog.svelte';
  import CurrencyInput from '$lib/components/ui/CurrencyInput.svelte';
  import { products, createProduct, updateProduct, deleteProduct } from '$lib/stores/data';
  import { Download } from '@lucide/svelte';

  let showModal = $state(false);
  let showExport = $state(false);
  let editingIndex = $state<number | null>(null);
  let deleteIndex = $state<number | null>(null);

  let form = $state({ sku: '', name: '', category: '', stock: 0, minStock: 0, price: 0, cost: 0, status: 'active' });

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
    form = { sku: '', name: '', category: '', stock: 0, minStock: 0, price: 0, cost: 0, status: 'active' };
    editingIndex = null;
    showModal = true;
  }

  function openEdit(i: number) {
    form = { ...$products[i] };
    editingIndex = i;
    showModal = true;
  }

  function save() {
    if (editingIndex !== null) {
      updateProduct($products[editingIndex].id, form);
    } else {
      createProduct(form);
    }
    showModal = false;
  }

  function confirmDelete() {
    if (deleteIndex !== null) {
      deleteProduct($products[deleteIndex].id);
      deleteIndex = null;
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
  <MetricCard label="Total Produk" value={24} format="number" />
  <MetricCard label="Stok Kritis" value={1} format="number" />
  <MetricCard label="Nilai Stok" value={38500000} format="currency" />
  <MetricCard label="Dead Stock" value={3} format="number" />
</div>

<DataTable
  columns={[
    { key: 'sku', label: 'SKU', sortable: true },
    { key: 'name', label: 'Nama', sortable: true },
    { key: 'category', label: 'Kategori' },
    { key: 'stock', label: 'Stok', align: 'right' },
    { key: 'price', label: 'Harga', align: 'right', render: (item: any) => `Rp ${item.price.toLocaleString('id-ID')}` },
    { key: 'status', label: 'Status', render: (item: any) => `<span class="badge-${item.status}">${item.status}</span>` },
  ]}
  data={$products}
  total={24}
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
        <label class="label-text">Harga Jual (Rp)</label>
        <CurrencyInput value={form.price} onchange={(v) => form.price = v} class="input-field mt-1" required />
      </div>
      <div>
        <label class="label-text">Harga Modal (Rp)</label>
        <CurrencyInput value={form.cost} onchange={(v) => form.cost = v} class="input-field mt-1" />
      </div>
    </div>
    <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
      <div>
        <label class="label-text">Stok</label>
        <input type="number" bind:value={form.stock} class="input-field mt-1" required />
      </div>
      <div>
        <label class="label-text">Min. Stok</label>
        <input type="number" bind:value={form.minStock} class="input-field mt-1" required />
      </div>
    </div>
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
  rows={$products}
  filename="produk"
/>
