<script lang="ts">
  import { Eye, EyeOff, Lock, Mail } from '@lucide/svelte';
  import Button from '$lib/components/ui/Button.svelte';

  let email = $state('');
  let password = $state('');
  let showPassword = $state(false);
  let loading = $state(false);

  async function handleLogin(e: Event) {
    e.preventDefault();
    loading = true;
    await new Promise(r => setTimeout(r, 1000));
    loading = false;
    window.location.href = '/app/toko-maju';
  }
</script>

<div class="card p-6 sm:p-8">
  <div class="text-center mb-6">
    <a href="/" class="inline-flex items-center gap-2 mb-4">
      <div class="w-8 h-8 bg-[var(--color-kepin-red)] flex items-center justify-center rounded">
        <span class="text-white font-bold text-sm">K</span>
      </div>
      <span class="font-bold text-lg">KePin</span>
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

    <Button type="submit" class="w-full" {loading}>
      Masuk
    </Button>
  </form>

  <p class="mt-4 text-center text-sm text-[hsl(var(--muted-foreground))]">
    Belum punya akun? <a href="/auth/register" class="text-[hsl(var(--primary))] hover:underline font-medium">Daftar gratis</a>
  </p>
</div>
