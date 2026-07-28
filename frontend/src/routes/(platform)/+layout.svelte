<script lang="ts">
  import { page } from '$app/stores';
  import AdminShell from '$lib/components/layout/AdminShell.svelte';
  import { loadAdminTenants, loadPlatformAudit, loadAdminUsers, loadSubscriberNotifs } from '$lib/stores/data';
  import { onMount } from 'svelte';

  let { children } = $props();
  const path = $derived($page.url.pathname);

  onMount(() => {
    loadAdminTenants();
    loadPlatformAudit();
    loadAdminUsers();
    loadSubscriberNotifs();
  });

  function navigate(href: string) {
    window.location.href = href;
  }
</script>

<AdminShell currentPath={path} onNavigate={navigate}>
  {@render children()}
</AdminShell>
