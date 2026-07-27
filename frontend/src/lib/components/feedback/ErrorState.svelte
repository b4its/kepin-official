<script lang="ts">
  import { cn } from '$lib/utils/cn';
  import { AlertTriangle } from '@lucide/svelte';
  import Button from '$lib/components/ui/Button.svelte';

  type Props = {
    title?: string;
    description?: string;
    retry?: () => void;
    requestId?: string;
    class?: string;
  };

  let {
    title = 'Terjadi kesalahan',
    description = 'Silakan coba lagi. Jika masalah berlanjut, hubungi tim dukungan.',
    retry,
    requestId,
    class: className = '',
  }: Props = $props();
</script>

<div class={cn('flex flex-col items-center justify-center py-12 px-4 text-center', className)}>
  <AlertTriangle class="w-12 h-12 text-[var(--color-kepin-danger)] mb-4" />
  <h3 class="text-base font-medium text-[hsl(var(--foreground))]">{title}</h3>
  <p class="mt-1 text-sm text-[hsl(var(--muted-foreground))] max-w-sm">{description}</p>
  {#if requestId}
    <p class="mt-2 text-xs text-[hsl(var(--muted-foreground))]">ID: {requestId}</p>
  {/if}
  {#if retry}
    <div class="mt-4">
      <Button variant="primary" onclick={retry}>
        Coba Lagi
      </Button>
    </div>
  {/if}
</div>
