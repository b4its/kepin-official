<script lang="ts">
  import { page } from '$app/stores';
  import { goto } from '$app/navigation';
  import WorkspaceShell from '$lib/components/layout/WorkspaceShell.svelte';
  import {
    setSlug,
    clearTenantStores,
    loadSidebarSettings,
    loadCustomers,
    loadSuppliers,
    loadProducts,
    loadPurchaseOrders,
    loadTransactions,
    loadAccounts,
    loadInvoices,
    loadBranches,
    loadMembers,
    loadNotifications,
    loadStockMovements,
    loadJournals,
    loadAuditEvents,
    loadInventoryLocations,
    loadSupplierPayments,
    setCurrentRole,
  } from '$lib/stores/data';
  import { logout } from '$lib/stores/auth';
  import { api, type ApiError } from '$lib/api/client';

  let { children } = $props();

  const path = $derived($page.url.pathname);
  const tenantSlug = $derived($page.params.tenantSlug || '');

  let tenantName = $state('');
  let status = $state<'idle' | 'loading' | 'ready' | 'unauthorized' | 'forbidden' | 'not-found' | 'error'>('idle');
  let errorMessage = $state('');
  let loadSeq = 0;

  async function loadTenant(slug: string) {
    const seq = ++loadSeq;
    status = 'loading';
    errorMessage = '';
    tenantName = '';
    setSlug(slug);

    try {
      const ctx: any = await api(`/tenants/${slug}/context`);
      if (seq !== loadSeq) return;
      tenantName = ctx?.tenant?.name || slug;
      const role = ctx?.role as 'tenant_owner' | 'employee' | null;
      setCurrentRole(role ?? null);
      status = 'ready';

      await Promise.allSettled([
        loadSidebarSettings(slug),
        loadCustomers(slug),
        loadSuppliers(slug),
        loadProducts(slug),
        loadPurchaseOrders(slug),
        loadTransactions(slug),
        loadAccounts(slug),
        loadJournals(slug),
        loadInvoices(slug),
        loadBranches(slug),
        loadMembers(slug),
        loadNotifications(slug),
        loadStockMovements(slug),
        loadAuditEvents(slug),
        loadInventoryLocations(slug),
        loadSupplierPayments(slug),
      ]);
    } catch (err) {
      if (seq !== loadSeq) return;
      clearTenantStores();
      tenantName = slug;
      const apiError = err as ApiError;
      errorMessage = apiError.message || 'Gagal memuat workspace';
      if (apiError.status === 401) {
        status = 'unauthorized';
        logout();
        void goto('/auth/login');
      } else if (apiError.status === 403) {
        status = 'forbidden';
      } else if (apiError.status === 404) {
        status = 'not-found';
      } else {
        status = 'error';
      }
    }
  }

  $effect(() => {
    if (!tenantSlug) return;
    void loadTenant(tenantSlug);
  });

  function navigate(href: string) {
    window.location.href = `/app/${tenantSlug}${href}`;
  }
</script>

{#if status === 'ready'}
  <WorkspaceShell currentPath={path} {tenantName} {tenantSlug} onNavigate={navigate}>
    {@render children()}
  </WorkspaceShell>
{:else}
  <div class="min-h-screen bg-[hsl(var(--background))] flex items-center justify-center p-6">
    <div class="card max-w-md w-full p-6 text-center">
      {#if status === 'loading' || status === 'idle' || status === 'unauthorized'}
        <div class="skeleton h-8 w-44 mx-auto mb-3"></div>
        <p class="text-sm text-[hsl(var(--muted-foreground))]">Memverifikasi akses workspace...</p>
      {:else if status === 'forbidden'}
        <h1 class="text-lg font-semibold mb-2">Akses Ditolak</h1>
        <p class="text-sm text-[hsl(var(--muted-foreground))]">{errorMessage || 'Anda bukan anggota organisasi ini.'}</p>
      {:else if status === 'not-found'}
        <h1 class="text-lg font-semibold mb-2">Tenant Tidak Ditemukan</h1>
        <p class="text-sm text-[hsl(var(--muted-foreground))]">{errorMessage || 'Workspace tidak ditemukan.'}</p>
      {:else}
        <h1 class="text-lg font-semibold mb-2">Gagal Memuat Workspace</h1>
        <p class="text-sm text-[hsl(var(--muted-foreground))] mb-4">{errorMessage}</p>
        <button class="text-sm text-[hsl(var(--primary))] hover:underline" onclick={() => tenantSlug && loadTenant(tenantSlug)}>Coba lagi</button>
      {/if}
      </div>
    </div>
  {/if}

