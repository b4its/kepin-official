<script lang="ts">
  import type { Snippet } from 'svelte';
  import { cn } from '$lib/utils/cn';

  type Props = {
    title: string;
    description?: string;
    breadcrumbs?: { label: string; href?: string }[];
    actions?: Snippet;
    class?: string;
  };

  let {
    title,
    description = '',
    breadcrumbs = [],
    actions,
    class: className = '',
  }: Props = $props();
</script>

<div class={cn('mb-6', className)}>
  {#if breadcrumbs.length > 0}
    <nav class="flex items-center gap-1 text-sm text-[hsl(var(--muted-foreground))] mb-2">
      {#each breadcrumbs as crumb, i}
        {#if i > 0}
          <span class="mx-1">/</span>
        {/if}
        {#if crumb.href}
          <a href={crumb.href} class="hover:text-[hsl(var(--foreground))] transition-colors">{crumb.label}</a>
        {:else}
          <span>{crumb.label}</span>
        {/if}
      {/each}
    </nav>
  {/if}
  <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
    <div>
      <h1 class="text-2xl sm:text-3xl font-bold text-[hsl(var(--foreground))]">{title}</h1>
      {#if description}
        <p class="mt-1 text-sm text-[hsl(var(--muted-foreground))]">{description}</p>
      {/if}
    </div>
    {#if actions}
      <div class="flex items-center gap-2 shrink-0">
        {@render actions()}
      </div>
    {/if}
  </div>
</div>
