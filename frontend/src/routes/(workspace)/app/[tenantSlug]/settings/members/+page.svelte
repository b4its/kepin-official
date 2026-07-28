<script lang="ts">
  import PageHeader from '$lib/components/layout/PageHeader.svelte';
  import DataTable from '$lib/components/data-display/DataTable.svelte';
  import Button from '$lib/components/ui/Button.svelte';
  import Modal from '$lib/components/ui/Modal.svelte';
  import ConfirmDialog from '$lib/components/ui/ConfirmDialog.svelte';
  import { members, createMember, updateMember, deleteMember } from '$lib/stores/data';
  import { showToast } from '$lib/stores/toast';

  let showModal = $state(false);
  let editingIndex = $state<number | null>(null);
  let deleteIndex = $state<number | null>(null);

  let form = $state({ name: '', email: '', role: 'Staff', status: 'active' });

  function openCreate() {
    form = { name: '', email: '', role: 'Staff', status: 'active' };
    editingIndex = null;
    showModal = true;
  }

  function openEdit(i: number) {
    const m = $members[i];
    form = { name: m.user.name, email: m.user.email, role: m.role, status: m.status };
    editingIndex = i;
    showModal = true;
  }

  async function save() {
    if (editingIndex !== null) {
      await updateMember(editingIndex, form as any);
      showToast('Anggota berhasil diperbarui', 'success');
    } else {
      await createMember(form as any);
      showToast('Anggota berhasil diundang', 'success');
    }
    showModal = false;
  }

  async function confirmDelete() {
    if (deleteIndex !== null) {
      await deleteMember(deleteIndex);
      deleteIndex = null;
      showToast('Anggota berhasil dihapus', 'success');
    }
  }
</script>

<PageHeader title="Anggota Tim" description="Kelola anggota workspace" breadcrumbs={[{ label: 'Pengaturan' }, { label: 'Anggota' }]}>
  {#snippet actions()}
    <Button onclick={openCreate}>+ Undang Anggota</Button>
  {/snippet}
</PageHeader>

<DataTable
  columns={[
    { key: 'name', label: 'Nama', sortable: true },
    { key: 'email', label: 'Email' },
    { key: 'role', label: 'Peran' },
    { key: 'status', label: 'Status', render: (item: any) => `<span class="badge-${item.status}">${item.status}</span>` },
  ]}
  data={$members}
  total={$members.length}
  searchable={true}
>
  {#snippet rowActions(item: any, i: number)}
    <button onclick={() => openEdit(i)} class="text-xs text-[hsl(var(--primary))] hover:underline mr-2">Edit</button>
    <button onclick={() => deleteIndex = i} class="text-xs text-[var(--color-kepin-danger)] hover:underline">Hapus</button>
  {/snippet}
</DataTable>

<Modal title={editingIndex !== null ? 'Edit Anggota' : 'Undang Anggota'} open={showModal} onclose={() => showModal = false}>
  <form onsubmit={save} class="space-y-4">
    <div>
      <label class="label-text">Nama</label>
      <input type="text" bind:value={form.name} class="input-field mt-1" required />
    </div>
    <div>
      <label class="label-text">Email</label>
      <input type="email" bind:value={form.email} class="input-field mt-1" required />
    </div>
    <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
      <div>
        <label class="label-text">Peran</label>
        <select bind:value={form.role} class="input-field mt-1">
          <option value="Owner">Owner</option>
          <option value="Admin">Admin</option>
          <option value="Finance">Finance</option>
          <option value="Staff">Staff</option>
        </select>
      </div>
      <div>
        <label class="label-text">Status</label>
        <select bind:value={form.status} class="input-field mt-1">
          <option value="active">Aktif</option>
          <option value="inactive">Nonaktif</option>
        </select>
      </div>
    </div>
    <div class="flex justify-end gap-2 pt-2">
      <Button variant="secondary" type="button" onclick={() => showModal = false}>Batal</Button>
      <Button type="submit">{editingIndex !== null ? 'Simpan' : 'Undang'}</Button>
    </div>
  </form>
</Modal>

<ConfirmDialog
  open={deleteIndex !== null}
  onclose={() => deleteIndex = null}
  onconfirm={confirmDelete}
  message="Hapus anggota ini? Tindakan ini tidak dapat dibatalkan."
/>
