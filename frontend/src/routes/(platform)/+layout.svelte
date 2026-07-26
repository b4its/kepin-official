<script lang="ts">
  import AdminShell from '$lib/components/layout/AdminShell.svelte';

  let { children } = $props();
  let path = $state('/admin');

  function navigate(href: string) {
    path = href;
    window.location.href = href;
  }
</script>

<AdminShell currentPath={path} onNavigate={navigate}>
  {@render children()}
</AdminShell>
