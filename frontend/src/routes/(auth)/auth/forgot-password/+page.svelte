<script lang="ts">
  import { Mail } from '@lucide/svelte';
  import Button from '$lib/components/ui/Button.svelte';

  let email = $state('');
  let sent = $state(false);

  function handleSubmit(e: Event) {
    e.preventDefault();
    sent = true;
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
      <Button type="submit" class="w-full">Kirim Tautan Reset</Button>
    </form>
    <p class="mt-4 text-center text-sm text-[hsl(var(--muted-foreground))]">
      <a href="/auth/login" class="text-[hsl(var(--primary))] hover:underline">Kembali ke Login</a>
    </p>
  {/if}
</div>
