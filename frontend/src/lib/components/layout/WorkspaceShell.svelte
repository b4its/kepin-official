<script lang="ts">
  import type { Snippet } from 'svelte';
  import Sidebar from '$lib/components/layout/Sidebar.svelte';
  import WorkspaceSidebarContent from '$lib/components/layout/WorkspaceSidebar.svelte';
  import TopBar from '$lib/components/layout/TopBar.svelte';

  type Props = {
    currentPath: string;
    tenantName: string;
    tenantSlug: string;
    onNavigate: (href: string) => void;
    children: Snippet;
    topBarChildren?: Snippet;
  };

  let {
    currentPath,
    tenantName = 'Workspace',
    tenantSlug,
    onNavigate,
    children,
    topBarChildren,
  }: Props = $props();

  let sidebarOpen = $state(false);
  let sidebarCollapsed = $state(false);
  let branchOpen = $state(false);

  function handleToggleSidebar() {
    if (typeof window !== 'undefined' && window.innerWidth >= 1024) {
      sidebarCollapsed = !sidebarCollapsed;
    } else {
      sidebarOpen = !sidebarOpen;
    }
  }
</script>

<div class="flex h-screen overflow-hidden bg-[hsl(var(--background))]">
  <div
    class="hidden lg:block shrink-0 border-r border-[hsl(var(--border))] transition-all duration-200"
    class:w-16={sidebarCollapsed}
    class:w-64={!sidebarCollapsed}
    data-tour="workspace-sidebar"
  >
    <WorkspaceSidebarContent
      {currentPath}
      {tenantName}
      {tenantSlug}
      {onNavigate}
      collapsed={sidebarCollapsed}
      ontogglecollapsed={() => sidebarCollapsed = !sidebarCollapsed}
    />
  </div>

  {#if sidebarOpen}
    <Sidebar open={sidebarOpen} onclose={() => sidebarOpen = false} title={tenantName}>
      <WorkspaceSidebarContent {currentPath} {tenantName} {tenantSlug} {onNavigate} />
    </Sidebar>
  {/if}

  <div class="flex flex-col flex-1 min-w-0">
    <TopBar title={tenantName} sidebarOpen={sidebarOpen} ontogglesidebar={handleToggleSidebar}>
      {#if topBarChildren}
        {@render topBarChildren()}
      {/if}
    </TopBar>

    {#if branchOpen}
      <div class="bg-[var(--color-kepin-yellow)] px-4 py-1 text-xs text-[var(--color-ink)] text-center">
        Cabang: Toko Pusat
        <button class="underline ml-2" onclick={() => branchOpen = false}>Ganti</button>
      </div>
    {/if}

    <main class="flex-1 min-w-0 overflow-x-hidden overflow-y-auto p-3 sm:p-6 lg:p-8">
      <div class="w-full max-w-7xl mx-auto">
        {@render children()}
      </div>
    </main>
  </div>
</div>
