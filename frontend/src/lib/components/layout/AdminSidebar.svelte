<script lang="ts">
  import { adminNavigation } from '$lib/config/navigation';
  import { cn } from '$lib/utils/cn';
  import { ChevronLeft, ChevronRight } from '@lucide/svelte';
  import Logo from '$lib/components/ui/Logo.svelte';

  type Props = {
    currentPath: string;
    onNavigate: (href: string) => void;
    collapsed?: boolean;
    ontogglecollapsed?: () => void;
  };

  let { currentPath, onNavigate, collapsed = false, ontogglecollapsed }: Props = $props();

  function isActive(href: string) {
    return currentPath === href;
  }
</script>

<div class="flex flex-col h-full">
  <div class="p-4 flex-1 overflow-y-auto">
    <a href="/admin" class="flex items-center gap-2 mb-6">
      <Logo height={24} />
      {#if !collapsed}
        <span class="font-bold text-sm">KePin Admin</span>
      {/if}
    </a>

    <div class="space-y-1">
      {#each adminNavigation as group}
        {#if !collapsed}
          <p class="px-3 py-1 text-xs font-semibold text-[hsl(var(--muted-foreground))] uppercase tracking-wider">
            {group.label}
          </p>
        {/if}
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
              {item.label}
            {/if}
          </button>
        {/each}
      {/each}
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
