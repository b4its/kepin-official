<script lang="ts">
  import { Mail, Copy } from '@lucide/svelte';
  import Button from '$lib/components/ui/Button.svelte';
  import { forgotPassword } from '$lib/stores/auth';
  import { showToast } from '$lib/stores/toast';

  let email = $state('');
  let sent = $state(false);
  let loading = $state(false);
  let error = $state('');
  let devToken = $state('');

  async function handleSubmit(e: Event) {
    e.preventDefault();
    error = '';
    loading = true;
    const result = await forgotPassword(email);
    loading = false;
    if (result.success) {
      devToken = result.devToken || '';
      sent = true;
    } else {
      error = result.error || 'Gagal mengirim tautan reset';
      showToast(error, 'error');
    }
  }

  function copyToken() {
    navigator.clipboard.writeText(devToken);
    showToast('Token disalin ke clipboard', 'success');
  }
</script>

<div class="card p-6 sm:p-8">
  <div class="text-center mb-6">
    <h1 class="text-2xl font-bold">Lupa Password</h1>
    <p class="text-sm text-[hsl(var(--muted-foreground))] mt-1">
      {sent ? 'Cek email Anda untuk tautan reset password' : 'Masukkan email untuk menerima tautan reset'}
    </p>
  </div>

  {#if sent}
    <div class="text-center">
      <div class="w-12 h-12 bg-[var(--color-kepin-green)] rounded-full flex items-center justify-center mx-auto mb-4">
        <Mail class="w-6 h-6 text-white" />
      </div>
      <p class="text-sm text-[hsl(var(--muted-foreground))]">
        Jika email terdaftar, tautan reset akan dikirim dalam beberapa menit.
      </p>
      {#if devToken}
        <div class="mt-4 rounded-lg border border-dashed border-[hsl(var(--input))] p-4 text-left space-y-2">
          <p class="text-xs text-[hsl(var(--muted-foreground))]">
            <strong>Mode pengembangan</strong> — layanan email belum terhubung, gunakan token berikut untuk melanjutkan reset:
          </p>
          <p class="font-mono text-xs break-all bg-[hsl(var(--muted))] px-3 py-2 rounded">{devToken}</p>
          <div class="flex justify-center gap-2">
            <Button variant="secondary" type="button" onclick={copyToken}><Copy class="w-4 h-4" /> Salin Token</Button>
            <a href="/auth/reset-password?token={encodeURIComponent(devToken)}">
              <Button type="button">Lanjutkan Reset</Button>
            </a>
          </div>
        </div>
      {/if}
      <a href="/auth/login" class="mt-4 btn-ghost inline-flex">Kembali ke Login</a>
    </div>
    {:else}
      <form onsubmit={handleSubmit} class="space-y-4">
      <div>
        <label class="label-text mb-1 block" for="reset-email">Email</label>
        <div class="relative">
          <Mail class="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-[hsl(var(--muted-foreground))]" />
          <input id="reset-email" type="email" bind:value={email} placeholder="nama@perusahaan.com" required class="input-field pl-10" />
        </div>
      </div>
       <Button type="submit" class="w-full" {loading}>Kirim Tautan Reset</Button>
      </form>
      {#if error}
        <p class="mt-3 text-sm text-[var(--color-kepin-danger)]">{error}</p>
      {/if}
    <p class="mt-4 text-center text-sm text-[hsl(var(--muted-foreground))]">
      <a href="/auth/login" class="text-[hsl(var(--primary))] hover:underline">Kembali ke Login</a>
    </p>
  {/if}
</div>
