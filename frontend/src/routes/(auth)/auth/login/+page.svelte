<script lang="ts">
  import { Eye, EyeOff, Lock, Mail } from '@lucide/svelte';
  import Button from '$lib/components/ui/Button.svelte';
  import Logo from '$lib/components/ui/Logo.svelte';
  import { login } from '$lib/stores/auth';
  import { showToast } from '$lib/stores/toast';

  let email = $state('');
  let password = $state('');
  let showPassword = $state(false);
  let loading = $state(false);
  let error = $state('');

  async function handleLogin(e: Event) {
    e.preventDefault();
    error = '';
    loading = true;
    const result = await login(email, password);
    loading = false;
    if (result.success) {
      showToast('Login berhasil', 'success');
      const targetSlug = result.tenantSlug || 'toko-maju';
      window.location.href = `/app/${targetSlug}`;
    } else {
      error = result.error || 'Login gagal';
      showToast(error, 'error');
    }
  }
</script>

<div class="card p-6 sm:p-8">
  <div class="text-center mb-6">
    <a href="/" class="inline-flex items-center gap-2 mb-4">
      <Logo height={32} />
    </a>
    <h1 class="text-2xl font-bold">Masuk</h1>
    <p class="text-sm text-[hsl(var(--muted-foreground))] mt-1">Masuk ke workspace KePin Anda</p>
  </div>

  <form onsubmit={handleLogin} class="space-y-4">
    <div>
      <label class="label-text mb-1 block" for="email">Email</label>
      <div class="relative">
        <Mail class="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-[hsl(var(--muted-foreground))]" />
        <input
          id="email"
          type="email"
          bind:value={email}
          placeholder="nama@perusahaan.com"
          required
          class="input-field pl-10"
        />
      </div>
    </div>
    <div>
      <label class="label-text mb-1 block" for="password">Password</label>
      <div class="relative">
        <Lock class="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-[hsl(var(--muted-foreground))]" />
        <input
          id="password"
          type={showPassword ? 'text' : 'password'}
          bind:value={password}
          placeholder="Masukkan password"
          required
          class="input-field pl-10 pr-10"
        />
        <button
          type="button"
          onclick={() => showPassword = !showPassword}
          class="absolute right-3 top-1/2 -translate-y-1/2"
          aria-label={showPassword ? 'Sembunyikan password' : 'Tampilkan password'}
        >
          {#if showPassword}
            <EyeOff class="w-4 h-4 text-[hsl(var(--muted-foreground))]" />
          {:else}
            <Eye class="w-4 h-4 text-[hsl(var(--muted-foreground))]" />
          {/if}
        </button>
      </div>
    </div>

    <div class="flex items-center justify-between text-sm">
      <label class="flex items-center gap-2">
        <input type="checkbox" class="w-4 h-4 rounded border-[hsl(var(--border))]" />
        <span>Ingat saya</span>
      </label>
      <a href="/auth/forgot-password" class="text-[hsl(var(--primary))] hover:underline">Lupa password?</a>
    </div>

    {#if error}
      <p class="text-sm text-[var(--color-kepin-danger)] bg-[var(--color-kepin-danger)]/10 px-3 py-2 rounded">{error}</p>
    {/if}

    <Button type="submit" class="w-full" {loading}>
      Masuk
    </Button>
  </form>

  <p class="mt-4 text-center text-sm text-[hsl(var(--muted-foreground))]">
    Belum punya akun? <a href="/auth/register" class="text-[hsl(var(--primary))] hover:underline font-medium">Daftar gratis</a>
  </p>
</div>
