<script lang="ts">
  import { page } from '$app/stores';
  import PageHeader from '$lib/components/layout/PageHeader.svelte';
  import DataTable from '$lib/components/data-display/DataTable.svelte';
  import Button from '$lib/components/ui/Button.svelte';
  import Modal from '$lib/components/ui/Modal.svelte';
  import ExportModal from '$lib/components/ui/ExportModal.svelte';
  import { accounts, currentRole, journalEntries, loadJournals, tenantApi } from '$lib/stores/data';
  import { showToast } from '$lib/stores/toast';
  import { formatIDR } from '$lib/utils/currency';
  import { Download, Plus, RefreshCw } from '@lucide/svelte';

  type Line = { accountId: string; description: string; debit: string; credit: string };
  type LedgerLine = { journalEntryId: string; journalNumber: string; journalDate: string; status: string; reference: string; description: string; debit: string; credit: string; balance: string };
  type Ledger = { accountId: string; accountCode: string; accountName: string; accountType: string; normalBalance: string; opening: string; closing: string; items: LedgerLine[] };

  const slug = $derived($page.params.tenantSlug || '');
  const isOwner = $derived($currentRole === 'tenant_owner');
  let showExport = $state(false);
  let showModal = $state(false);
  let loading = $state(false);
  let saving = $state(false);
  let error = $state('');
  let accountFilter = $state('');
  let showLedger = $state(false);
  let ledger = $state<Ledger | null>(null);
  let ledgerLoading = $state(false);
  let ledgerPage = $state(1);
  const LEDGER_PAGE_SIZE = 25;
  const ledgerPageItems = $derived(ledger?.items.slice((ledgerPage - 1) * LEDGER_PAGE_SIZE, ledgerPage * LEDGER_PAGE_SIZE) ?? []);
  const ledgerTotalPages = $derived(ledger ? Math.max(1, Math.ceil(ledger.items.length / LEDGER_PAGE_SIZE)) : 1);
  let startDate = $state('');
  let endDate = $state('');
  let form = $state({ journalDate: '', reference: '', description: '', lines: [] as Line[] });

  const totalDebit = $derived(form.lines.reduce((sum, line) => sum + amount(line.debit), 0));
  const totalCredit = $derived(form.lines.reduce((sum, line) => sum + amount(line.credit), 0));
  const balanced = $derived(form.lines.length >= 2 && totalDebit > 0 && totalDebit === totalCredit);

  const exportColumns = [
    { key: 'date', label: 'Tanggal' },
    { key: 'reference', label: 'Nomor/Referensi' },
    { key: 'description', label: 'Deskripsi' },
    { key: 'status', label: 'Status' },
    { key: 'createdAt', label: 'Dibuat' },
  ];

  function amount(value: string) {
    const parsed = Number(value || 0);
    return Number.isFinite(parsed) ? parsed : 0;
  }

  function format(value: number) {
    return `Rp ${value.toLocaleString('id-ID')}`;
  }

  function openCreate() {
    const today = new Date().toISOString().slice(0, 10);
    form = {
      journalDate: today,
      reference: '',
      description: '',
      lines: [
        { accountId: '', description: '', debit: '', credit: '' },
        { accountId: '', description: '', debit: '', credit: '' },
      ],
    };
    showModal = true;
  }

  function addLine() {
    form.lines = [...form.lines, { accountId: '', description: '', debit: '', credit: '' }];
  }

  function removeLine(index: number) {
    if (form.lines.length <= 2) return;
    form.lines = form.lines.filter((_, current) => current !== index);
  }

  async function refresh() {
    if (!slug) return;
    loading = true;
    error = '';
    try {
      await loadJournals(slug, accountFilter ? `?accountId=${accountFilter}` : undefined);
    } catch (err: any) {
      error = err?.message || 'Gagal memuat jurnal';
    } finally {
      loading = false;
    }
  }

  async function loadLedger() {
    if (!slug || !accountFilter) return;
    ledgerLoading = true;
    error = '';
    try {
      const parts = [`?accountId=${accountFilter}`];
      if (startDate) parts.push(`startDate=${startDate}`);
      if (endDate) parts.push(`endDate=${endDate}`);
      ledger = await tenantApi.getLedger(slug, parts.join('&')) as Ledger;
      ledgerPage = 1;
    } catch (err: any) {
      ledger = null;
      error = err?.message || 'Gagal memuat buku besar';
    } finally {
      ledgerLoading = false;
    }
  }

  async function toggleLedger() {
    showLedger = !showLedger;
    if (showLedger) await loadLedger();
  }

  function setLedgerPage(p: number) {
    if (p < 1 || p > ledgerTotalPages) return;
    ledgerPage = p;
  }

  async function saveDraft() {
    if (!slug || !isOwner || !balanced) return;
    saving = true;
    try {
      await tenantApi.createJournal(slug, {
        ...form,
        lines: form.lines.map((line) => ({ ...line, debit: line.debit || '0', credit: line.credit || '0' })),
      });
      showModal = false;
      showToast('Jurnal draft berhasil dibuat', 'success');
      await refresh();
    } catch (err: any) {
      showToast(err?.message || 'Gagal membuat jurnal', 'error');
    } finally {
      saving = false;
    }
  }

  async function post(id: string) {
    if (!slug || !isOwner) return;
    try {
      await tenantApi.postJournal(slug, id);
      showToast('Jurnal berhasil diposting ke buku besar', 'success');
      await refresh();
    } catch (err: any) {
      showToast(err?.message || 'Gagal memposting jurnal', 'error');
    }
  }

  async function reverse(id: string) {
    if (!slug || !isOwner || !confirm('Reverse jurnal posted ini?')) return;
    try {
      await tenantApi.reverseJournal(slug, id);
      showToast('Jurnal reversal berhasil dibuat', 'success');
      await refresh();
    } catch (err: any) {
      showToast(err?.message || 'Gagal melakukan reversal jurnal', 'error');
    }
  }

  $effect(() => { if (slug) void refresh(); });
