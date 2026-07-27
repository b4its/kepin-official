<script lang="ts">
  import { page } from '$app/stores';
  import WorkspaceShell from '$lib/components/layout/WorkspaceShell.svelte';
  import {
    setSlug,
    loadSidebarSettings,
    setCurrentRole,
    currentRole,
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

    // Load sidebar settings for the tenant
    loadSidebarSettings(tenantSlug);
  });

  function navigate(href: string) {
    window.location.href = `/app/${tenantSlug}${href}`;
  }
</script>

<WorkspaceShell currentPath={path} {tenantName} {tenantSlug} onNavigate={navigate}>
  {@render children()}
</WorkspaceShell>
