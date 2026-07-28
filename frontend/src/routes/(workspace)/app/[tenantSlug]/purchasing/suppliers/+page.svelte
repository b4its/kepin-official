<script lang="ts">
  import PageHeader from '$lib/components/layout/PageHeader.svelte';
  import DataTable from '$lib/components/data-display/DataTable.svelte';
  import Button from '$lib/components/ui/Button.svelte';
  import Modal from '$lib/components/ui/Modal.svelte';
  import ExportModal from '$lib/components/ui/ExportModal.svelte';
  import ConfirmDialog from '$lib/components/ui/ConfirmDialog.svelte';
  import { suppliers, createSupplier, updateSupplier, deleteSupplier } from '$lib/stores/data';
  import { showToast } from '$lib/stores/toast';
  import { Download } from '@lucide/svelte';

  let showModal = $state(false);
  let showExport = $state(false);
  let editingIndex = $state<number | null>(null);
  let deleteIndex = $state<number | null>(null);

  let form = $state({ name: '', email: '', phone: '', address: '' });

  const exportColumns = [
    { key: 'name', label: 'Nama' },
    { key: 'email', label: 'Email' },
    { key: 'phone', label: 'Telepon' },
    { key: 'address', label: 'Kota' },
    { key: 'createdAt', label: 'Bergabung' },
  ];

  function openCreate() {
    form = { name: '', email: '', phone: '', address: '' };
    editingIndex = null;
    showModal = true;
  }

  function openEdit(i: number) {
    const item = $suppliers[i];
    form = { name: item.name, email: item.email, phone: item.phone, address: item.address };
    editingIndex = i;
    showModal = true;
  }

  async function save() {
    const data = { name: form.name, email: form.email, phone: form.phone, address: form.address };
    if (editingIndex !== null) {
      await updateSupplier($suppliers[editingIndex].id, data);
      showToast('Pemasok berhasil diperbarui', 'success');
    } else {
      await createSupplier(data);
      showToast('Pemasok berhasil ditambahkan', 'success');
    }
    showModal = false;
  }

  async function confirmDelete() {
    if (deleteIndex !== null) {
      await deleteSupplier($suppliers[deleteIndex].id);
      deleteIndex = null;
      showToast('Pemasok berhasil dihapus', 'success');
    }
  }
</script>

<PageHeader title="Pemasok" description="Daftar pemasok" breadcrumbs={[{ label: 'Pembelian' }, { label: 'Pemasok' }]}>
  {#snippet actions()}
    <Button variant="secondary" onclick={() => showExport = true}><Download class="w-4 h-4" /> Ekspor</Button>
    <Button onclick={openCreate}>+ Pemasok Baru</Button>
  {/snippet}
</PageHeader>

<DataTable
  columns={[
    { key: 'name', label: 'Nama', sortable: true },
    { key: 'email', label: 'Email' },
    { key: 'phone', label: 'Telepon' },
    { key: 'address', label: 'Kota' },
    { key: 'createdAt', label: 'Bergabung' },
  ]}
  data={$suppliers}
  total={$suppliers.length}
  searchable={true}
>
  {#snippet rowActions(item: any, i: number)}
    <button onclick={() => openEdit(i)} class="text-xs text-[hsl(var(--primary))] hover:underline mr-2">Edit</button>
    <button onclick={() => deleteIndex = i} class="text-xs text-[var(--color-kepin-danger)] hover:underline">Hapus</button>
  {/snippet}
</DataTable>

<Modal title={editingIndex !== null ? 'Edit Pemasok' : 'Pemasok Baru'} open={showModal} onclose={() => showModal = false}>
  <form onsubmit={save} class="space-y-4">
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
      <label class="label-text">Kota</label>
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
  message="Hapus pemasok ini? Tindakan ini tidak dapat dibatalkan."
/>

<ExportModal
  open={showExport}
  onclose={() => showExport = false}
  title="Daftar Pemasok"
  subtitle="Data pemasok aktif"
  columns={exportColumns}
  rows={$suppliers}
  filename="pemasok"
/>
