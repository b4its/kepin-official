<script lang="ts">
  import type { Snippet } from 'svelte';
  import { cn } from '$lib/utils/cn';
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
</script>

<div class="flex h-screen overflow-hidden bg-[hsl(var(--background))]">
  <div class="hidden lg:block w-64 shrink-0 border-r border-[hsl(var(--border))]">
    <AdminSidebarContent {currentPath} {onNavigate} />
  </div>

  {#if sidebarOpen}
    <Sidebar open={sidebarOpen} onclose={() => sidebarOpen = false} title="Menu Admin">
      <AdminSidebarContent {currentPath} {onNavigate} />
    </Sidebar>
  {/if}

  <div class="flex flex-col flex-1 min-w-0">
    <TopBar title="Platform Admin" {sidebarOpen} ontogglesidebar={() => sidebarOpen = !sidebarOpen} />
    <main class="flex-1 overflow-y-auto p-4 sm:p-6 lg:p-8">
      <div class="max-w-7xl mx-auto">
        {@render children()}
      </div>
    </main>
  </div>
</div>
