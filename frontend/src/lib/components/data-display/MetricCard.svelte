<script lang="ts">
  import { cn } from '$lib/utils/cn';
  import { formatIDR, formatPercent } from '$lib/utils/currency';
  import { TrendingUp, TrendingDown, Minus } from '@lucide/svelte';
  import Button from '$lib/components/ui/Button.svelte';

  type Props = {
    label: string;
    value: number | null | undefined;
    previousValue?: number | null | undefined;
    unit?: string;
    loading?: boolean;
    href?: string;
    class?: string;
    format?: 'currency' | 'number' | 'percent';
  };

  let {
    label,
    value,
    previousValue,
    unit = '',
    loading = false,
    href = '',
    class: className = '',
    format = 'currency',
  }: Props = $props();

  let displayValue: string = $derived.by(() => {
    if (value === null || value === undefined) return '-';
    switch (format) {
      case 'currency': return formatIDR(value);
      case 'number': return new Intl.NumberFormat('id-ID').format(value);
      case 'percent': return formatPercent(value);
      default: return String(value);
    }
  });

  let change: number | null = $derived(
    previousValue === null || previousValue === undefined || previousValue === 0
      ? null
      : ((value ?? 0) - previousValue) / previousValue * 100
  );

  let isPositive: boolean | null = $derived(change === null ? null : change >= 0);
</script>

<div class={cn('card p-4 sm:p-5', loading && 'opacity-60', className)}>
  {#if loading}
    <div class="space-y-2">
      <div class="skeleton h-4 w-24"></div>
      <div class="skeleton h-8 w-32"></div>
      <div class="skeleton h-3 w-20"></div>
    </div>
  {:else}
    <div class="flex items-center justify-between mb-1">
      <p class="text-sm text-[hsl(var(--muted-foreground))]">{label}</p>
      {#if href}
        <Button variant="ghost" size="sm" {href}>
          Detail
        </Button>
      {/if}
    </div>
    <p class="text-2xl sm:text-3xl font-bold tabular-nums tracking-tight text-[hsl(var(--foreground))]">
      {displayValue}{unit}
    </p>
    {#if change !== null}
      <div class="flex items-center gap-1 mt-1">
        {#if isPositive}
          <TrendingUp class="w-3 h-3 text-[var(--color-kepin-green)]" />
          <span class="text-xs text-[var(--color-kepin-green)]">
            +{change.toFixed(1)}%
          </span>
        {:else if isPositive === false}
          <TrendingDown class="w-3 h-3 text-[var(--color-kepin-red)]" />
          <span class="text-xs text-[var(--color-kepin-red)]">
            {change.toFixed(1)}%
          </span>
        {:else}
          <Minus class="w-3 h-3 text-[hsl(var(--muted-foreground))]" />
          <span class="text-xs text-[hsl(var(--muted-foreground))]">0%</span>
        {/if}
      </div>
    {/if}
  {/if}
</div>
