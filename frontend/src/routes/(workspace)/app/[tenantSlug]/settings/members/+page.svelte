<script lang="ts">
  import PageHeader from '$lib/components/layout/PageHeader.svelte';
  import DataTable from '$lib/components/data-display/DataTable.svelte';
  import Button from '$lib/components/ui/Button.svelte';
  import Modal from '$lib/components/ui/Modal.svelte';
  import ConfirmDialog from '$lib/components/ui/ConfirmDialog.svelte';
  import { members, createMember, updateMember, deleteMember, currentRole } from '$lib/stores/data';
  import { showToast } from '$lib/stores/toast';

  let showModal = $state(false);
  let editingIndex = $state<number | null>(null);
  let deleteIndex = $state<number | null>(null);

  let form = $state({ name: '', email: '', role: 'employee', status: 'active' });
  const isOwner = $derived($currentRole === 'tenant_owner');
  const rows = $derived($members.map((m: any, index) => ({
    index,
    id: m.id,
    name: m.user?.name || m.userName || '-',
    email: m.user?.email || m.userEmail || '-',
    role: m.role || m.roleName || '-',
    status: m.status || 'active',
  })));

  function openCreate() {
    if (!isOwner) return;
    form = { name: '', email: '', role: 'employee', status: 'active' };
    editingIndex = null;
    showModal = true;
  }

  function openEdit(i: number) {
    if (!isOwner) return;
    const m = $members[i];
    form = { name: m.user?.name || '', email: m.user?.email || '', role: m.role || m.roleName || 'employee', status: m.status };
    editingIndex = i;
    showModal = true;
  }

  async function save() {
    if (!isOwner) return;
    try {
      if (editingIndex !== null) {
        await updateMember(editingIndex, form as any);
        showToast('Anggota berhasil diperbarui', 'success');
      } else {
        await createMember(form as any);
        showToast('Anggota berhasil diundang', 'success');
      }
      showModal = false;
    } catch (err: any) {
      showToast(err?.message || 'Gagal menyimpan anggota', 'error');
    }
  }

  async function confirmDelete() {
    if (!isOwner) return;
    if (deleteIndex !== null) {
      try {
        await deleteMember(deleteIndex);
        showToast('Anggota berhasil dihapus', 'success');
      } catch (err: any) {
        showToast(err?.message || 'Gagal menghapus anggota', 'error');
      }
      deleteIndex = null;
    }
  }
</script>

<PageHeader title="Anggota Tim" description="Kelola anggota workspace" breadcrumbs={[{ label: 'Pengaturan' }, { label: 'Anggota' }]}>
  {#snippet actions()}
    {#if isOwner}
      <Button onclick={openCreate}>+ Undang Anggota</Button>
    {/if}
  {/snippet}
</PageHeader>

{#if !isOwner}
  <div class="card p-4 mb-6 text-sm text-[hsl(var(--muted-foreground))]">
    Hanya <strong>tenant_owner</strong> yang dapat mengundang, mengubah role, atau menghapus anggota. Daftar anggota ditampilkan read-only.
  </div>
{/if}

<DataTable
  columns={[
    { key: 'name', label: 'Nama', sortable: true },
    { key: 'email', label: 'Email' },
    { key: 'role', label: 'Peran' },
    { key: 'status', label: 'Status', render: (item: any) => `<span class="badge-${item.status}">${item.status}</span>` },
  ]}
  data={rows}
  total={rows.length}
  searchable={true}
>
  {#snippet rowActions(item: any, i: number)}
    {#if isOwner}
      <button onclick={() => openEdit(item.index)} class="text-xs text-[hsl(var(--primary))] hover:underline mr-2">Edit</button>
      <button onclick={() => deleteIndex = item.index} class="text-xs text-[var(--color-kepin-danger)] hover:underline">Hapus</button>
    {/if}
  {/snippet}
</DataTable>

<Modal title={editingIndex !== null ? 'Edit Anggota' : 'Undang Anggota'} open={showModal} onclose={() => showModal = false}>
  <form onsubmit={save} class="space-y-4">
    <div>
      <label class="label-text" for="member-name">Nama</label>
      <input id="member-name" type="text" bind:value={form.name} class="input-field mt-1" required />
    </div>
    <div>
      <label class="label-text" for="member-email">Email</label>
      <input id="member-email" type="email" bind:value={form.email} class="input-field mt-1" required />
    </div>
    <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
      <div>
        <label class="label-text" for="member-role">Peran</label>
        <select id="member-role" bind:value={form.role} class="input-field mt-1">
          <option value="tenant_owner">Owner</option>
          <option value="employee">Employee</option>
        </select>
      </div>
      <div>
        <label class="label-text" for="member-status">Status</label>
        <select id="member-status" bind:value={form.status} class="input-field mt-1">
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
