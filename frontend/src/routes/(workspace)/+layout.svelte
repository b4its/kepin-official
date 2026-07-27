<script lang="ts">
  import { page } from '$app/stores';
  import WorkspaceShell from '$lib/components/layout/WorkspaceShell.svelte';

  let { children } = $props();
  let tenantName = $state('Toko Maju Jaya');
  const path = $derived($page.url.pathname);
  const tenantSlug = $derived($page.params.tenantSlug || 'toko-maju');

  function navigate(href: string) {
    window.location.href = `/app/${tenantSlug}${href}`;
  }
</script>

<WorkspaceShell currentPath={path} {tenantName} onNavigate={navigate}>
  {@render children()}
</WorkspaceShell>
