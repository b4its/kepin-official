<script lang="ts">
  import PageHeader from '$lib/components/layout/PageHeader.svelte';
  import DataTable from '$lib/components/data-display/DataTable.svelte';
  import Button from '$lib/components/ui/Button.svelte';
  import Modal from '$lib/components/ui/Modal.svelte';
  import ExportModal from '$lib/components/ui/ExportModal.svelte';
  import ConfirmDialog from '$lib/components/ui/ConfirmDialog.svelte';
  import StatementModal from '$lib/components/ui/StatementModal.svelte';
  import { customers, createCustomer, updateCustomer, deleteCustomer, tenantApi } from '$lib/stores/data';
  import { showToast } from '$lib/stores/toast';
  import { Download, Search } from '@lucide/svelte';
  import { page } from '$app/stores';

  const slug = $derived($page.params.tenantSlug || '');

  let items = $state<any[]>([]);
  let search = $state('');
  let loading = $state(false);
  let searchTimer: ReturnType<typeof setTimeout> | undefined;

  async function loadCatalog(q = search) {
    loading = true;
    try {
      const res: any = await tenantApi.getCustomers(slug, q || undefined);
      items = (res.items ?? []).map((c: any) => ({
        id: c.id, code: c.code || '', name: c.name, email: c.email || '', phone: c.phone || '', address: c.address || '', createdAt: c.createdAt,
      }));
    } catch {
      /* biarkan data lama */
    } finally {
      loading = false;
    }
  }

  $effect(() => {
    if (!slug) return;
    clearTimeout(searchTimer);
    searchTimer = setTimeout(() => void loadCatalog(search), search ? 250 : 0);
    return () => clearTimeout(searchTimer);
  });

  let showModal = $state(false);
  let showExport = $state(false);
  let editingIndex = $state<number | null>(null);
  let deleteIndex = $state<number | null>(null);

  let showStatement = $state(false);
  let statementCustomer = $state<{ id: string; code: string; name: string } | null>(null);

  let form = $state({ code: '', name: '', email: '', phone: '', address: '' });

  const exportColumns = [
    { key: 'code', label: 'Kode' },
    { key: 'name', label: 'Nama' },
    { key: 'email', label: 'Email' },
    { key: 'phone', label: 'Telepon' },
    { key: 'address', label: 'Alamat' },
    { key: 'createdAt', label: 'Bergabung' },
  ];

  function openCreate() {
    form = { code: '', name: '', email: '', phone: '', address: '' };
    editingIndex = null;
    showModal = true;
  }

  function openEdit(i: number) {
    const item = items[i];
    form = { code: item.code || '', name: item.name, email: item.email, phone: item.phone, address: item.address };
    editingIndex = i;
    showModal = true;
  }

  async function save() {
    const data = { code: form.code, name: form.name, email: form.email, phone: form.phone, address: form.address };
    if (editingIndex !== null) {
      await updateCustomer(items[editingIndex].id, data);
      showToast('Pelanggan berhasil diperbarui', 'success');
    } else {
      await createCustomer(data);
      showToast('Pelanggan berhasil ditambahkan', 'success');
    }
    showModal = false;
    void loadCatalog();
  }

  async function confirmDelete() {
    if (deleteIndex !== null) {
      await deleteCustomer(items[deleteIndex].id);
      deleteIndex = null;
      showToast('Pelanggan berhasil dihapus', 'success');
      void loadCatalog();
    }
  }

  async function openStatement(item: { id: string; code: string; name: string }) {
    statementCustomer = { id: item.id, code: item.code, name: item.name };
    showStatement = true;
  }
</script>

<PageHeader title="Pelanggan" description="Daftar pelanggan" breadcrumbs={[{ label: 'Penjualan' }, { label: 'Pelanggan' }]}>
  {#snippet actions()}
    <Button variant="secondary" onclick={() => showExport = true}><Download class="w-4 h-4" /> Ekspor</Button>
    <Button onclick={openCreate}>+ Pelanggan Baru</Button>
  {/snippet}
</PageHeader>

<div class="flex items-center gap-2 mb-4 card px-3 py-2">
  <Search class="w-4 h-4 shrink-0 text-[hsl(var(--muted-foreground))]" />
  <input
    type="search"
    bind:value={search}
    placeholder="Cari..."
    class="flex-1 bg-transparent border-none outline-none text-sm placeholder:text-[hsl(var(--muted-foreground))]"
  />
</div>

<DataTable
  tourHook="customers-table"
  columns={[
    { key: 'code', label: 'Kode', sortable: true },
    { key: 'name', label: 'Nama', sortable: true },
    { key: 'email', label: 'Email' },
    { key: 'phone', label: 'Telepon' },
    { key: 'createdAt', label: 'Bergabung' },
  ]}
  data={items}
  total={items.length}
  loading={loading}
>
  {#snippet rowActions(item: any, i: number)}
    <button onclick={() => openStatement(item)} class="text-xs text-[hsl(var(--primary))] hover:underline mr-2">Statement</button>
    <button onclick={() => openEdit(i)} class="text-xs text-[hsl(var(--primary))] hover:underline mr-2">Edit</button>
    <button onclick={() => deleteIndex = i} class="text-xs text-[var(--color-kepin-danger)] hover:underline">Hapus</button>
  {/snippet}
</DataTable>

<Modal title={editingIndex !== null ? 'Edit Pelanggan' : 'Pelanggan Baru'} open={showModal} onclose={() => showModal = false}>
  <form onsubmit={save} class="space-y-4">
    <div>
      <label class="label-text">Kode</label>
      <input type="text" bind:value={form.code} class="input-field mt-1" placeholder="cth: CUS-001" required />
    </div>
    <div>
      <label class="label-text">Nama</label>
      <input type="text" bind:value={form.name} class="input-field mt-1" required />
    </div>
    <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
      <div>
        <label class="label-text">Email</label>
        <input type="email" bind:value={form.email} class="input-field mt-1" required />
      </div>
      <div>
        <label class="label-text">Telepon</label>
        <input type="text" bind:value={form.phone} class="input-field mt-1" required />
      </div>
    </div>
    <div>
      <label class="label-text">Alamat</label>
      <input type="text" bind:value={form.address} class="input-field mt-1" />
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
  message="Hapus pelanggan ini? Tindakan ini tidak dapat dibatalkan."
/>

<StatementModal
  kind="customer"
  open={showStatement}
  entityId={statementCustomer?.id ?? ''}
  entityCode={statementCustomer?.code ?? ''}
  entityName={statementCustomer?.name ?? ''}
  onclose={() => showStatement = false}
/>

<ExportModal
  open={showExport}
  onclose={() => showExport = false}
  title="Daftar Pelanggan"
  subtitle="Data pelanggan aktif"
  columns={exportColumns}
  rows={$customers}
  filename="pelanggan"
/>
