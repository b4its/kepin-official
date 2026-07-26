<script lang="ts">
  import { cn } from '$lib/utils/cn';
  import { Inbox } from '@lucide/svelte';
  import Button from '$lib/components/ui/Button.svelte';

  type Props = {
    title?: string;
    description?: string;
    action?: { label: string; onclick: () => void };
    icon?: any;
    class?: string;
  };

  let {
    title = 'Belum ada data',
    description = '',
    action,
    icon: Icon = Inbox,
    class: className = '',
  }: Props = $props();
</script>

<div class={cn('flex flex-col items-center justify-center py-12 px-4 text-center', className)}>
  <Icon class="w-12 h-12 text-[hsl(var(--muted-foreground))] mb-4" />
  <h3 class="text-base font-medium text-[hsl(var(--foreground))]">{title}</h3>
  {#if description}
    <p class="mt-1 text-sm text-[hsl(var(--muted-foreground))] max-w-sm">{description}</p>
  {/if}
  {#if action}
    <div class="mt-4">
      <Button variant="primary" onclick={action.onclick}>
        {action.label}
      </Button>
    </div>
  {/if}
</div>
