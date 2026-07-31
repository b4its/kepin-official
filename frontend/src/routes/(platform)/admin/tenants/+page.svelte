<script lang="ts">
  import PageHeader from '$lib/components/layout/PageHeader.svelte';
  import DataTable from '$lib/components/data-display/DataTable.svelte';
  import Button from '$lib/components/ui/Button.svelte';
  import Modal from '$lib/components/ui/Modal.svelte';
  import ConfirmDialog from '$lib/components/ui/ConfirmDialog.svelte';
  import { adminTenants, loadAdminTenants, adminApi } from '$lib/stores/data';
  import { showToast } from '$lib/stores/toast';

  let showModal = $state(false);
  let editingId = $state<string | null>(null);
  let deleteTarget = $state<{ id: string; name: string } | null>(null);
  let saving = $state(false);

  let form = $state({ name: '', slug: '', legalName: '', sector: 'Ritel', timezone: 'Asia/Jakarta', currency: 'IDR' });

  function openCreate() {
    form = { name: '', slug: '', legalName: '', sector: 'Ritel', timezone: 'Asia/Jakarta', currency: 'IDR' };
    editingId = null;
    showModal = true;
  }

  function openEdit(i: number) {
    const t = $adminTenants[i];
    form = { name: t.name, slug: t.slug, legalName: t.legalName, sector: t.sector, timezone: t.timezone, currency: t.currency || 'IDR' };
    editingId = t.id;
    showModal = true;
  }

  async function save() {
    saving = true;
    try {
      if (editingId !== null) {
        await adminApi.updateAdminTenant(editingId, form);
        showToast('Tenant berhasil diperbarui', 'success');
      } else {
        await adminApi.createAdminTenant(form);
        showToast('Tenant berhasil ditambahkan', 'success');
      }
      await loadAdminTenants();
      showModal = false;
    } catch (e: any) {
      showToast(e?.message || 'Gagal menyimpan tenant', 'error');
    } finally {
      saving = false;
    }
  }

  async function confirmDelete() {
    if (!deleteTarget) return;
    try {
      await adminApi.deleteAdminTenant(deleteTarget.id);
      showToast('Tenant dihapus', 'success');
      await loadAdminTenants();
    } catch (e: any) {
      showToast(e?.message || 'Gagal menghapus tenant', 'error');
    }
    deleteTarget = null;
  }

  async function toggleStatus(t: any) {
    try {
      if (t.status === 'active') {
        await adminApi.suspendTenant(t.id);
        showToast('Tenant ditangguhkan', 'success');
      } else {
        await adminApi.reactivateTenant(t.id);
        showToast('Tenant diaktifkan kembali', 'success');
      }
      await loadAdminTenants();
    } catch (e: any) {
      showToast(e?.message || 'Gagal mengubah status', 'error');
    }
  }

  function goToTenant(slug: string) {
    window.location.href = `/app/${slug}`;
  }
</script>

<PageHeader title="Manajemen Tenant" description="Kelola seluruh organisasi pelanggan">
  {#snippet actions()}
    <Button onclick={openCreate}>+ Tenant Baru</Button>
  {/snippet}
</PageHeader>

<DataTable
  columns={[
    { key: 'name', label: 'Nama', sortable: true },
    { key: 'legalName', label: 'Legal', sortable: true },
    { key: 'sector', label: 'Sektor' },
    { key: 'status', label: 'Status', render: (item: any) => `<span class="badge-${item.status}">${item.status}</span>` },
  ]}
  data={$adminTenants}
  total={$adminTenants.length}
  searchable={true}
>
  {#snippet rowActions(item: any, i: number)}
    <button onclick={() => goToTenant(item.slug)} class="text-xs text-[hsl(var(--primary))] hover:underline mr-2">View</button>
    <button onclick={() => openEdit(i)} class="text-xs text-[hsl(var(--primary))] hover:underline mr-2">Edit</button>
    {#if item.status === 'active'}
      <button onclick={() => toggleStatus(item)} class="text-xs text-[hsl(var(--primary))] hover:underline mr-2">Suspend</button>
    {:else if item.status === 'suspended'}
      <button onclick={() => toggleStatus(item)} class="text-xs text-[hsl(var(--primary))] hover:underline mr-2">Reactivate</button>
    {/if}
    <button onclick={() => deleteTarget = { id: item.id, name: item.name }} class="text-xs text-[var(--color-kepin-danger)] hover:underline">Hapus</button>
  {/snippet}
</DataTable>

<Modal title={editingId !== null ? 'Edit Tenant' : 'Tambah Tenant'} open={showModal} onclose={() => showModal = false}>
  <form onsubmit={save} class="space-y-4">
    <div>
      <label class="label-text">Nama Tenant</label>
      <input type="text" bind:value={form.name} class="input-field mt-1" required />
    </div>
    <div>
      <label class="label-text">Slug</label>
      <input type="text" bind:value={form.slug} class="input-field mt-1" required placeholder="nama-perusahaan" disabled={editingId !== null} />
    </div>
    <div>
      <label class="label-text">Nama Legal</label>
      <input type="text" bind:value={form.legalName} class="input-field mt-1" />
    </div>
    <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
      <div>
        <label class="label-text">Sektor</label>
        <select bind:value={form.sector} class="input-field mt-1">
          <option value="Ritel">Ritel</option>
          <option value="F&B">F&B</option>
          <option value="Otomotif">Otomotif</option>
          <option value="Fashion">Fashion</option>
          <option value="Teknologi">Teknologi</option>
          <option value="Jasa">Jasa</option>
        </select>
      </div>
      <div>
        <label class="label-text">Zona Waktu</label>
        <select bind:value={form.timezone} class="input-field mt-1">
          <option value="Asia/Jakarta">Asia/Jakarta (WIB)</option>
          <option value="Asia/Makassar">Asia/Makassar (WITA)</option>
          <option value="Asia/Jayapura">Asia/Jayapura (WIT)</option>
        </select>
      </div>
    </div>
    <div>
      <label class="label-text">Mata Uang</label>
      <select bind:value={form.currency} class="input-field mt-1">
        <option value="IDR">IDR</option>
      </select>
    </div>
    <div class="flex justify-end gap-2 pt-2">
      <Button variant="secondary" type="button" onclick={() => showModal = false}>Batal</Button>
      <Button type="submit" disabled={saving}>Simpan</Button>
    </div>
  </form>
</Modal>

<ConfirmDialog
  open={deleteTarget !== null}
  onclose={() => deleteTarget = null}
  onconfirm={confirmDelete}
  title="Hapus Tenant"
  message={`Apakah Anda yakin ingin menghapus tenant "${deleteTarget?.name ?? ''}"? Seluruh datanya akan terhapus permanen.`}
  confirmText="Hapus"
/>
