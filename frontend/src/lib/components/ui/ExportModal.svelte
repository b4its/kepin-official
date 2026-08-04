<script lang="ts">
  import { fade, scale } from 'svelte/transition';
  import { X, FileText, Sheet, Download } from '@lucide/svelte';
  import Button from '$lib/components/ui/Button.svelte';
  import type { ExportColumn, ExportOptions, ExportSheet } from '$lib/utils/export';
  import { downloadPdf, downloadExcel } from '$lib/utils/export';

  type Props = {
    open: boolean;
    onclose: () => void;
    title: string;
    subtitle?: string;
    columns: ExportColumn[];
    rows: any[];
    filename?: string;
    sheets?: ExportSheet[];
  };

  let { open, onclose, title, subtitle, columns, rows, filename, sheets }: Props = $props();

  let pdfLoading = $state(false);
  let xlsxLoading = $state(false);

  function cellValue(col: ExportColumn, row: any): string {
    if (col.render) return col.render(row).replace(/<[^>]*>/g, '');
    const v = row[col.key as keyof typeof row];
    return v == null ? '' : String(v);
  }

  async function handlePdf() {
    pdfLoading = true;
    try {
      await downloadPdf({ title, subtitle, columns, rows, filename });
    } finally {
      pdfLoading = false;
    }
  }

  async function handleExcel() {
    xlsxLoading = true;
    try {
      await downloadExcel({ title, subtitle, columns, rows, filename, sheets });
    } finally {
      xlsxLoading = false;
    }
  }

  $effect(() => {
    if (open) {
      document.body.style.overflow = 'hidden';
    } else {
      document.body.style.overflow = '';
    }
    return () => { document.body.style.overflow = ''; };
  });

  function onkey(e: KeyboardEvent) {
    if (e.key === 'Escape') onclose();
  }
</script>

<svelte:window onkeydown={onkey} />

{#if open}
  <!-- backdrop -->
  <div
    class="fixed inset-0 z-50 flex items-start justify-center p-4 pt-10 overflow-y-auto"
    role="dialog"
    aria-modal="true"
  >
    <div
      class="fixed inset-0 bg-black/50"
      transition:fade={{ duration: 150 }}
      onclick={onclose}
    ></div>

    <!-- panel -->
    <div
      class="relative z-10 w-full max-w-5xl bg-[hsl(var(--background))] border border-[hsl(var(--border))] shadow-xl rounded-xl flex flex-col max-h-[90vh]"
      transition:scale={{ duration: 150, start: 0.97 }}
    >
      <!-- header -->
      <div class="flex items-center justify-between px-6 py-4 border-b border-[hsl(var(--border))] shrink-0">
        <div>
          <h2 class="text-base font-semibold">{title}</h2>
          {#if subtitle}
            <p class="text-xs text-[hsl(var(--muted-foreground))] mt-0.5">{subtitle}</p>
          {/if}
        </div>
        <button
          onclick={onclose}
          class="p-1.5 rounded-md hover:bg-[hsl(var(--accent))] transition-colors"
          aria-label="Tutup"
        >
          <X class="w-4 h-4" />
        </button>
      </div>

      <!-- preview table -->
      <div class="flex-1 overflow-auto px-6 py-4 min-h-0">
        <!-- meta -->
        <p class="text-xs text-[hsl(var(--muted-foreground))] mb-3">
          Preview — {rows.length} baris · dicetak {new Date().toLocaleString('id-ID', { dateStyle: 'medium', timeStyle: 'short' })}
        </p>

        <div class="overflow-x-auto rounded-lg border border-[hsl(var(--border))]">
          <table class="w-full text-sm border-collapse">
            <thead>
              <tr class="bg-[hsl(var(--primary)/0.08)]">
                <th class="px-3 py-2.5 text-left text-xs font-semibold text-[hsl(var(--muted-foreground))] border-b border-[hsl(var(--border))] whitespace-nowrap w-8">#</th>
                {#each columns as col}
                  <th class="px-3 py-2.5 text-left text-xs font-semibold text-[hsl(var(--muted-foreground))] border-b border-[hsl(var(--border))] whitespace-nowrap">
                    {col.label}
                  </th>
                {/each}
              </tr>
            </thead>
            <tbody>
              {#each rows as row, ri}
                <tr class="border-b border-[hsl(var(--border))] last:border-0 hover:bg-[hsl(var(--accent)/0.5)] transition-colors">
                  <td class="px-3 py-2 text-xs text-[hsl(var(--muted-foreground))]">{ri + 1}</td>
                  {#each columns as col}
                    <td class="px-3 py-2 text-xs text-[hsl(var(--foreground))] whitespace-nowrap">
                      {cellValue(col, row)}
                    </td>
                  {/each}
                </tr>
              {:else}
                <tr>
                  <td colspan={columns.length + 1} class="px-4 py-6 text-center text-xs text-[hsl(var(--muted-foreground))]">
                    Tidak ada data untuk diekspor
                  </td>
                </tr>
              {/each}
            </tbody>
          </table>
        </div>
      </div>

      <!-- footer actions -->
      <div class="flex items-center justify-between gap-3 px-6 py-4 border-t border-[hsl(var(--border))] shrink-0 bg-[hsl(var(--muted)/0.3)]">
        <span class="text-xs text-[hsl(var(--muted-foreground))]">
          Pilih format untuk mengunduh
        </span>
        <div class="flex items-center gap-2">
          <Button variant="secondary" onclick={onclose} size="sm">Batal</Button>
          <Button
            variant="secondary"
            size="sm"
            onclick={handleExcel}
            loading={xlsxLoading}
            disabled={rows.length === 0}
          >
            <Sheet class="w-4 h-4 text-green-600" />
            Excel (.xlsx)
          </Button>
          <Button
            size="sm"
            onclick={handlePdf}
            loading={pdfLoading}
            disabled={rows.length === 0}
          >
            <FileText class="w-4 h-4" />
            PDF (.pdf)
          </Button>
        </div>
      </div>
    </div>
  </div>
{/if}
