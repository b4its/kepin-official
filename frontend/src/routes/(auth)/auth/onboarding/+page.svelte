<script lang="ts">
  import { Building2, UserPlus, LogOut } from '@lucide/svelte';
  import Logo from '$lib/components/ui/Logo.svelte';
  import { onMount } from 'svelte';
  import { logout } from '$lib/stores/auth';

  let checking = $state(true);

  onMount(() => {
    const user = JSON.parse(localStorage.getItem('kepin_session') || '{}');
    if (user.isSuperadmin) {
      window.location.href = '/admin';
      return;
    }
    const tenants = JSON.parse(localStorage.getItem('kepin_tenants') || '[]');
    if (tenants.length > 0) {
      window.location.href = `/app/${tenants[0].slug}`;
    } else {
      checking = false;
    }
  });
</script>

{#if !checking}
  <div class="card p-8 sm:p-10 text-center">
    <div class="flex justify-center mb-6">
      <a href="/"><Logo height={36} /></a>
    </div>
    <h1 class="text-2xl font-bold mb-2">Selamat Datang!</h1>
    <p class="text-sm text-[hsl(var(--muted-foreground))] mb-8">
      Akun Anda sudah siap. Pilih langkah berikutnya untuk memulai.
    </p>

    <div class="grid sm:grid-cols-2 gap-4 max-w-lg mx-auto">
      <a
        href="/auth/create-company"
        class="flex flex-col items-center gap-3 p-6 rounded-xl border-2 border-[hsl(var(--border))] hover:border-[hsl(var(--primary))] hover:bg-[hsl(var(--accent))] transition-all"
      >
        <Building2 class="w-10 h-10 text-[hsl(var(--primary))]" />
        <div>
          <p class="font-semibold">Buat Perusahaan Baru</p>
          <p class="text-xs text-[hsl(var(--muted-foreground))] mt-1">Membuat perusahaan baru dan menjadi pemilik</p>
        </div>
      </a>
      <a
        href="/auth/join-company"
        class="flex flex-col items-center gap-3 p-6 rounded-xl border-2 border-[hsl(var(--border))] hover:border-[hsl(var(--primary))] hover:bg-[hsl(var(--accent))] transition-all"
      >
        <UserPlus class="w-10 h-10 text-[hsl(var(--primary))]" />
        <div>
          <p class="font-semibold">Gabung Perusahaan</p>
          <p class="text-xs text-[hsl(var(--muted-foreground))] mt-1">Masuk ke perusahaan yang sudah ada menggunakan kode</p>
        </div>
      </a>
    </div>

    <p class="mt-8 text-sm text-[hsl(var(--muted-foreground))]">
      <button onclick={() => { logout(); window.location.href = '/'; }} class="inline-flex items-center gap-1 text-[hsl(var(--primary))] hover:underline">
        <LogOut class="w-3 h-3" /> Logout
      </button>
    </p>
  </div>
{/if}
