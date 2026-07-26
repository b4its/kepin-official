<script lang="ts" generics="T">
  import { cn } from '$lib/utils/cn';
  import { ArrowUp, ArrowDown, ChevronLeft, ChevronRight } from '@lucide/svelte';
  import Button from '$lib/components/ui/Button.svelte';

  type Column = {
    key: string;
    label: string;
    sortable?: boolean;
    render?: (item: T) => string;
    class?: string;
    align?: 'left' | 'right';
  };

  type Props = {
    columns: Column[];
    data: T[];
    loading?: boolean;
    emptyMessage?: string;
    page?: number;
    pageSize?: number;
    total?: number;
    onpagechange?: (page: number) => void;
    onsort?: (key: string) => void;
    sortKey?: string;
    sortDir?: 'asc' | 'desc';
    class?: string;
    rowLink?: (item: T) => string;
  };

  let {
    columns,
    data,
    loading = false,
    emptyMessage = 'Tidak ada data',
    page = 1,
    pageSize = 10,
    total = 0,
    onpagechange,
    onsort,
    sortKey = '',
    sortDir = 'asc',
    class: className = '',
    rowLink,
  }: Props = $props();

  let totalPages = $derived(Math.max(1, Math.ceil(total / pageSize)));
</script>

<div class={cn('overflow-x-auto rounded-lg border border-[hsl(var(--border))]', className)}>
  <table class="w-full caption-bottom text-sm">
    <thead class="bg-[hsl(var(--muted))]">
      <tr>
        {#each columns as col}
          <th
            class={cn(
              'h-10 px-3 text-left align-middle font-medium text-[hsl(var(--muted-foreground))] whitespace-nowrap',
              col.align === 'right' ? 'text-right' : 'text-left',
              col.class
            )}
          >
            {#if col.sortable}
              <button
                class="inline-flex items-center gap-1 hover:text-[hsl(var(--foreground))]"
                onclick={() => onsort?.(col.key)}
              >
                {col.label}
                {#if sortKey === col.key}
                  {#if sortDir === 'asc'}
                    <ArrowUp class="w-3 h-3" />
                  {:else}
                    <ArrowDown class="w-3 h-3" />
                  {/if}
                {/if}
              </button>
            {:else}
              {col.label}
            {/if}
          </th>
        {/each}
      </tr>
    </thead>
    <tbody>
      {#if loading}
        {#each Array(5) as _, i}
          <tr class="border-t border-[hsl(var(--border))]">
            {#each columns as col}
              <td class="p-3">
                <div class="skeleton h-4" style="width: {60 + Math.random() * 30}%"></div>
              </td>
            {/each}
          </tr>
        {/each}
      {:else if data.length === 0}
        <tr class="border-t border-[hsl(var(--border))]">
          <td colspan={columns.length} class="h-32 text-center text-sm text-[hsl(var(--muted-foreground))]">
            {emptyMessage}
          </td>
        </tr>
      {:else}
        {#each data as item, i}
          <tr
            class={cn(
              'border-t border-[hsl(var(--border))] transition-colors',
              rowLink ? 'cursor-pointer hover:bg-[hsl(var(--muted))]' : ''
            )}
            onclick={rowLink ? () => window.location.href = rowLink(item) : undefined}
          >
            {#each columns as col}
              <td
                class={cn(
                  'p-3 align-middle',
                  col.align === 'right' ? 'text-right tabular-nums' : 'text-left',
                  col.class
                )}
              >
                {#if col.render}
                {@html col.render(item)}
              {:else}
                {String(item[col.key as keyof typeof item] ?? '-')}
              {/if}
              </td>
            {/each}
          </tr>
        {/each}
      {/if}
    </tbody>
  </table>
  {#if total > pageSize}
    <div class="flex items-center justify-between px-3 py-2 border-t border-[hsl(var(--border))]">
      <p class="text-xs text-[hsl(var(--muted-foreground))]">
        {(page - 1) * pageSize + 1}-{Math.min(page * pageSize, total)} dari {total}
      </p>
      <div class="flex items-center gap-1">
        <Button
          variant="ghost"
          size="sm"
          disabled={page <= 1}
          onclick={() => onpagechange?.(page - 1)}
        >
          <ChevronLeft class="w-4 h-4" />
        </Button>
        <span class="text-xs text-[hsl(var(--muted-foreground))] px-2">{page}</span>
        <Button
          variant="ghost"
          size="sm"
          disabled={page >= totalPages}
          onclick={() => onpagechange?.(page + 1)}
        >
          <ChevronRight class="w-4 h-4" />
        </Button>
      </div>
    </div>
  {/if}
</div>
