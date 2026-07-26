<script lang="ts">
  import { cn } from '$lib/utils/cn';

  type Props = {
    variant?: 'success' | 'info' | 'warning' | 'danger' | 'neutral';
    class?: string;
    children?: import('svelte').Snippet;
  };

  let {
    variant = 'neutral',
    class: className = '',
    children,
  }: Props = $props();

  const variants: Record<string, string> = {
    success: 'bg-[var(--color-kepin-green)] text-white',
    info: 'bg-[hsl(var(--primary))] text-white',
    warning: 'bg-[var(--color-kepin-yellow)] text-[var(--color-ink)]',
    danger: 'bg-[var(--color-kepin-red)] text-white',
    neutral: 'bg-[hsl(var(--muted))] text-[hsl(var(--muted-foreground))]',
  };
</script>

<span class={cn('inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium', variants[variant], className)}>
  {#if children}
    {@render children()}
  {/if}
</span>
