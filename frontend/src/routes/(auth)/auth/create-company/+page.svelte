<script lang="ts">
  import { ArrowLeft, Building2 } from '@lucide/svelte';
  import Button from '$lib/components/ui/Button.svelte';
  import Logo from '$lib/components/ui/Logo.svelte';
  import { showToast } from '$lib/stores/toast';
  import { getApiUrl } from '$lib/config/api';

  let name = $state('');
  let slug = $state('');
  let plan = $state('free');
  let loading = $state(false);
  let error = $state('');
  let joinCode = $state('');

  function autoSlug(value: string) {
    slug = value
      .toLowerCase()
      .replace(/[^a-z0-9]+/g, '-')
      .replace(/^-|-$/g, '');
  }

  async function handleCreate(e: Event) {
    e.preventDefault();
    error = '';
    loading = true;

    const token = localStorage.getItem('kepin_token');
    try {
      const res = await fetch(`${getApiUrl()}/auth/create-organization`, {
        method: 'POST',
        headers: { 'content-type': 'application/json', authorization: `Bearer ${token}` },
        body: JSON.stringify({ name, slug, plan }),
      });
      const data = await res.json();
      if (!res.ok) {
        error = data.detail || 'Gagal membuat perusahaan';
        showToast(error, 'error');
        return;
      }
      joinCode = data.tenant.joinCode;
      showToast('Perusahaan berhasil dibuat', 'success');

      const tenants = JSON.parse(localStorage.getItem('kepin_tenants') || '[]');
      tenants.push({ slug: data.tenant.slug, role: 'tenant_owner' });
      localStorage.setItem('kepin_tenants', JSON.stringify(tenants));
    } catch (err: any) {
      error = err?.message || 'Gagal terhubung ke server';
      showToast(error, 'error');
    } finally {
      loading = false;
    }
  }
</script>

<div class="card p-6 sm:p-8 max-w-lg mx-auto">
  <div class="text-center mb-6">
    <a href="/" class="inline-flex items-center gap-2 mb-4">
      <Logo height={32} />
    </a>
    <h1 class="text-2xl font-bold">Buat Perusahaan Baru</h1>
    <p class="text-sm text-[hsl(var(--muted-foreground))] mt-1">Anda akan menjadi pemilik perusahaan ini</p>
  </div>

  {#if joinCode}
    <div class="text-center space-y-4">
      <div class="p-6 bg-[hsl(var(--accent))] rounded-xl">
        <p class="text-sm text-[hsl(var(--muted-foreground))] mb-2">Kode Bergabung Perusahaan</p>
        <p class="text-2xl font-mono font-bold tracking-wider text-[hsl(var(--primary))]">{joinCode}</p>
        <p class="text-xs text-[hsl(var(--muted-foreground))] mt-2">Bagikan kode ini ke anggota tim Anda</p>
      </div>
      <div class="flex gap-2 justify-center">
        <a href="/auth/onboarding">
          <Button variant="secondary">Kembali</Button>
        </a>
        <a href="/app/{slug}">
          <Button>Masuk ke Workspace</Button>
        </a>
      </div>
    </div>
  {:else}
    <form onsubmit={handleCreate} class="space-y-4" data-tour="auth-form">
      <div>
        <label class="label-text mb-1 block" for="co-name">Nama Perusahaan</label>
        <div class="relative">
          <Building2 class="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-[hsl(var(--muted-foreground))]" />
          <input
            id="co-name"
            type="text"
            bind:value={name}
            oninput={(e) => autoSlug(e.currentTarget.value)}
            placeholder="Nama perusahaan Anda"
            required
            class="input-field pl-10"
          />
        </div>
      </div>
      <div>
        <label class="label-text mb-1 block" for="co-slug">Link Unik</label>
        <div class="relative">
          <span class="absolute left-3 top-1/2 -translate-y-1/2 text-sm text-[hsl(var(--muted-foreground))]">/app/</span>
          <input
            id="co-slug"
            type="text"
            bind:value={slug}
            placeholder="nama-perusahaan"
            required
            class="input-field pl-14"
          />
        </div>
        <p class="text-xs text-[hsl(var(--muted-foreground))] mt-1">URL workspace perusahaan Anda</p>
      </div>
      <div>
        <label class="label-text mb-1 block" for="co-plan">Paket Langganan</label>
        <select id="co-plan" bind:value={plan} class="input-field">
          <option value="free">Free - Rp0/bln</option>
          <option value="basic">Basic - Rp99.000/bln</option>
          <option value="premium">Premium - Rp299.000/bln</option>
          <option value="platinum">Platinum - Rp799.000/bln</option>
        </select>
      </div>

      {#if error}
        <p class="text-sm text-[var(--color-kepin-danger)] bg-[var(--color-kepin-danger)]/10 px-3 py-2 rounded">{error}</p>
      {/if}

      <Button type="submit" class="w-full" {loading}>
        Buat Perusahaan
      </Button>
    </form>

    <p class="mt-4 text-center text-sm text-[hsl(var(--muted-foreground))]">
      <a href="/auth/onboarding" class="inline-flex items-center gap-1 text-[hsl(var(--primary))] hover:underline">
        <ArrowLeft class="w-3 h-3" /> Kembali
      </a>
    </p>
  {/if}
</div>
