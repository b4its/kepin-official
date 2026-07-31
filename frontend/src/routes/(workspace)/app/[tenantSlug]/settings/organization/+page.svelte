<script lang="ts">
  import { page } from '$app/stores';
  import PageHeader from '$lib/components/layout/PageHeader.svelte';
  import Button from '$lib/components/ui/Button.svelte';
  import Modal from '$lib/components/ui/Modal.svelte';
  import { tenantApi } from '$lib/stores/data';
  import { showToast } from '$lib/stores/toast';
  import { RefreshCw } from '@lucide/svelte';

  type Organization = {
    tenantId: string;
    tenantName?: string | null;
    legalName?: string | null;
    taxId?: string | null;
    address?: string | null;
    phone?: string | null;
    email?: string | null;
    website?: string | null;
    timezone?: string | null;
    currency?: string | null;
    fiscalYearStart?: string | null;
  };

  const slug = $derived($page.params.tenantSlug || '');
  let org = $state<Organization | null>(null);
  let loading = $state(false);
  let saving = $state(false);
  let error = $state('');
  let showModal = $state(false);
  let editForm = $state({ tenantName: '', legalName: '', taxId: '', address: '', phone: '', email: '', website: '', timezone: 'Asia/Jakarta', currency: 'IDR' });

  async function loadOrganization() {
    if (!slug) return;
    loading = true;
    error = '';
    try {
      org = await tenantApi.getOrganization(slug) as Organization;
    } catch (err: any) {
      error = err?.message || 'Gagal memuat organisasi';
    } finally {
      loading = false;
    }
  }

  function openEdit() {
    editForm = {
      tenantName: org?.tenantName || '',
      legalName: org?.legalName || '',
      taxId: org?.taxId || '',
      address: org?.address || '',
      phone: org?.phone || '',
      email: org?.email || '',
      website: org?.website || '',
      timezone: org?.timezone || 'Asia/Jakarta',
      currency: org?.currency || 'IDR',
    };
    showModal = true;
  }

  async function save() {
    saving = true;
    try {
      org = await tenantApi.updateOrganization(slug, editForm) as Organization;
      showModal = false;
      showToast('Profil organisasi berhasil diperbarui', 'success');
    } catch (err: any) {
      showToast(err?.message || 'Gagal memperbarui organisasi', 'error');
    } finally {
      saving = false;
    }
  }

  $effect(() => { if (slug) void loadOrganization(); });
</script>

<PageHeader title="Organisasi" description="Profil organisasi dari backend" breadcrumbs={[{ label: 'Pengaturan' }, { label: 'Organisasi' }]}> 
  {#snippet actions()}
    <Button variant="secondary" onclick={loadOrganization} loading={loading}><RefreshCw class="w-4 h-4" /> Refresh</Button>
    <Button onclick={openEdit} disabled={!org || loading}>Edit Profil</Button>
  {/snippet}
</PageHeader>

{#if error}
  <div class="mb-4 rounded-lg border border-red-200 bg-red-50 p-4 text-sm text-red-700">{error}</div>
{/if}

<div class="card p-6 max-w-2xl space-y-4">
  <div class="grid sm:grid-cols-2 gap-4">
    <div>
      <p class="label-text mb-1">Nama Tampilan</p>
      <p class="text-sm">{org?.tenantName ?? '-'}</p>
    </div>
    <div>
      <p class="label-text mb-1">Nama Legal</p>
      <p class="text-sm">{org?.legalName ?? '-'}</p>
    </div>
    <div>
      <p class="label-text mb-1">NPWP</p>
      <p class="text-sm">{org?.taxId ?? '-'}</p>
    </div>
    <div>
      <p class="label-text mb-1">Telepon</p>
      <p class="text-sm">{org?.phone ?? '-'}</p>
    </div>
    <div>
      <p class="label-text mb-1">Email</p>
      <p class="text-sm">{org?.email ?? '-'}</p>
    </div>
    <div>
      <p class="label-text mb-1">Website</p>
      <p class="text-sm">{org?.website ?? '-'}</p>
    </div>
    <div>
      <p class="label-text mb-1">Alamat</p>
      <p class="text-sm">{org?.address ?? '-'}</p>
    </div>
    <div>
      <p class="label-text mb-1">Zona Waktu</p>
      <p class="text-sm">{org?.timezone ?? '-'}</p>
    </div>
    <div>
      <p class="label-text mb-1">Currency</p>
      <p class="text-sm">{org?.currency ?? '-'}</p>
    </div>
  </div>
</div>

<div class="card p-6 max-w-2xl mt-6 text-sm text-[hsl(var(--muted-foreground))]">
  Kode bergabung tidak lagi dibaca dari localStorage. Fitur tampil/regenerate kode perlu endpoint tenant-scoped yang eksplisit agar tidak membocorkan join code.
</div>

<Modal title="Edit Profil Organisasi" open={showModal} onclose={() => showModal = false}>
  <form onsubmit={save} class="space-y-4">
    <div class="grid sm:grid-cols-2 gap-4">
      <div>
        <label class="label-text" for="org-name">Nama Tampilan</label>
        <input id="org-name" type="text" bind:value={editForm.tenantName} class="input-field mt-1" required />
      </div>
      <div>
        <label class="label-text" for="org-legal">Nama Legal</label>
        <input id="org-legal" type="text" bind:value={editForm.legalName} class="input-field mt-1" required />
      </div>
      <div>
        <label class="label-text" for="org-tax">NPWP</label>
        <input id="org-tax" type="text" bind:value={editForm.taxId} class="input-field mt-1" />
      </div>
      <div>
        <label class="label-text" for="org-phone">Telepon</label>
        <input id="org-phone" type="text" bind:value={editForm.phone} class="input-field mt-1" />
      </div>
      <div>
        <label class="label-text" for="org-email">Email</label>
        <input id="org-email" type="email" bind:value={editForm.email} class="input-field mt-1" />
      </div>
      <div>
        <label class="label-text" for="org-website">Website</label>
        <input id="org-website" type="url" bind:value={editForm.website} class="input-field mt-1" />
      </div>
      <div class="sm:col-span-2">
        <label class="label-text" for="org-address">Alamat</label>
        <textarea id="org-address" bind:value={editForm.address} class="input-field mt-1" rows="2"></textarea>
      </div>
      <div>
        <label class="label-text" for="org-timezone">Zona Waktu</label>
        <select id="org-timezone" bind:value={editForm.timezone} class="input-field mt-1">
          <option value="Asia/Jakarta">Asia/Jakarta (WIB)</option>
          <option value="Asia/Makassar">Asia/Makassar (WITA)</option>
          <option value="Asia/Jayapura">Asia/Jayapura (WIT)</option>
        </select>
      </div>
      <div>
        <label class="label-text" for="org-currency">Currency</label>
        <select id="org-currency" bind:value={editForm.currency} class="input-field mt-1">
          <option value="IDR">IDR</option>
        </select>
      </div>
    </div>
    <div class="flex justify-end gap-2 pt-2">
      <Button variant="secondary" type="button" onclick={() => showModal = false}>Batal</Button>
      <Button type="submit" loading={saving}>Simpan Perubahan</Button>
    </div>
  </form>
</Modal>
