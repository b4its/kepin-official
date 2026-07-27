<script lang="ts">
  import PageHeader from '$lib/components/layout/PageHeader.svelte';
  import DataTable from '$lib/components/data-display/DataTable.svelte';
  import Button from '$lib/components/ui/Button.svelte';
  import Modal from '$lib/components/ui/Modal.svelte';
  import ConfirmDialog from '$lib/components/ui/ConfirmDialog.svelte';
  import { adminTenants } from '$lib/stores/data';

  let showModal = $state(false);
  let editingIndex = $state<number | null>(null);
  let deleteIndex = $state<number | null>(null);

  let form = $state({ name: '', slug: '', legalName: '', sector: 'Ritel', timezone: 'Asia/Jakarta', plan: 'Pro', status: 'active' });

  function openCreate() {
    form = { name: '', slug: '', legalName: '', sector: 'Ritel', timezone: 'Asia/Jakarta', plan: 'Pro', status: 'active' };
    editingIndex = null;
    showModal = true;
  }

  function openEdit(i: number) {
    const t = $adminTenants[i];
    form = { name: t.name, slug: t.slug, legalName: t.legalName, sector: t.sector, timezone: t.timezone, plan: t.plan, status: t.status };
    editingIndex = i;
    showModal = true;
  }

  function save() {
    adminTenants.update((list: any[]) => {
      if (editingIndex !== null) {
        return list.map((t, i) => i === editingIndex ? { ...t, ...form } : t);
      } else {
        return [...list, { id: 'TEN-'+String(Date.now()).slice(-6), ...form, createdAt: new Date().toISOString() }];
      }
    });
    showModal = false;
  }

  function confirmDelete() {
    if (deleteIndex !== null) {
      adminTenants.update((list: any[]) => list.filter((_, i) => i !== deleteIndex));
      deleteIndex = null;
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
    { key: 'plan', label: 'Paket' },
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
    <button onclick={() => deleteIndex = i} class="text-xs text-[var(--color-kepin-danger)] hover:underline">Hapus</button>
  {/snippet}
</DataTable>

<Modal title={editingIndex !== null ? 'Edit Tenant' : 'Tambah Tenant'} open={showModal} onclose={() => showModal = false}>
  <form onsubmit={save} class="space-y-4">
    <div>
      <label class="label-text">Nama Tenant</label>
      <input type="text" bind:value={form.name} class="input-field mt-1" required />
    </div>
    <div>
      <label class="label-text">Slug</label>
      <input type="text" bind:value={form.slug} class="input-field mt-1" required placeholder="nama-perusahaan" />
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
        <label class="label-text">Paket</label>
        <select bind:value={form.plan} class="input-field mt-1">
          <option value="Trial">Trial</option>
          <option value="Basic">Basic</option>
          <option value="Pro">Pro</option>
          <option value="Enterprise">Enterprise</option>
        </select>
      </div>
    </div>
    <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
      <div>
        <label class="label-text">Zona Waktu</label>
        <select bind:value={form.timezone} class="input-field mt-1">
          <option value="Asia/Jakarta">Asia/Jakarta (WIB)</option>
          <option value="Asia/Makassar">Asia/Makassar (WITA)</option>
          <option value="Asia/Jayapura">Asia/Jayapura (WIT)</option>
        </select>
      </div>
      <div>
        <label class="label-text">Status</label>
        <select bind:value={form.status} class="input-field mt-1">
          <option value="active">Aktif</option>
          <option value="trial">Trial</option>
          <option value="suspended">Ditangguhkan</option>
        </select>
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
  title="Hapus Tenant"
  message="Apakah Anda yakin ingin menghapus tenant ini? Tindakan ini tidak dapat dibatalkan."
  confirmText="Hapus"
/>
