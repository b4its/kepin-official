<script lang="ts">
  import PageHeader from '$lib/components/layout/PageHeader.svelte';
  import DataTable from '$lib/components/data-display/DataTable.svelte';
  import Button from '$lib/components/ui/Button.svelte';
  import Modal from '$lib/components/ui/Modal.svelte';
  import ConfirmDialog from '$lib/components/ui/ConfirmDialog.svelte';
  import { customers, createCustomer, updateCustomer, deleteCustomer } from '$lib/stores/data';

  let showModal = $state(false);
  let editingIndex = $state<number | null>(null);
  let deleteIndex = $state<number | null>(null);

  let form = $state({ name: '', email: '', phone: '', address: '', totalTrans: 0, totalAmount: 0, lastTrans: '' });

  function openCreate() {
    form = { name: '', email: '', phone: '', address: '', totalTrans: 0, totalAmount: 0, lastTrans: '' };
    editingIndex = null;
    showModal = true;
  }

  function openEdit(i: number) {
    const item = $customers[i];
    form = { name: item.name, email: item.email, phone: item.phone, address: item.address, totalTrans: 0, totalAmount: 0, lastTrans: '' };
    editingIndex = i;
    showModal = true;
  }

  function save() {
    const data = { name: form.name, email: form.email, phone: form.phone, address: form.address };
    if (editingIndex !== null) {
      updateCustomer($customers[editingIndex].id, data);
    } else {
      createCustomer(data);
    }
    showModal = false;
  }

  function confirmDelete() {
    if (deleteIndex !== null) {
      deleteCustomer($customers[deleteIndex].id);
      deleteIndex = null;
    }
  }
</script>

<PageHeader title="Pelanggan" description="Daftar pelanggan" breadcrumbs={[{ label: 'Penjualan' }, { label: 'Pelanggan' }]}>
  {#snippet actions()}
    <Button onclick={openCreate}>+ Pelanggan Baru</Button>
  {/snippet}
</PageHeader>

<DataTable
  columns={[
    { key: 'name', label: 'Nama', sortable: true },
    { key: 'email', label: 'Email' },
    { key: 'phone', label: 'Telepon' },
    { key: 'createdAt', label: 'Bergabung' },
  ]}
  data={$customers}
  total={24}
  searchable={true}
>
  {#snippet rowActions(item: any, i: number)}
    <button onclick={() => openEdit(i)} class="text-xs text-[hsl(var(--primary))] hover:underline mr-2">Edit</button>
    <button onclick={() => deleteIndex = i} class="text-xs text-[var(--color-kepin-danger)] hover:underline">Hapus</button>
  {/snippet}
</DataTable>

<Modal title={editingIndex !== null ? 'Edit Pelanggan' : 'Pelanggan Baru'} open={showModal} onclose={() => showModal = false}>
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
