<script lang="ts">
  import type { Snippet } from 'svelte';
  import { fade, scale } from 'svelte/transition';
  import { X } from '@lucide/svelte';
  import { cn } from '$lib/utils/cn';

  type Props = {
    open: boolean;
    onclose: () => void;
    title?: string;
    size?: 'sm' | 'md' | 'lg' | 'xl';
    children: Snippet;
  };

  let { open, onclose, title = '', size = 'md', children }: Props = $props();

  $effect(() => {
    if (open) {
      document.body.style.overflow = 'hidden';
    } else {
      document.body.style.overflow = '';
    }
    return () => { document.body.style.overflow = ''; };
  });

  function handleKeydown(e: KeyboardEvent) {
    if (e.key === 'Escape') onclose();
  }
</script>

<svelte:window onkeydown={handleKeydown} />

{#if open}
  <div
    class="fixed inset-0 z-50 flex items-center justify-center p-3 sm:p-4"
    role="dialog"
    aria-modal="true"
    tabindex="-1"
  >
    <div class="fixed inset-0 bg-black/50" transition:fade={{ duration: 150 }} onclick={onclose}></div>

    <div
      class={cn(
        'relative z-10 w-full bg-[hsl(var(--background))] border border-[hsl(var(--border))] shadow-lg max-h-[calc(100dvh-1.5rem)] sm:max-h-[85vh] overflow-x-hidden overflow-y-auto rounded-lg',
        size === 'sm' && 'max-w-sm',
        size === 'md' && 'max-w-lg',
        size === 'lg' && 'max-w-2xl',
        size === 'xl' && 'max-w-4xl',
      )}
      transition:scale={{ duration: 150, start: 0.95 }}
    >
      <button
        class="absolute top-3 right-3 p-1 rounded hover:bg-[hsl(var(--accent))] transition-colors z-20"
        onclick={onclose}
        aria-label="Tutup"
      >
        <X class="w-4 h-4" />
      </button>
      {#if title}
        <div class="px-5 py-3 border-b border-[hsl(var(--border))]">
          <h2 class="text-sm font-semibold">{title}</h2>
        </div>
      {/if}
      <div class="p-5">
        {@render children()}
      </div>
    </div>
  </div>
{/if}
