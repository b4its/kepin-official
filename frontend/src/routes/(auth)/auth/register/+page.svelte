<script lang="ts">
  import { Mail, User, Lock, Building2 } from '@lucide/svelte';
  import Button from '$lib/components/ui/Button.svelte';

  let name = $state('');
  let email = $state('');
  let company = $state('');
  let password = $state('');
  let loading = $state(false);

  async function handleRegister(e: Event) {
    e.preventDefault();
    loading = true;
    await new Promise(r => setTimeout(r, 1500));
    loading = false;
    window.location.href = '/auth/login';
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

    <Button type="submit" class="w-full" {loading}>
      Buat Akun & Mulai Trial
    </Button>
  </form>

  <p class="mt-4 text-center text-sm text-[hsl(var(--muted-foreground))]">
    Sudah punya akun? <a href="/auth/login" class="text-[hsl(var(--primary))] hover:underline font-medium">Masuk</a>
  </p>
</div>