</script>

<PageHeader title="Jurnal" description="Draft, posting, dan reversal melalui Central Posting Engine" breadcrumbs={[{ label: 'Akuntansi' }, { label: 'Jurnal' }]}> 
  {#snippet actions()}
    <Button variant="secondary" onclick={() => showExport = true} disabled={Boolean(error) || loading}><Download class="w-4 h-4" /> Ekspor</Button>
    <Button variant="secondary" onclick={refresh} loading={loading}><RefreshCw class="w-4 h-4" /> Refresh</Button>
    {#if isOwner}<Button onclick={openCreate}><Plus class="w-4 h-4" /> Jurnal Baru</Button>{/if}
  {/snippet}
</PageHeader>

{#if error}<div class="mb-4 rounded-lg border border-red-200 bg-red-50 p-4 text-sm text-red-700">{error}</div>{/if}
{#if !isOwner}<div class="card p-4 mb-6 text-sm text-[hsl(var(--muted-foreground))]">Daftar jurnal bersifat read-only. Hanya owner dapat membuat, posting, atau reverse jurnal.</div>{/if}

<div class="card mb-4 flex flex-wrap items-center gap-3 p-4">
  <label class="flex items-center gap-2 text-sm text-[hsl(var(--muted-foreground))]">
    Buku besar per akun:
    <select bind:value={accountFilter} onchange={() => { showLedger = false; void refresh(); }} class="input-field" aria-label="Filter akun buku besar">
      <option value="">Semua akun</option>
      {#each $accounts.filter((account) => account.status === 'active') as account}
        <option value={account.id}>{account.code} · {account.name}</option>
      {/each}
    </select>
  </label>
  {#if accountFilter}
    <span class="text-xs text-[hsl(var(--muted-foreground))]">Hanya jurnal yang menyentuh akun terpilih</span>
    <button class="text-xs text-[hsl(var(--primary))] hover:underline" onclick={() => { accountFilter = ''; showLedger = false; void refresh(); }}>Reset</button>
    <label class="flex cursor-pointer items-center gap-2 text-sm font-medium">
      <input type="checkbox" checked={showLedger} onclick={toggleLedger} class="h-4 w-4" />
      Lihat buku besar (saldo berjalan)
    </label>
  {/if}
</div>

{#if showLedger && ledger}
  <div class="card mb-4 flex flex-wrap items-center justify-between gap-3 p-4">
    <div class="flex flex-wrap items-center gap-2 text-sm">
      <span>Periode:</span>
      <input type="date" bind:value={startDate} class="input-field w-40" aria-label="Tanggal mulai buku besar" />
      <span>s.d.</span>
      <input type="date" bind:value={endDate} class="input-field w-40" aria-label="Tanggal akhir buku besar" />
      <Button size="sm" variant="secondary" onclick={loadLedger} loading={ledgerLoading}>Terapkan</Button>
    </div>
    <p class="text-xs text-[hsl(var(--muted-foreground))]">
      Saldo awal {formatIDR(Number(ledger.opening))} · Saldo akhir {formatIDR(Number(ledger.closing))}
    </p>
  </div>
{/if}

{#if showLedger && ledger}
  <div class="card overflow-x-auto">
    <div class="flex items-center justify-between border-b border-[hsl(var(--border))] px-4 py-3">
      <h3 class="font-semibold">Buku Besar · {ledger.accountCode} {ledger.accountName}</h3>
      <span class="rounded-full bg-[hsl(var(--muted))] px-2 py-0.5 text-xs">{ledger.accountType} · normal {ledger.normalBalance}</span>
    </div>
    <table class="w-full text-sm">
      <thead>
        <tr class="border-b border-[hsl(var(--border))] text-left text-xs text-[hsl(var(--muted-foreground))]">
          <th class="px-4 py-2">Tanggal</th>
          <th class="px-4 py-2">No. Jurnal</th>
          <th class="px-4 py-2">Deskripsi</th>
          <th class="px-4 py-2 text-right">Debit</th>
          <th class="px-4 py-2 text-right">Kredit</th>
          <th class="px-4 py-2 text-right">Saldo</th>
        </tr>
      </thead>
      <tbody>
        <tr class="border-b border-[hsl(var(--border))]">
          <td class="px-4 py-2 text-xs text-[hsl(var(--muted-foreground))]" colspan="5">Saldo awal</td>
          <td class="px-4 py-2 text-right font-semibold tabular-nums">{formatIDR(Number(ledger.opening))}</td>
        </tr>
        {#each ledgerPageItems as line}
          <tr class="border-b border-[hsl(var(--border))]">
            <td class="px-4 py-2">{line.journalDate}</td>
            <td class="px-4 py-2 font-mono text-xs">{line.journalNumber}</td>
            <td class="px-4 py-2 text-[hsl(var(--muted-foreground))]">{line.description || line.reference || '-'}</td>
            <td class="px-4 py-2 text-right tabular-nums">{Number(line.debit) !== 0 ? formatIDR(Number(line.debit)) : ''}</td>
            <td class="px-4 py-2 text-right tabular-nums">{Number(line.credit) !== 0 ? formatIDR(Number(line.credit)) : ''}</td>
            <td class="px-4 py-2 text-right font-medium tabular-nums">{formatIDR(Number(line.balance))}</td>
          </tr>
        {/each}
        <tr>
          <td class="px-4 py-2 font-semibold" colspan="5">Saldo akhir</td>
          <td class="px-4 py-2 text-right font-semibold tabular-nums">{formatIDR(Number(ledger.closing))}</td>
        </tr>
      </tbody>
    </table>
    {#if ledgerTotalPages > 1}
      <div class="flex items-center justify-between border-t border-[hsl(var(--border))] px-4 py-2 text-xs text-[hsl(var(--muted-foreground))]">
        <span>Menampilkan {ledgerPageItems.length} dari {ledger.items.length} baris</span>
        <div class="flex items-center gap-1">
          <button
            class="px-2 py-1 rounded border border-border hover:bg-accent disabled:opacity-40 disabled:pointer-events-none"
            disabled={ledgerPage <= 1}
            onclick={() => setLedgerPage(ledgerPage - 1)}
          >Sebelumnya</button>
          <span class="px-2 tabular-nums">Halaman {ledgerPage} / {ledgerTotalPages}</span>
          <button
            class="px-2 py-1 rounded border border-border hover:bg-accent disabled:opacity-40 disabled:pointer-events-none"
            disabled={ledgerPage >= ledgerTotalPages}
            onclick={() => setLedgerPage(ledgerPage + 1)}
          >Berikutnya</button>
        </div>
      </div>
    {/if}
  </div>
{:else}
<DataTable
  columns={[
    { key: 'date', label: 'Tanggal', sortable: true },
    { key: 'reference', label: 'Nomor/Referensi' },
    { key: 'description', label: 'Deskripsi' },
    { key: 'status', label: 'Status', render: (item: any) => `<span class="badge-${item.status}">${item.status}</span>` },
    { key: 'createdAt', label: 'Dibuat' },
  ]}
  data={$journalEntries}
  total={$journalEntries.length}
  pageSize={10}
  loading={loading}
  searchable={true}
>
  {#snippet rowActions(item: any)}
    {#if isOwner && item.status === 'draft'}<button class="text-xs text-[hsl(var(--primary))] hover:underline" onclick={() => post(item.id)}>Post</button>{/if}
    {#if isOwner && item.status === 'posted'}<button class="ml-2 text-xs text-[var(--color-kepin-danger)] hover:underline" onclick={() => reverse(item.id)}>Reverse</button>{/if}
  {/snippet}
</DataTable>
{/if}

<Modal title="Jurnal Baru" open={showModal} onclose={() => showModal = false}>
  <form onsubmit={saveDraft} class="space-y-4">
    <div class="grid sm:grid-cols-2 gap-4"><div><label class="label-text" for="journal-date">Tanggal</label><input id="journal-date" type="date" bind:value={form.journalDate} class="input-field mt-1" required /></div><div><label class="label-text" for="journal-reference">Referensi</label><input id="journal-reference" bind:value={form.reference} class="input-field mt-1" /></div></div>
    <div><label class="label-text" for="journal-description">Deskripsi</label><input id="journal-description" bind:value={form.description} class="input-field mt-1" required /></div>
    <div class="space-y-2"><div class="flex items-center justify-between"><h3 class="text-sm font-semibold">Baris Jurnal</h3><Button size="sm" variant="secondary" type="button" onclick={addLine}>+ Baris</Button></div>{#each form.lines as line, index}<div class="grid grid-cols-12 gap-2 rounded border border-[hsl(var(--border))] p-2"><select class="input-field col-span-5" bind:value={line.accountId} required><option value="">Pilih akun</option>{#each $accounts.filter((account) => account.status === 'active') as account}<option value={account.id}>{account.code} · {account.name}</option>{/each}</select><input class="input-field col-span-3" bind:value={line.description} placeholder="Deskripsi" /><input class="input-field col-span-2" type="number" min="0" step="0.01" bind:value={line.debit} placeholder="Debit" /><input class="input-field col-span-2" type="number" min="0" step="0.01" bind:value={line.credit} placeholder="Kredit" />{#if form.lines.length > 2}<button type="button" class="col-span-12 text-right text-xs text-[var(--color-kepin-danger)]" onclick={() => removeLine(index)}>Hapus baris</button>{/if}</div>{/each}</div>
    <div class="rounded bg-[hsl(var(--muted))] p-3 text-sm flex justify-between"><span>Debit {format(totalDebit)} · Kredit {format(totalCredit)}</span><span class={balanced ? 'text-[var(--color-kepin-green)]' : 'text-[var(--color-kepin-danger)]'}>{balanced ? 'Balanced' : 'Belum balanced'}</span></div>
    <div class="flex justify-end gap-2"><Button variant="secondary" type="button" onclick={() => showModal = false}>Batal</Button><Button type="submit" loading={saving} disabled={!balanced}>Simpan Draft</Button></div>
  </form>
</Modal>

<ExportModal open={showExport} onclose={() => showExport = false} title="Jurnal Akuntansi" subtitle="Daftar entri jurnal dari backend" columns={exportColumns} rows={$journalEntries} filename="jurnal" />
