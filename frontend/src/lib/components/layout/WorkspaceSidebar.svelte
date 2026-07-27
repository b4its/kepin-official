<script lang="ts">
  import { clientNavigation } from '$lib/config/navigation';
  import { sidebarSettings, isNavEnabled, currentRole } from '$lib/stores/data';
  import { cn } from '$lib/utils/cn';
  import { ChevronLeft, ChevronRight, ChevronDown, LayoutGrid } from '@lucide/svelte';
  import Logo from '$lib/components/ui/Logo.svelte';

  type Props = {
    currentPath: string;
    tenantName: string;
    tenantSlug: string;
    onNavigate: (href: string) => void;
    collapsed?: boolean;
    ontogglecollapsed?: () => void;
  };

  let { currentPath, tenantName, tenantSlug, onNavigate, collapsed = false, ontogglecollapsed }: Props = $props();

  let groupsExpanded = $state<Record<string, boolean>>(
    Object.fromEntries(clientNavigation.map(g => [g.key, true]))
  );

  function toggleGroup(key: string) {
    groupsExpanded = { ...groupsExpanded, [key]: !groupsExpanded[key] };
  }

  function isActive(href: string) {
    const relativePath = currentPath.replace(/^\/app\/[^/]+/, '') || '';
    return href === ''
      ? relativePath === '' || relativePath === '/'
      : relativePath === href || (href === '/notifications' && relativePath.startsWith('/notifications/'));
  }

  // Visible nav filtered by sidebar settings (pinned items always shown)
  const visibleNav = $derived(
    clientNavigation.map(group => ({
      ...group,
      items: group.items.filter(item =>
        item.pinned || isNavEnabled($sidebarSettings, item.key)
      ),
    })).filter(group => group.items.length > 0)
  );

  const isOwner = $derived($currentRole === 'tenant_owner');
</script>

<div class="flex flex-col h-full">
  <div class="p-4 flex-1 overflow-y-auto">
    <a href="/app/{tenantSlug}" class="flex items-center gap-2 mb-6">
      <Logo height={24} />
      {#if !collapsed}
        <div class="min-w-0">
          <span class="font-bold text-sm block truncate">{tenantName}</span>
          <span class="text-xs text-[hsl(var(--muted-foreground))]">Workspace</span>
        </div>
      {/if}
    </a>

    <div class="space-y-1">
      {#each visibleNav as group}
        {#if !collapsed}
          <button
            onclick={() => toggleGroup(group.key)}
            class="flex items-center justify-between w-full px-3 py-1.5 text-xs font-semibold text-[hsl(var(--muted-foreground))] uppercase tracking-wider hover:text-[hsl(var(--foreground))] transition-colors rounded"
          >
            <span>{group.label}</span>
            <ChevronDown
              class={"w-3.5 h-3.5 transition-transform duration-200 " + (groupsExpanded[group.key] ? 'rotate-180' : '')}
            />
          </button>
        {:else}
          <div class="h-4" />
        {/if}
        {#if groupsExpanded[group.key]}
          {#each group.items as item}
            <button
              onclick={() => onNavigate(item.href)}
              class={cn(
                'flex items-center gap-3 w-full px-3 py-2 text-sm rounded-md transition-colors',
                collapsed ? 'justify-center px-2' : '',
                isActive(item.href)
                  ? 'bg-[hsl(var(--primary))] text-[hsl(var(--primary-foreground))] font-semibold shadow-sm'
                  : 'text-[hsl(var(--muted-foreground))] hover:text-[hsl(var(--foreground))] hover:bg-[hsl(var(--accent))]'
              )}
              aria-current={isActive(item.href) ? 'page' : undefined}
              title={collapsed ? item.label : undefined}
            >
              <item.icon class="w-4 h-4 shrink-0" />
              {#if !collapsed}
                <span class="truncate">{item.label}</span>
                {#if item.badge}
                  <span class="ml-auto badge-info text-[10px]">{item.badge}</span>
                {/if}
              {/if}
            </button>
          {/each}
        {/if}
      {/each}

      <!-- Kustomisasi Sidebar — hanya owner -->
      {#if isOwner}
        <div class="mt-2">
          {#if !collapsed}
            <div class="px-3 py-1.5 text-xs font-semibold text-[hsl(var(--muted-foreground))] uppercase tracking-wider">
              Owner
            </div>
          {:else}
            <div class="h-4" />
          {/if}
          <button
            onclick={() => onNavigate('/settings/sidebar')}
            class={cn(
              'flex items-center gap-3 w-full px-3 py-2 text-sm rounded-md transition-colors',
              collapsed ? 'justify-center px-2' : '',
              isActive('/settings/sidebar')
                ? 'bg-[hsl(var(--primary))] text-[hsl(var(--primary-foreground))] font-semibold shadow-sm'
                : 'text-[hsl(var(--muted-foreground))] hover:text-[hsl(var(--foreground))] hover:bg-[hsl(var(--accent))]'
            )}
            aria-current={isActive('/settings/sidebar') ? 'page' : undefined}
            title={collapsed ? 'Kustomisasi Sidebar' : undefined}
          >
            <LayoutGrid class="w-4 h-4 shrink-0" />
            {#if !collapsed}
              <span class="truncate">Kustomisasi Sidebar</span>
            {/if}
          </button>
        </div>
      {/if}
    </div>
  </div>

  <div class="p-3 border-t border-[hsl(var(--border))]">
    <button
      onclick={ontogglecollapsed}
      class="flex items-center justify-center w-full py-1.5 text-xs text-[hsl(var(--muted-foreground))] hover:text-[hsl(var(--foreground))] transition-colors rounded-md hover:bg-[hsl(var(--accent))]"
      aria-label={collapsed ? 'Perluas sidebar' : 'Ciutkan sidebar'}
    >
      {#if collapsed}
        <ChevronRight class="w-4 h-4" />
      {:else}
        <ChevronLeft class="w-4 h-4" />
      {/if}
    </button>
  </div>
</div>
