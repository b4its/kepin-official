<script lang="ts">
  import { FileText, Sheet } from '@lucide/svelte';
  import Button from '$lib/components/ui/Button.svelte';
  import Modal from '$lib/components/ui/Modal.svelte';
  import { getCustomerStatement, getSupplierStatement } from '$lib/api/tenants';
  import { page } from '$app/stores';
  import { showToast } from '$lib/stores/toast';
  import { formatIDR } from '$lib/utils/currency';
  import { downloadExcel, downloadPdf, type ExportColumn } from '$lib/utils/export';

  type StatementLine = {
    date: string;
    reference: string;
    description: string;
    debit: number;
    credit: number;
    balance: number;
  };

  type StatementDoc = {
    opening: number;
    closing: number;
    items: StatementLine[];
  };

  let {
    kind = 'customer',
    entityId,
    entityCode = '',
    entityName,
    open,
    onclose,
  }: {
    kind?: 'customer' | 'supplier';
    entityId: string;
    entityCode?: string;
    entityName: string;
    open: boolean;
    onclose: () => void;
  } = $props();

  const slug = $derived($page.params.tenantSlug ?? '');
  const label = $derived(kind === 'customer' ? 'piutang' : 'hutang');
  const title = $derived(
    `Kartu ${kind === 'customer' ? 'Piutang' : 'Hutang'} · ${entityCode ? `${entityCode} ` : ''}${entityName}`,
  );

  let statement = $state<StatementDoc | null>(null);
  let loading = $state(false);
  let start = $state('');
  let end = $state('');

  async function load() {
    if (!entityId) return;
    loading = true;
    try {
      const params = [];
      if (start) params.push(`&startDate=${start}`);
      if (end) params.push(`&endDate=${end}`);
      statement = (kind === 'customer'
        ? await getCustomerStatement(slug, entityId, params.join(''))
        : await getSupplierStatement(slug, entityId, params.join(''))) as StatementDoc;
    } catch {
      statement = null;
      showToast(`Gagal memuat kartu ${label}`, 'error');
    } finally {
      loading = false;
    }
  }

  let wasOpen = false;
  $effect(() => {
    if (open && !wasOpen) {
      statement = null;
      start = '';
      end = '';
      void load();
    }
    wasOpen = open;
  });

  const exportColumns: ExportColumn[] = [
    { key: 'date', label: 'Tanggal' },
    { key: 'reference', label: 'No. Referensi' },
    { key: 'description', label: 'Deskripsi' },
    { key: 'debit', label: 'Debit', render: (r) => formatIDR(Number(r.debit)) },
    { key: 'credit', label: 'Kredit', render: (r) => formatIDR(Number(r.credit)) },
    { key: 'balance', label: 'Saldo', render: (r) => formatIDR(Number(r.balance)) },
  ];

  const exportFilename = $derived(
    `${kind === 'customer' ? 'kartu-piutang' : 'kartu-hutang'}-${entityCode || entityName}`
      .toLowerCase()
      .replace(/[^a-z0-9-_]+/g, '-'),
  );

  async function exportPdf() {
    if (!statement) return;
    await downloadPdf({
      title,
      subtitle: `Saldo awal ${formatIDR(Number(statement.opening))} · Saldo akhir ${formatIDR(Number(statement.closing))}`,
      columns: exportColumns,
      rows: statement.items,
      filename: exportFilename,
    });
  }

  async function exportExcel() {
    if (!statement) return;
    await downloadExcel({
      title,
      columns: exportColumns,
      rows: statement.items,
      filename: exportFilename,
    });
  }
</script>

<Modal title={title} open={open} onclose={onclose}>
  <div class="space-y-4">
    <div class="flex flex-wrap items-center gap-2 text-sm">
      <span>Periode:</span>
      <input type="date" bind:value={start} class="input-field w-40" aria-label={`Tanggal mulai kartu ${label}`} />
      <span>s.d.</span>
      <input type="date" bind:value={end} class="input-field w-40" aria-label={`Tanggal akhir kartu ${label}`} />
      <Button size="sm" variant="secondary" onclick={load} loading={loading}>Terapkan</Button>
      {#if statement}
        <div class="ml-auto flex items-center gap-2">
          <Button size="sm" variant="secondary" onclick={exportPdf}><FileText class="w-4 h-4" /> PDF</Button>
          <Button size="sm" variant="secondary" onclick={exportExcel}><Sheet class="w-4 h-4" /> Excel</Button>
        </div>
      {/if}
    </div>
    {#if statement}
      <p class="text-xs text-[hsl(var(--muted-foreground))]">
        Saldo awal {formatIDR(Number(statement.opening))} · Saldo akhir {formatIDR(Number(statement.closing))}
      </p>
      <div class="max-h-96 overflow-auto rounded border border-[hsl(var(--border))]">
        <table class="w-full text-sm">
          <thead class="sticky top-0 bg-[hsl(var(--card))]">
            <tr class="border-b border-[hsl(var(--border))] text-left text-xs text-[hsl(var(--muted-foreground))]">
              <th class="px-4 py-2">Tanggal</th>
              <th class="px-4 py-2">No. Referensi</th>
              <th class="px-4 py-2">Deskripsi</th>
              <th class="px-4 py-2 text-right">Debit</th>
              <th class="px-4 py-2 text-right">Kredit</th>
              <th class="px-4 py-2 text-right">Saldo</th>
            </tr>
          </thead>
          <tbody>
            <tr class="border-b border-[hsl(var(--border))]">
              <td class="px-4 py-2 text-xs text-[hsl(var(--muted-foreground))]" colspan="5">Saldo awal</td>
              <td class="px-4 py-2 text-right font-semibold tabular-nums">{formatIDR(Number(statement.opening))}</td>
            </tr>
            {#if statement.items.length === 0}
              <tr class="border-b border-[hsl(var(--border))]">
                <td class="px-4 py-2 text-xs text-[hsl(var(--muted-foreground))]" colspan="6">Tidak ada mutasi pada periode ini</td>
              </tr>
            {/if}
            {#each statement.items as line}
              <tr class="border-b border-[hsl(var(--border))]">
                <td class="px-4 py-2">{line.date}</td>
                <td class="px-4 py-2 font-mono text-xs">{line.reference}</td>
                <td class="px-4 py-2 text-[hsl(var(--muted-foreground))]">{line.description}</td>
                <td class="px-4 py-2 text-right tabular-nums">{Number(line.debit) !== 0 ? formatIDR(Number(line.debit)) : ''}</td>
                <td class="px-4 py-2 text-right tabular-nums">{Number(line.credit) !== 0 ? formatIDR(Number(line.credit)) : ''}</td>
                <td class="px-4 py-2 text-right font-medium tabular-nums">{formatIDR(Number(line.balance))}</td>
              </tr>
            {/each}
            <tr>
              <td class="px-4 py-2 font-semibold" colspan="5">Saldo akhir</td>
              <td class="px-4 py-2 text-right font-semibold tabular-nums">{formatIDR(Number(statement.closing))}</td>
            </tr>
          </tbody>
        </table>
      </div>
    {:else if loading}
      <p class="text-sm text-[hsl(var(--muted-foreground))]">Memuat kartu {label}…</p>
    {/if}
  </div>
</Modal>
