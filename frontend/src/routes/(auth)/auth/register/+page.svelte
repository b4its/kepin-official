<script lang="ts">
  import { Mail, User, Lock, Building2 } from '@lucide/svelte';
  import Button from '$lib/components/ui/Button.svelte';
  import Logo from '$lib/components/ui/Logo.svelte';
  import { register } from '$lib/stores/auth';

  let name = $state('');
  let email = $state('');
  let company = $state('');
  let password = $state('');
  let loading = $state(false);
  let error = $state('');
  let success = $state(false);

  function handleRegister(e: Event) {
    e.preventDefault();
    error = '';
    loading = true;
    const result = register(name, email, password);
    loading = false;
    if (result.success) {
      success = true;
    } else {
      error = result.error || 'Registrasi gagal';
    }
  }
</script>

<div class="card p-6 sm:p-8">
  <div class="text-center mb-6">
    <a href="/" class="inline-flex items-center gap-2 mb-4">
      <Logo height={32} />
    </a>
    <h1 class="text-2xl font-bold">Daftar Gratis</h1>
    <p class="text-sm text-[hsl(var(--muted-foreground))] mt-1">Mulai trial 14 hari tanpa kartu kredit</p>
  </div>

  <form onsubmit={handleRegister} class="space-y-4">
    <div>
      <label class="label-text mb-1 block" for="name">Nama Lengkap</label>
      <div class="relative">
        <User class="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-[hsl(var(--muted-foreground))]" />
        <input id="name" type="text" bind:value={name} placeholder="Nama Anda" required class="input-field pl-10" />
      </div>
    </div>
    <div>
      <label class="label-text mb-1 block" for="reg-email">Email</label>
      <div class="relative">
        <Mail class="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-[hsl(var(--muted-foreground))]" />
        <input id="reg-email" type="email" bind:value={email} placeholder="nama@perusahaan.com" required class="input-field pl-10" />
      </div>
    </div>
    <div>
      <label class="label-text mb-1 block" for="company">Nama Perusahaan</label>
      <div class="relative">
        <Building2 class="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-[hsl(var(--muted-foreground))]" />
        <input id="company" type="text" bind:value={company} placeholder="Nama bisnis Anda" required class="input-field pl-10" />
      </div>
    </div>
    <div>
      <label class="label-text mb-1 block" for="reg-password">Password</label>
      <div class="relative">
        <Lock class="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-[hsl(var(--muted-foreground))]" />
        <input id="reg-password" type="password" bind:value={password} placeholder="Min. 8 karakter" required minlength={8} class="input-field pl-10" />
      </div>
    </div>

    {#if error}
      <p class="text-sm text-[var(--color-kepin-danger)] bg-[var(--color-kepin-danger)]/10 px-3 py-2 rounded">{error}</p>
    {/if}

    {#if success}
      <p class="text-sm text-green-600 bg-green-50 dark:bg-green-900/20 px-3 py-2 rounded">Pendaftaran berhasil! <a href="/auth/login" class="underline font-medium">Masuk sekarang</a></p>
    {/if}

    <Button type="submit" class="w-full" {loading}>
      Buat Akun & Mulai Trial
    </Button>
  </form>

  <p class="mt-4 text-center text-sm text-[hsl(var(--muted-foreground))]">
    Sudah punya akun? <a href="/auth/login" class="text-[hsl(var(--primary))] hover:underline font-medium">Masuk</a>
  </p>
</div>
