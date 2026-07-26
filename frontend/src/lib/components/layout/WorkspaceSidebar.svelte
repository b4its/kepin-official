<script lang="ts">
  import { clientNavigation } from '$lib/config/navigation';
  import { cn } from '$lib/utils/cn';

  type Props = {
    currentPath: string;
    tenantName: string;
    onNavigate: (href: string) => void;
  };

  let { currentPath, tenantName, onNavigate }: Props = $props();
</script>

<div class="p-4">
  <a href="/app/toko-maju" class="flex items-center gap-2 mb-6">
    <div class="w-7 h-7 bg-[var(--color-kepin-red)] flex items-center justify-center rounded">
      <span class="text-white font-bold text-xs">K</span>
    </div>
    <div class="min-w-0">
      <span class="font-bold text-sm block truncate">{tenantName}</span>
      <span class="text-xs text-[hsl(var(--muted-foreground))]">Workspace</span>
    </div>
  </a>

  <div class="space-y-1">
    {#each clientNavigation as group}
      <p class="px-3 py-1 text-xs font-semibold text-[hsl(var(--muted-foreground))] uppercase tracking-wider">
        {group.label}
      </p>
      {#each group.items as item}
        <button
          onclick={() => onNavigate(item.href)}
          class={cn(
            'flex items-center gap-3 w-full px-3 py-2 text-sm rounded-md transition-colors',
            currentPath === item.href
              ? 'bg-[hsl(var(--primary))] text-[hsl(var(--primary-foreground))]'
              : 'text-[hsl(var(--muted-foreground))] hover:text-[hsl(var(--foreground))] hover:bg-[hsl(var(--accent))]'
          )}
        >
          <item.icon class="w-4 h-4 shrink-0" />
          {item.label}
          {#if item.badge}
            <span class="ml-auto badge-info text-[10px]">{item.badge}</span>
          {/if}
        </button>
      {/each}
    {/each}
  </div>
</div>
