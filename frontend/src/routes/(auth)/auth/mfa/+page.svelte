<script lang="ts">
  import { onMount } from 'svelte';
  import { Shield } from '@lucide/svelte';
  import Button from '$lib/components/ui/Button.svelte';
  import Logo from '$lib/components/ui/Logo.svelte';
  import { verifyMfa } from '$lib/stores/auth';
  import { showToast } from '$lib/stores/toast';

  let codes = $state(Array(6).fill(''));
  let recoveryCode = $state('');
  let tab = $state<'code' | 'recovery'>('code');
  let loading = $state(false);
  let error = $state('');
  let sessionMissing = $state(false);

  onMount(() => {
    if (!localStorage.getItem('kepin_mfa_token')) {
      sessionMissing = true;
    }
  });

  function handleInput(e: Event, i: number) {
    const input = e.target as HTMLInputElement;
    if (input.value && i < 5) {
      const next = document.getElementById(`mfa-${i + 1}`);
      next?.focus();
    }
  }

  function handlePaste(e: ClipboardEvent) {
    const data = e.clipboardData?.getData('text');
    if (data?.length === 6) {
      codes = data.split('');
    }
  }

  async function handleSubmit(e: SubmitEvent) {
    e.preventDefault();
    if (sessionMissing) return;
    error = '';
    loading = true;
    const code = tab === 'code' ? codes.join('') : recoveryCode.trim();
    const result = await verifyMfa(code);
    loading = false;
    if (result.success) {
      showToast('Verifikasi berhasil', 'success');
      if (result.isSuperadmin) {
        window.location.href = '/admin';
      } else {
        const tenants = JSON.parse(localStorage.getItem('kepin_tenants') || '[]');
        if (tenants.length > 0) {
          window.location.href = `/app/${result.tenantSlug || tenants[0]?.slug || 'toko-maju'}`;
        } else {
          window.location.href = '/auth/onboarding';
        }
      }
    } else {
      error = result.error || 'Kode verifikasi salah';
      showToast(error, 'error');
    }
  }
</script>

<div class="card p-6 sm:p-8">
  <div class="text-center mb-6">
    <a href="/" class="inline-flex items-center gap-2 mb-4">
      <Logo height={32} />
    </a>
    <div class="w-12 h-12 bg-[var(--color-kepin-blue)] rounded-full flex items-center justify-center mx-auto mb-4">
      <Shield class="w-6 h-6 text-white" />
    </div>
    <h1 class="text-2xl font-bold">Verifikasi Dua Langkah</h1>
    <p class="text-sm text-[hsl(var(--muted-foreground))] mt-1">
      {tab === 'code' ? 'Masukkan kode 6 digit dari aplikasi authenticator Anda' : 'Masukkan salah satu recovery code Anda'}
    </p>
  </div>

  {#if sessionMissing}
    <div class="text-center space-y-4">
      <p class="text-sm text-[hsl(var(--muted-foreground))]">Sesi verifikasi MFA tidak ditemukan atau telah kedaluwarsa.</p>
      <a href="/auth/login" class="inline-block">
        <Button type="button">Kembali ke Login</Button>
      </a>
    </div>
  {:else}
    <div class="flex justify-center gap-2 mb-6">
      <button
        type="button"
        onclick={() => { tab = 'code'; error = ''; }}
        class:tab-active={tab === 'code'}
        class="tab-btn"
      >Kode Authenticator</button>
      <button
        type="button"
        onclick={() => { tab = 'recovery'; error = ''; }}
        class:tab-active={tab === 'recovery'}
        class="tab-btn"
      >Recovery Code</button>
    </div>

    <form class="space-y-6" onsubmit={handleSubmit}>
      {#if tab === 'code'}
        <div class="flex justify-center gap-2" onpaste={handlePaste}>
          {#each codes as _, i}
            <input
              id="mfa-{i}"
              type="text"
              maxlength={1}
              bind:value={codes[i]}
              oninput={(e) => handleInput(e, i)}
              class="w-10 h-12 text-center text-lg font-bold border border-[hsl(var(--input))] rounded focus-visible:outline-2 focus-visible:outline-[hsl(var(--ring))] bg-[hsl(var(--background))] text-[hsl(var(--foreground))]"
            />
          {/each}
        </div>
      {:else}
        <input
          type="text"
          bind:value={recoveryCode}
          placeholder="XXXX-XXXX"
          class="input-field text-center tracking-widest"
          required
        />
      {/if}
      <Button type="submit" class="w-full" {loading}>
        Verifikasi
      </Button>
      {#if error}
        <p class="text-sm text-[var(--color-kepin-danger)] bg-[var(--color-kepin-danger)]/10 px-3 py-2 rounded">{error}</p>
      {/if}
    </form>
  {/if}

  <div class="mt-4 text-center">
    <p class="text-sm">
      <a href="/auth/login" class="text-[hsl(var(--muted-foreground))] hover:text-[hsl(var(--foreground))]">Kembali ke login</a>
    </p>
  </div>
</div>

<style>
  .tab-btn {
    padding: 0.375rem 0.875rem;
    border-radius: 0.5rem;
    font-size: 0.8125rem;
    color: hsl(var(--muted-foreground));
    border: 1px solid hsl(var(--input));
    background: hsl(var(--background));
    cursor: pointer;
  }
  .tab-btn.tab-active {
    color: hsl(var(--primary));
    border-color: hsl(var(--primary));
    background: hsl(var(--primary) / 0.08);
    font-weight: 600;
  }
</style>
