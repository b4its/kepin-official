<script lang="ts">
  import { page } from '$app/stores';
  import AdminShell from '$lib/components/layout/AdminShell.svelte';

  let { children } = $props();
  const path = $derived($page.url.pathname);

  function navigate(href: string) {
    window.location.href = href;
  }
</script>

<AdminShell currentPath={path} onNavigate={navigate}>
  {@render children()}
</AdminShell>
