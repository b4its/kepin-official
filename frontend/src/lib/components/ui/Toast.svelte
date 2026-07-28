<script lang="ts">
  import { fade, slide } from 'svelte/transition';
  import { X, CheckCircle, AlertCircle, AlertTriangle, Info } from '@lucide/svelte';
  import { toasts, dismissToast, type ToastType } from '$lib/stores/toast';

  const icons: Record<ToastType, typeof CheckCircle> = {
    success: CheckCircle,
    error: AlertCircle,
    warning: AlertTriangle,
    info: Info,
  };

  const colors: Record<ToastType, string> = {
    success: 'bg-[hsl(152,76%,40%)] text-white',
    error: 'bg-[hsl(var(--destructive))] text-[hsl(var(--destructive-foreground))]',
    warning: 'bg-[hsl(var(--kepin-yellow))] text-black',
    info: 'bg-[hsl(var(--primary))] text-[hsl(var(--primary-foreground))]',
  };
</script>

{#each $toasts as toast (toast.id)}
  <div
    class="fixed right-4 z-[9999] pointer-events-auto"
    style="top: calc(1rem + {Math.max(0, $toasts.findIndex(t => t.id === toast.id)) * 3.5}rem)"
    transition:fade={{ duration: 200 }}
    role="alert"
  >
    <div
      class="{colors[toast.type]} flex items-center gap-3 px-4 py-3 rounded-lg shadow-lg min-w-[300px] max-w-[420px] border border-white/20"
      transition:slide={{ duration: 200 }}
    >
      {#if icons[toast.type]}
        <svelte:component this={icons[toast.type]} class="w-5 h-5 shrink-0" />
      {/if}
      <span class="text-sm font-medium flex-1">{toast.message}</span>
      <button
        class="shrink-0 p-0.5 rounded hover:bg-white/20 transition-colors"
        onclick={() => dismissToast(toast.id)}
        aria-label="Tutup"
      >
        <X class="w-4 h-4" />
      </button>
    </div>
  </div>
{/each}
