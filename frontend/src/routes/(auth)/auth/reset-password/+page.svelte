<script lang="ts">
  import { page } from '$app/stores';
  import { Lock, KeyRound } from '@lucide/svelte';
  import Button from '$lib/components/ui/Button.svelte';
  import { resetPassword } from '$lib/stores/auth';
  import { showToast } from '$lib/stores/toast';

  let password = $state('');
  let confirm = $state('');
  let manualToken = $state('');
  let done = $state(false);
  let loading = $state(false);
  let error = $state('');

  const urlToken = $derived($page.url.searchParams.get('token') || '');
  const token = $derived(urlToken || manualToken.trim());

  async function handleSubmit(e: Event) {
    e.preventDefault();
    error = '';
    if (password !== confirm) {
      error = 'Konfirmasi password tidak sama.';
      return;
    }
    if (!token) {
      error = 'Token reset tidak ditemukan.';
      return;
    }
    loading = true;
    const result = await resetPassword(token, password);
    loading = false;
    if (result.success) {
      done = true;
      showToast('Password berhasil direset', 'success');
    } else {
      error = result.error || 'Gagal mereset password';
      showToast(error, 'error');
    }
  }
</script>

<div class="card p-6 sm:p-8">
  <div class="text-center mb-6">
    <h1 class="text-2xl font-bold">Reset Password</h1>
    <p class="text-sm text-[hsl(var(--muted-foreground))] mt-1">Buat password baru untuk akun Anda</p>
  </div>

  {#if done}
    <div class="text-center space-y-4">
      <div class="w-12 h-12 bg-[var(--color-kepin-green)] rounded-full flex items-center justify-center mx-auto">
        <KeyRound class="w-6 h-6 text-white" />
      </div>
      <p class="text-sm text-[hsl(var(--muted-foreground))]">
        Password berhasil direset. Silakan masuk dengan password baru.
      </p>
      <a href="/auth/login" class="inline-block">
        <Button type="button">Kembali ke Login</Button>
      </a>
    </div>
  {:else}
    <form onsubmit={handleSubmit} class="space-y-4">
      {#if !urlToken}
        <div>
          <label class="label-text mb-1 block" for="reset-token">Token Reset</label>
          <input
            id="reset-token"
            type="text"
            bind:value={manualToken}
            placeholder="Tempel token dari email / layar sebelumnya"
            class="input-field font-mono text-xs"
          />
        </div>
      {/if}
      <div>
        <label class="label-text mb-1 block" for="new-password">Password Baru</label>
        <div class="relative">
          <Lock class="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-[hsl(var(--muted-foreground))]" />
          <input id="new-password" type="password" bind:value={password} placeholder="Min. 8 karakter" required minlength={8} class="input-field pl-10" />
        </div>
      </div>
      <div>
        <label class="label-text mb-1 block" for="confirm-password">Konfirmasi Password</label>
        <input id="confirm-password" type="password" bind:value={confirm} placeholder="Ulangi password" required class="input-field" />
      </div>
      <Button type="submit" class="w-full" {loading}>
        Reset Password
      </Button>
      {#if error}
        <p class="text-sm text-[var(--color-kepin-danger)]">{error}</p>
      {/if}
    </form>
  {/if}
</div>
