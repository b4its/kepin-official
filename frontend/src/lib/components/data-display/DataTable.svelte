<script lang="ts" generics="T">
  import { cn } from '$lib/utils/cn';
  import type { Snippet } from 'svelte';
  import { ArrowUp, ArrowDown, ChevronLeft, ChevronRight, Search, X } from '@lucide/svelte';
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
    /** Hook unik untuk panduan tur (driver.js) — dipasang pada wrapper tabel. */
    tourHook?: string;
    rowLink?: (item: T) => string;
    rowActions?: Snippet<[item: T, index: number]>;
    searchable?: boolean;
    searchFields?: string[];
  };

  let {
    columns,
    data,
    loading = false,
    emptyMessage = 'Tidak ada data',
    page = 1,
    pageSize = 5,
    total = 0,
    onpagechange,
    onsort,
    sortKey = '',
    sortDir = 'asc',
    class: className = '',
    tourHook,
    rowLink,
    rowActions,
    searchable = false,
    searchFields,
  }: Props = $props();

  let searchTerm = $state('');
  let currentPage = $state(page);

  let filteredData = $derived(
    searchTerm
      ? data.filter(item => {
          const q = searchTerm.toLowerCase();
          const keys = searchFields ?? columns.map(c => c.key);
          return keys.some(key => {
            const val = item[key as keyof typeof item];
            return val != null && String(val).toLowerCase().includes(q);
          });
        })
      : data
  );

  let displayTotal = $derived(total > 0 ? total : (searchTerm ? filteredData.length : data.length));
  let displayTotalPages = $derived(Math.max(1, Math.ceil(displayTotal / pageSize)));

  let paginatedData = $derived(
    filteredData.slice((currentPage - 1) * pageSize, currentPage * pageSize)
  );

  $effect(() => {
    searchTerm;
    currentPage = 1;
  });

  $effect(() => {
    currentPage = page;
  });

  function goToPage(p: number) {
    currentPage = p;
    onpagechange?.(p);
  }
</script>

<div class={cn('rounded-lg border border-[hsl(var(--border))]', className)} data-tour={tourHook}>
  {#if searchable}
    <div class="flex items-center gap-2 px-3 py-2 border-b border-[hsl(var(--border))]">
      <Search class="w-4 h-4 shrink-0 text-[hsl(var(--muted-foreground))]" />
      <input
        type="search"
        bind:value={searchTerm}
        placeholder="Cari..."
        class="flex-1 bg-transparent border-none outline-none text-sm placeholder:text-[hsl(var(--muted-foreground))]"
      />
      {#if searchTerm}
        <button onclick={() => searchTerm = ''} class="shrink-0 text-[hsl(var(--muted-foreground))] hover:text-[hsl(var(--foreground))]">
          <X class="w-4 h-4" />
        </button>
      {/if}
    </div>
  {/if}
  <div class="overflow-x-auto">
  <table class="w-full min-w-[640px] caption-bottom text-sm">
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
        {#if rowActions}
          <th class="h-10 px-3 text-left align-middle font-medium text-[hsl(var(--muted-foreground))] whitespace-nowrap w-20"></th>
        {/if}
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
      {:else if filteredData.length === 0}
        <tr class="border-t border-[hsl(var(--border))]">
          <td colspan={columns.length + (rowActions ? 1 : 0)} class="h-32 text-center text-sm text-[hsl(var(--muted-foreground))]">
            {searchTerm ? 'Tidak ada hasil pencarian' : emptyMessage}
          </td>
        </tr>
      {:else}
        {#each paginatedData as item, i}
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
            {#if rowActions}
              <td class="p-3 text-right whitespace-nowrap">
                {@render rowActions(item, i)}
              </td>
            {/if}
          </tr>
        {/each}
      {/if}
    </tbody>
  </table>
  </div>
  {#if displayTotal > pageSize}
    <div class="flex flex-wrap items-center justify-between gap-2 px-3 py-2 border-t border-[hsl(var(--border))]">
      <p class="text-xs text-[hsl(var(--muted-foreground))]">
        {(currentPage - 1) * pageSize + 1}-{Math.min(currentPage * pageSize, displayTotal)} dari {displayTotal}
      </p>
      <div class="flex items-center gap-1">
        <Button
          variant="ghost"
          size="sm"
          disabled={currentPage <= 1}
          onclick={() => goToPage(currentPage - 1)}
        >
          <ChevronLeft class="w-4 h-4" />
        </Button>
        <span class="text-xs text-[hsl(var(--muted-foreground))] px-2">{currentPage}</span>
        <Button
          variant="ghost"
          size="sm"
          disabled={currentPage >= displayTotalPages}
          onclick={() => goToPage(currentPage + 1)}
        >
          <ChevronRight class="w-4 h-4" />
        </Button>
      </div>
    </div>
  {/if}
</div>
