<script lang="ts">
  import WorkspaceShell from '$lib/components/layout/WorkspaceShell.svelte';

  let { children } = $props();
  let path = $state('/app/toko-maju');
  let tenantName = $state('Toko Maju Jaya');

  function navigate(href: string) {
    const slug = 'toko-maju';
    path = `/app/${slug}${href}`;
    window.location.href = path;
  }
</script>

<WorkspaceShell currentPath={path} {tenantName} onNavigate={navigate}>
  {@render children()}
</WorkspaceShell>
