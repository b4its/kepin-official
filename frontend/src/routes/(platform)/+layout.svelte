<script lang="ts">
  import { page } from '$app/stores';
  import { goto } from '$app/navigation';
  import AdminShell from '$lib/components/layout/AdminShell.svelte';
  import { loadAdminTenants, loadPlatformAudit, loadAdminUsers, loadSubscriberNotifs } from '$lib/stores/data';
  import { logout } from '$lib/stores/auth';
  import { api, type ApiError } from '$lib/api/client';
  import { onMount } from 'svelte';

  let { children } = $props();
  const path = $derived($page.url.pathname);
  let status = $state<'loading' | 'ready' | 'forbidden' | 'error'>('loading');
  let errorMessage = $state('');

  onMount(() => {
    void loadAdmin();
  });

  async function loadAdmin() {
    status = 'loading';
    errorMessage = '';
    try {
      const me: any = await api('/auth/me');
      if (!me?.is_superadmin && !me?.isSuperadmin) {
        status = 'forbidden';
        errorMessage = 'Hanya superadmin yang dapat mengakses platform admin.';
        return;
      }
      status = 'ready';
      await Promise.allSettled([
        loadAdminTenants(),
        loadPlatformAudit(),
        loadAdminUsers(),
        loadSubscriberNotifs(),
      ]);
    } catch (err) {
      const apiError = err as ApiError;
      errorMessage = apiError.message || 'Gagal memuat admin platform';
      if (apiError.status === 401) {
        logout();
        void goto('/auth/login');
      } else if (apiError.status === 403) {
        status = 'forbidden';
      } else {
        status = 'error';
      }
    }
  }

  function navigate(href: string) {
    window.location.href = href;
  }
</script>

{#if status === 'ready'}
  <AdminShell currentPath={path} onNavigate={navigate}>
    {@render children()}
  </AdminShell>
{:else}
  <div class="min-h-screen bg-[hsl(var(--background))] flex items-center justify-center p-6">
    <div class="card max-w-md w-full p-6 text-center">
      {#if status === 'loading'}
        <div class="skeleton h-8 w-44 mx-auto mb-3"></div>
        <p class="text-sm text-[hsl(var(--muted-foreground))]">Memverifikasi akses admin...</p>
      {:else if status === 'forbidden'}
        <h1 class="text-lg font-semibold mb-2">Akses Ditolak</h1>
        <p class="text-sm text-[hsl(var(--muted-foreground))]">{errorMessage}</p>
      {:else}
        <h1 class="text-lg font-semibold mb-2">Gagal Memuat Admin</h1>
        <p class="text-sm text-[hsl(var(--muted-foreground))] mb-4">{errorMessage}</p>
        <button class="text-sm text-[hsl(var(--primary))] hover:underline" onclick={loadAdmin}>Coba lagi</button>
      {/if}
    </div>
  </div>
{/if}
