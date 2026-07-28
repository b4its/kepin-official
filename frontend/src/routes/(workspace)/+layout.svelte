<script lang="ts">
  import { page } from '$app/stores';
  import WorkspaceShell from '$lib/components/layout/WorkspaceShell.svelte';
  import {
    setSlug,
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
    setCurrentRole,
  } from '$lib/stores/data';
  import { api } from '$lib/api/client';
  import { onMount } from 'svelte';

  let { children } = $props();

  const path = $derived($page.url.pathname);
  const tenantSlug = $derived($page.params.tenantSlug || '');

  let tenantName = $state('');

  // Load context + sidebar settings when the slug changes
  $effect(() => {
    if (!tenantSlug) return;
    setSlug(tenantSlug);

    // Load tenant context: name + user role
    api(`/tenants/${tenantSlug}/context`)
      .then((ctx: any) => {
        tenantName = ctx?.tenant?.name || tenantSlug;
        const role = ctx?.role as 'tenant_owner' | 'employee' | null;
        setCurrentRole(role ?? null);
      })
      .catch(() => {
        tenantName = tenantSlug;
        setCurrentRole(null);
      });

    // Load all data stores for this tenant
    loadSidebarSettings(tenantSlug);
    loadCustomers(tenantSlug);
    loadSuppliers(tenantSlug);
    loadProducts(tenantSlug);
    loadPurchaseOrders(tenantSlug);
    loadTransactions(tenantSlug);
    loadAccounts(tenantSlug);
    loadInvoices(tenantSlug);
    loadBranches(tenantSlug);
    loadMembers(tenantSlug);
    loadNotifications(tenantSlug);
    loadStockMovements(tenantSlug);
  });

  function navigate(href: string) {
    window.location.href = `/app/${tenantSlug}${href}`;
  }
</script>

<WorkspaceShell currentPath={path} {tenantName} {tenantSlug} onNavigate={navigate}>
  {@render children()}
</WorkspaceShell>
