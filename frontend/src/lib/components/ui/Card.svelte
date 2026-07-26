<script lang="ts">
  import { cn } from '$lib/utils/cn';

  type Props = {
    class?: string;
    children?: import('svelte').Snippet;
  };

  let {
    class: className = '',
    children,
  }: Props = $props();
</script>

<div class={cn('rounded-lg border border-[hsl(var(--border))] bg-[hsl(var(--card))]', className)}>
  {#if children}
    {@render children()}
  {/if}
</div>
