<script lang="ts">
  import { cn } from '$lib/utils/cn';
  import { X } from '@lucide/svelte';

  type Props = {
    open: boolean;
    onclose: () => void;
    title?: string;
    children?: import('svelte').Snippet;
  };

  let {
    open,
    onclose,
    title = '',
    children,
  }: Props = $props();
</script>

{#if open}
  <!-- svelte-ignore a11y_no_static_element_interactions -->
  <div
    class="fixed inset-0 z-40 bg-black/50 lg:hidden"
    onclick={onclose}
    onkeydown={onclose}
  ></div>

  <aside
    class={cn(
      'fixed top-0 left-0 z-50 h-full w-64 bg-[hsl(var(--card))] border-r border-[hsl(var(--border))] transition-transform duration-200',
      'lg:translate-x-0 lg:static lg:z-0',
      open ? 'translate-x-0' : '-translate-x-full'
    )}
  >
    <div class="flex items-center justify-between p-4 border-b border-[hsl(var(--border))] lg:hidden">
      <span class="font-semibold">{title || 'Menu'}</span>
      <button onclick={onclose} class="p-1 rounded-md hover:bg-[hsl(var(--accent))]" aria-label="Tutup menu">
        <X class="w-5 h-5" />
      </button>
    </div>
    <div class="overflow-y-auto h-full pb-16 lg:pb-0">
      {#if children}
        {@render children()}
      {/if}
    </div>
  </aside>
{/if}
