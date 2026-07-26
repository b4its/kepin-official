<script lang="ts">
  import type { Snippet } from 'svelte';
  import { Building2 } from '@lucide/svelte';
  import Sidebar from '$lib/components/layout/Sidebar.svelte';
  import WorkspaceSidebarContent from '$lib/components/layout/WorkspaceSidebar.svelte';
  import TopBar from '$lib/components/layout/TopBar.svelte';

  type Props = {
    currentPath: string;
    tenantName: string;
    onNavigate: (href: string) => void;
    children: Snippet;
    topBarChildren?: Snippet;
  };

  let {
    currentPath,
    tenantName = 'Workspace',
    onNavigate,
    children,
    topBarChildren,
  }: Props = $props();

  let sidebarOpen = $state(false);
  let branchOpen = $state(false);
</script>

<div class="flex h-screen overflow-hidden bg-[hsl(var(--background))]">
  <div class="hidden lg:block w-64 shrink-0 border-r border-[hsl(var(--border))]">
    <WorkspaceSidebarContent {currentPath} {tenantName} {onNavigate} />
  </div>

  {#if sidebarOpen}
    <Sidebar open={sidebarOpen} onclose={() => sidebarOpen = false} title={tenantName}>
      <WorkspaceSidebarContent {currentPath} {tenantName} {onNavigate} />
    </Sidebar>
  {/if}

  <div class="flex flex-col flex-1 min-w-0">
    <TopBar title={tenantName} {sidebarOpen} ontogglesidebar={() => sidebarOpen = !sidebarOpen}>
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

    <main class="flex-1 overflow-y-auto p-4 sm:p-6 lg:p-8">
      <div class="max-w-7xl mx-auto">
        {@render children()}
      </div>
    </main>
  </div>
</div>
