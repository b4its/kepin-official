<script lang="ts">
  import { ArrowLeft, KeyRound, Building2 } from '@lucide/svelte';
  import Button from '$lib/components/ui/Button.svelte';
  import Logo from '$lib/components/ui/Logo.svelte';
  import { showToast } from '$lib/stores/toast';
  import { PUBLIC_API_URL } from '$env/static/public';

  let joinCode = $state('');
  let loading = $state(false);
  let error = $state('');
  let companyInfo: { name: string; slug: string } | null = $state(null);

  async function lookupCode() {
    if (joinCode.length < 3) return;
    try {
      const res = await fetch(`${PUBLIC_API_URL}/auth/join-info?code=${encodeURIComponent(joinCode)}`);
      if (res.ok) {
        const data = await res.json();
        companyInfo = data.tenant;
      } else {
        companyInfo = null;
      }
    } catch {
      companyInfo = null;
    }
  }

  async function handleJoin(e: Event) {
    e.preventDefault();
    error = '';
    loading = true;

    const token = localStorage.getItem('kepin_token');
    try {
      const res = await fetch(`${PUBLIC_API_URL}/auth/join-by-code`, {
        method: 'POST',
        headers: { 'content-type': 'application/json', authorization: `Bearer ${token}` },
        body: JSON.stringify({ join_code: joinCode }),
      });
      const data = await res.json();
      if (!res.ok) {
        error = data.detail || 'Kode bergabung tidak valid';
        showToast(error, 'error');
        return;
      }

      showToast('Berhasil bergabung ke perusahaan', 'success');
      const tenants = JSON.parse(localStorage.getItem('kepin_tenants') || '[]');
      tenants.push({ slug: data.tenant.slug, role: data.role });
      localStorage.setItem('kepin_tenants', JSON.stringify(tenants));
      window.location.href = `/app/${data.tenant.slug}`;
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
    <h1 class="text-2xl font-bold">Gabung Perusahaan</h1>
    <p class="text-sm text-[hsl(var(--muted-foreground))] mt-1">Masukkan kode bergabung yang diberikan oleh pemilik perusahaan</p>
  </div>

  <form onsubmit={handleJoin} class="space-y-4">
    <div>
      <label class="label-text mb-1 block" for="join-code">Kode Bergabung</label>
      <div class="relative">
        <KeyRound class="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-[hsl(var(--muted-foreground))]" />
        <input
          id="join-code"
          type="text"
          bind:value={joinCode}
          oninput={lookupCode}
          placeholder="Masukkan kode 16 karakter"
          required
          class="input-field pl-10 font-mono tracking-wider text-center"
        />
      </div>
    </div>

    {#if companyInfo}
      <div class="flex items-center gap-3 p-3 rounded-lg bg-[hsl(var(--accent))]">
        <Building2 class="w-5 h-5 text-[hsl(var(--primary))] shrink-0" />
        <div>
          <p class="text-sm font-semibold">{companyInfo.name}</p>
          <p class="text-xs text-[hsl(var(--muted-foreground))]">/app/{companyInfo.slug}</p>
        </div>
      </div>
    {/if}

    {#if error}
      <p class="text-sm text-[var(--color-kepin-danger)] bg-[var(--color-kepin-danger)]/10 px-3 py-2 rounded">{error}</p>
    {/if}

    <Button type="submit" class="w-full" disabled={!companyInfo} {loading}>
      Gabung
    </Button>
  </form>

  <p class="mt-4 text-center text-sm text-[hsl(var(--muted-foreground))]">
    <a href="/auth/onboarding" class="inline-flex items-center gap-1 text-[hsl(var(--primary))] hover:underline">
      <ArrowLeft class="w-3 h-3" /> Kembali
    </a>
  </p>
</div>
