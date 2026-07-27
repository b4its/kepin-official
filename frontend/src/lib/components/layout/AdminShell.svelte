<script lang="ts">
  import type { Snippet } from 'svelte';
  import Sidebar from '$lib/components/layout/Sidebar.svelte';
  import AdminSidebarContent from '$lib/components/layout/AdminSidebar.svelte';
  import TopBar from '$lib/components/layout/TopBar.svelte';

  type Props = {
    currentPath: string;
    onNavigate: (href: string) => void;
    children: Snippet;
  };

  let {
    currentPath,
    onNavigate,
    children,
  }: Props = $props();

  let sidebarOpen = $state(false);
  let sidebarCollapsed = $state(false);

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
  >
    <AdminSidebarContent
      {currentPath}
      {onNavigate}
      collapsed={sidebarCollapsed}
      ontogglecollapsed={() => sidebarCollapsed = !sidebarCollapsed}
    />
  </div>

  {#if sidebarOpen}
    <Sidebar open={sidebarOpen} onclose={() => sidebarOpen = false} title="Menu Admin">
      <AdminSidebarContent {currentPath} {onNavigate} />
    </Sidebar>
  {/if}

  <div class="flex flex-col flex-1 min-w-0">
    <TopBar title="Platform Admin" {sidebarOpen} ontogglesidebar={handleToggleSidebar} />
    <main class="flex-1 min-w-0 overflow-x-hidden overflow-y-auto p-3 sm:p-6 lg:p-8">
      <div class="w-full max-w-7xl mx-auto">
        {@render children()}
      </div>
    </main>
  </div>
</div>
