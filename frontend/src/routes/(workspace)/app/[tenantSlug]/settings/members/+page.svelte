<script lang="ts">
  import PageHeader from '$lib/components/layout/PageHeader.svelte';
  import DataTable from '$lib/components/data-display/DataTable.svelte';
  import Button from '$lib/components/ui/Button.svelte';
  import Modal from '$lib/components/ui/Modal.svelte';
  import ConfirmDialog from '$lib/components/ui/ConfirmDialog.svelte';
  import { members, createMember, updateMember, deleteMember, currentRole } from '$lib/stores/data';
  import { showToast } from '$lib/stores/toast';
  import { getJoinCode, regenerateJoinCode } from '$lib/api/tenants';
  import { page } from '$app/stores';
  import { KeyRound, Copy, Check, RefreshCw, ExternalLink } from '@lucide/svelte';

  let showModal = $state(false);
  let editingIndex = $state<number | null>(null);
  let deleteIndex = $state<number | null>(null);

  let form = $state({ name: '', email: '', role: 'employee', status: 'active' });
  const isOwner = $derived($currentRole === 'tenant_owner');
  const slug = $derived($page.params.tenantSlug || '');
  const rows = $derived($members.map((m: any, index) => ({
    index,
    id: m.id,
    name: m.user?.name || m.userName || '-',
    email: m.user?.email || m.userEmail || '-',
    role: m.role || m.roleName || '-',
    status: m.status || 'active',
  })));

  // ── Kode Bergabung (endpoint tenant-scoped — tidak dibaca dari localStorage) ──
  let joinCode = $state('');
  let copied = $state(false);
  let codeLoading = $state(false);
  let regenerating = $state(false);
  let codeError = $state('');

  $effect(() => {
    if (!isOwner || !slug) return;
    codeLoading = true;
    codeError = '';
    getJoinCode(slug)
      .then((res: any) => { joinCode = res?.joinCode || ''; })
      .catch((err: any) => { codeError = err?.message || 'Gagal memuat kode bergabung'; })
      .finally(() => { codeLoading = false; });
  });

  async function copyCode() {
    if (!joinCode) return;
    try {
      await navigator.clipboard.writeText(joinCode);
      copied = true;
      showToast('Kode bergabung disalin', 'success');
      setTimeout(() => copied = false, 2000);
    } catch {
      showToast('Gagal menyalin kode', 'error');
    }
  }

  async function regenerate() {
    if (!isOwner || !slug) return;
    regenerating = true;
    try {
      const res: any = await regenerateJoinCode(slug);
      joinCode = res?.joinCode || '';
      showToast('Kode bergabung berhasil diperbarui', 'success');
    } catch (err: any) {
      showToast(err?.message || 'Gagal memperbarui kode bergabung', 'error');
    } finally {
      regenerating = false;
    }
  }

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
{:else}
  <div class="card p-5 mb-6 max-w-2xl" data-tour="join-code-card">
    <div class="flex items-start gap-4">
      <div class="w-10 h-10 bg-[var(--color-kepin-blue)]/10 rounded-full flex items-center justify-center shrink-0">
        <KeyRound class="w-5 h-5 text-[var(--color-kepin-blue)]" />
      </div>
      <div class="flex-1 min-w-0">
        <h2 class="font-semibold">Kode Bergabung</h2>
        <p class="text-sm text-[hsl(var(--muted-foreground))] mt-1">
          Bagikan kode ini kepada orang yang ingin bergabung. Mereka bisa bergabung di halaman
          <a href="/auth/join-company" class="text-[hsl(var(--primary))] hover:underline inline-flex items-center gap-0.5">
            Gabung Perusahaan <ExternalLink class="w-3 h-3" />
          </a>
          — selama mereka belum menjadi anggota perusahaan lain (satu akun hanya untuk satu perusahaan).
        </p>
        <div class="flex flex-wrap items-center gap-3 mt-4">
          {#if codeLoading}
            <div class="skeleton h-10 w-44 rounded-lg"></div>
          {:else}
            <code
              class="px-3 py-2 rounded-lg bg-[hsl(var(--muted))] border border-[hsl(var(--border))] font-mono text-base font-bold tracking-widest text-[hsl(var(--primary))]"
            >{joinCode || '—'}</code>
          {/if}
          <Button size="sm" variant="secondary" onclick={copyCode} disabled={!joinCode || codeLoading}>
            {#if copied}<Check class="w-4 h-4" /> Tersalin{:else}<Copy class="w-4 h-4" /> Salin{/if}
          </Button>
          <Button size="sm" variant="secondary" onclick={regenerate} loading={regenerating} disabled={codeLoading}>
            <RefreshCw class="w-4 h-4" /> Perbarui Kode
          </Button>
        </div>
        {#if codeError}
          <p class="text-xs text-[var(--color-kepin-danger)] mt-2">{codeError}</p>
        {:else if !joinCode && !codeLoading}
          <p class="text-xs text-[hsl(var(--muted-foreground))] mt-2">
            Kode tidak tersedia. Klik "Perbarui Kode" untuk membuat kode baru.
          </p>
        {/if}
      </div>
    </div>
  </div>
{/if}

<DataTable
  tourHook="members-table"
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
