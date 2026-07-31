<script lang="ts">
  import { page } from '$app/stores';
  import PageHeader from '$lib/components/layout/PageHeader.svelte';
  import Button from '$lib/components/ui/Button.svelte';
  import Modal from '$lib/components/ui/Modal.svelte';
  import { tenantApi, currentRole } from '$lib/stores/data';
  import { showToast } from '$lib/stores/toast';
  import { Link, Plus, RefreshCw } from '@lucide/svelte';

  type Integration = { id?: string | null; provider?: string | null; displayName?: string | null; display_name?: string | null; status: string; lastSyncedAt?: string | null; last_synced_at?: string | null };

  const slug = $derived($page.params.tenantSlug || '');
  let integrations = $state<Integration[]>([]);
  let loading = $state(false);
  let saving = $state(false);
  let error = $state('');
  let showModal = $state(false);
  let form = $state({ provider: '', displayName: '' });
  const isOwner = $derived($currentRole === 'tenant_owner');

  async function loadIntegrations() {
    if (!slug) return;
    loading = true;
    error = '';
    try {
      integrations = await tenantApi.getIntegrations(slug) as Integration[];
    } catch (err: any) {
      error = err?.message || 'Gagal memuat integrasi';
    } finally {
      loading = false;
    }
  }

  function nameOf(item: Integration) {
    return item.displayName || item.display_name || item.provider || 'Integrasi';
  }

  async function createIntegration() {
    if (!isOwner || !slug) return;
    saving = true;
    try {
      await tenantApi.createIntegration(slug, form);
      showModal = false;
      form = { provider: '', displayName: '' };
      showToast('Integrasi berhasil dicatat. Konfigurasi secret dilakukan melalui backend connector.', 'success');
      await loadIntegrations();
    } catch (err: any) {
      showToast(err?.message || 'Gagal menambah integrasi', 'error');
    } finally {
      saving = false;
    }
  }

  async function setStatus(item: Integration, status: string) {
    if (!isOwner || !slug || !item.id) return;
    try {
      await tenantApi.updateIntegration(slug, item.id, { status });
      showToast(status === 'disconnected' ? 'Integrasi diputuskan' : 'Status integrasi diperbarui', 'success');
      await loadIntegrations();
    } catch (err: any) {
      showToast(err?.message || 'Gagal memperbarui integrasi', 'error');
    }
  }

  $effect(() => { if (slug) void loadIntegrations(); });
</script>

<PageHeader title="Integrasi" description="Status integrasi dari backend" breadcrumbs={[{ label: 'Pengaturan' }, { label: 'Integrasi' }]}>
  {#snippet actions()}
    <Button variant="secondary" onclick={loadIntegrations} loading={loading}><RefreshCw class="w-4 h-4" /> Refresh</Button>
    {#if isOwner}
      <Button onclick={() => showModal = true}><Plus class="w-4 h-4" /> Tambah Integrasi</Button>
    {/if}
  {/snippet}
</PageHeader>

{#if error}
  <div class="mb-4 rounded-lg border border-red-200 bg-red-50 p-4 text-sm text-red-700">{error}</div>
{/if}

<div class="space-y-3 max-w-2xl">
  {#if loading}
    <div class="card p-4"><div class="skeleton h-10 w-full"></div></div>
  {:else if integrations.length > 0}
    {#each integrations as int}
      <div class="card p-4 flex items-center justify-between gap-4">
        <div class="flex items-center gap-3">
          <Link class="w-5 h-5 text-[var(--color-kepin-blue)] shrink-0" />
          <div>
            <p class="font-medium text-sm">{nameOf(int)}</p>
            <p class="text-xs text-[hsl(var(--muted-foreground))]">Sinkron terakhir: {int.lastSyncedAt || int.last_synced_at || '-'}</p>
          </div>
        </div>
        <span class="rounded-full border border-[hsl(var(--border))] px-2.5 py-1 text-xs uppercase">{int.status}</span>
        {#if isOwner && int.id}
          <Button variant="ghost" size="sm" onclick={() => setStatus(int, int.status === 'disconnected' ? 'active' : 'disconnected')}>
            {int.status === 'disconnected' ? 'Aktifkan' : 'Putuskan'}
          </Button>
        {/if}
      </div>
    {/each}
  {:else}
    <div class="card p-5 text-sm text-[hsl(var(--muted-foreground))]">
      Backend belum mengembalikan integrasi aktif. Tidak menampilkan daftar integrasi dummy.
    </div>
  {/if}
</div>

<Modal title="Tambah Integrasi" open={showModal} onclose={() => showModal = false}>
  <form onsubmit={createIntegration} class="space-y-4">
    <p class="text-sm text-[hsl(var(--muted-foreground))]">Data connector/API key tidak dimasukkan di browser. Halaman ini hanya mencatat lifecycle integrasi.</p>
    <div>
      <label class="label-text" for="integration-provider">Provider</label>
      <input id="integration-provider" bind:value={form.provider} class="input-field mt-1" placeholder="contoh: bca" required />
    </div>
    <div>
      <label class="label-text" for="integration-name">Nama Tampilan</label>
      <input id="integration-name" bind:value={form.displayName} class="input-field mt-1" placeholder="contoh: BCA Rekening Utama" required />
    </div>
    <div class="flex justify-end gap-2 pt-2">
      <Button variant="secondary" type="button" onclick={() => showModal = false}>Batal</Button>
      <Button type="submit" loading={saving}>Simpan</Button>
    </div>
  </form>
</Modal>
