<script lang="ts">
  import { cn } from '$lib/utils/cn';
  import { formatIDR, formatIDRCompact } from '$lib/utils/currency';

  type Props = {
    value: number | null | undefined;
    compact?: boolean;
    class?: string;
    privacy?: boolean;
  };

  let {
    value,
    compact = false,
    class: className = '',
    privacy = false,
  }: Props = $props();

  let displayValue: string = $derived(
    value === null || value === undefined
      ? '-'
      : compact
        ? formatIDRCompact(value)
        : formatIDR(value)
  );
</script>

<span
  class={cn(
    'tabular-nums',
    value === null || value === undefined ? 'text-[hsl(var(--muted-foreground))]' : '',
    className
  )}
  {...(privacy ? { 'data-privacy': 'masked' } : {})}
>
  {privacy ? '***' : displayValue}
</span>
