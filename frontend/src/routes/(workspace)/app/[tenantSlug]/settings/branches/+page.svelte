<script lang="ts">
  import PageHeader from '$lib/components/layout/PageHeader.svelte';
  import DataTable from '$lib/components/data-display/DataTable.svelte';
  import Button from '$lib/components/ui/Button.svelte';
  import Modal from '$lib/components/ui/Modal.svelte';
  import ConfirmDialog from '$lib/components/ui/ConfirmDialog.svelte';
  import { branches, createBranch, updateBranch, deleteBranch } from '$lib/stores/data';
  import { showToast } from '$lib/stores/toast';

  let showModal = $state(false);
  let editingIndex = $state<number | null>(null);
  let deleteIndex = $state<number | null>(null);

  let form = $state({ name: '', code: '', address: '', status: 'active' });

  function openCreate() {
    form = { name: '', code: '', address: '', status: 'active' };
    editingIndex = null;
    showModal = true;
  }

  function openEdit(i: number) {
    const b = $branches[i];
    form = { name: b.name, code: b.code, address: b.address || '', status: b.status || 'active' };
    editingIndex = i;
    showModal = true;
  }

  async function save() {
    const data = { name: form.name, code: form.code, address: form.address };
    if (editingIndex !== null) {
      try {
        await updateBranch($branches[editingIndex].id, { ...data, status: form.status });
        showToast('Cabang berhasil diperbarui', 'success');
        showModal = false;
      } catch (err: any) { showToast(err?.message || 'Gagal memperbarui cabang', 'error'); }
    } else {
      try {
        await createBranch(data);
        showToast('Cabang berhasil ditambahkan', 'success');
        showModal = false;
      } catch (err: any) { showToast(err?.message || 'Gagal menambahkan cabang', 'error'); }
    }
  }

  async function confirmDelete() {
    if (deleteIndex !== null) {
      try { await deleteBranch($branches[deleteIndex].id); showToast('Cabang berhasil dihapus', 'success'); }
      catch (err: any) { showToast(err?.message || 'Gagal menghapus cabang', 'error'); }
      finally { deleteIndex = null; }
    }
  }
</script>

<PageHeader title="Cabang" description="Manajemen cabang bisnis" breadcrumbs={[{ label: 'Pengaturan' }, { label: 'Cabang' }]}>
  {#snippet actions()}
    <Button onclick={openCreate}>+ Cabang Baru</Button>
  {/snippet}
</PageHeader>

<DataTable
  tourHook="branches-table"
  columns={[
    { key: 'name', label: 'Nama Cabang', sortable: true },
    { key: 'code', label: 'Kode' },
    { key: 'address', label: 'Alamat' },
    { key: 'isMain', label: 'Pusat', render: (item: any) => item.isMain ? 'Ya' : 'Tidak' },
    { key: 'status', label: 'Status', render: (item: any) => `<span class="badge-${item.status}">${item.status}</span>` },
  ]}
  data={$branches}
  total={$branches.length}
  searchable={true}
>
  {#snippet rowActions(item: any, i: number)}
    <button onclick={() => openEdit(i)} class="text-xs text-[hsl(var(--primary))] hover:underline mr-2">Edit</button>
    <button onclick={() => deleteIndex = i} class="text-xs text-[var(--color-kepin-danger)] hover:underline">Hapus</button>
  {/snippet}
</DataTable>

<Modal title={editingIndex !== null ? 'Edit Cabang' : 'Cabang Baru'} open={showModal} onclose={() => showModal = false}>
  <form onsubmit={save} class="space-y-4">
    <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
      <div>
        <label class="label-text">Nama Cabang</label>
        <input type="text" bind:value={form.name} class="input-field mt-1" required />
      </div>
      <div>
        <label class="label-text">Kode</label>
        <input type="text" bind:value={form.code} class="input-field mt-1" required />
      </div>
    </div>
    <div>
      <label class="label-text">Alamat</label>
      <input type="text" bind:value={form.address} class="input-field mt-1" />
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
  message="Hapus cabang ini? Tindakan ini tidak dapat dibatalkan."
/>
